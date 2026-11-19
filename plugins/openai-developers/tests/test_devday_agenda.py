import copy
import importlib.util
import unittest
from datetime import date
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "skills/devday-guide/scripts/render_agenda.py"
SPEC = importlib.util.spec_from_file_location("devday_agenda", SCRIPT)
AGENDA = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AGENDA)


class AgendaTest(unittest.TestCase):
    def setUp(self):
        # Synthetic fixture, not a published event schedule.
        self.data = {
            "date": "2026-01-10", "timezone": "America/Los_Angeles",
            "checked_on": "2026-01-01", "location": "Example venue",
            "source_url": "https://devday.openai.com/",
            "events": [
                {"id": "program", "title": "Example program", "start": "2026-01-10T11:15:00-08:00", "end": "2026-01-10T15:30:00-08:00"},
                {"id": "meal", "title": "Example meal", "start": "2026-01-10T11:30:00-08:00", "end": None},
            ],
        }

    def test_overlapping_program_and_unknown_end_are_preserved(self):
        rendered = AGENDA.render(self.data)
        self.assertIn('data-end=""', rendered)
        self.assertIn('11:15 am</span><span class="time-end"> – 3:30 pm', rendered)
        self.assertIn("11:30 am", rendered)
        self.assertNotIn("12:30", rendered)

    def test_untrusted_text_is_escaped_and_not_substituted_twice(self):
        self.data["events"][0]["title"] = '<script>alert(1)</script> @@ROWS@@'
        rendered = AGENDA.render(self.data)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt; @@ROWS@@", rendered)
        self.assertNotIn("<script>alert(1)", rendered)

    def test_rejects_private_and_script_links(self):
        for url in ["https://openai.enterprise.slack.com/", "javascript:alert(1)", "https://devday.openai.com.evil.example/", "https://devday.openai.com/?ticket=private", "https://user:secret@devday.openai.com/"]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                self.data["source_url"] = url
                AGENDA.render(self.data)

    def test_rejects_naive_dates_and_wrong_local_day(self):
        for start in ["2026-01-10T11:15:00", "2026-01-10T00:15:00+09:00"]:
            with self.subTest(start=start), self.assertRaises(ValueError):
                self.data["events"][0]["start"] = start
                AGENDA.render(self.data)

    def test_rejects_invalid_end_duplicate_id_and_selection(self):
        for field, value in [("end", "2026-01-10T10:00:00-08:00"), ("id", "meal"), ("selected", "false")]:
            data = copy.deepcopy(self.data)
            data["events"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                AGENDA.render(data)

    def test_archive_changes_after_event_in_local_timezone(self):
        self.assertIn("Your day at DevDay", AGENDA.render(self.data, today=date(2026, 1, 10)))
        self.assertIn("Past event · published agenda", AGENDA.render(self.data, today=date(2026, 1, 11)))

    def test_no_network_or_unnecessary_resources(self):
        rendered = AGENDA.render(self.data)
        self.assertIn("default-src 'none'", rendered)
        for forbidden in ["<iframe", "<img", "fetch(", "XMLHttpRequest", "localStorage", "https://fonts", "<script src="]:
            self.assertNotIn(forbidden, rendered)


if __name__ == "__main__":
    unittest.main()
