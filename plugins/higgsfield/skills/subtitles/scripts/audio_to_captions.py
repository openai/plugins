#!/usr/bin/env python3
"""Build timed captions using authored text and Whisper's word clock.

Whisper supplies timing only when a script manifest is available. Caption text
is aligned back to the exact ``vo_line``/``phrase`` values, preventing
transcription substitutions from being burned into generated videos.
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


NORMALIZE_PATTERN = re.compile(r"[^\w]+", re.UNICODE)
TOKEN_PATTERN = re.compile(r"[^\W_]+(?:[-'’][^\W_]+)*[.,!?;:]?", re.UNICODE)
NONVERBAL_DIRECTION_PATTERN = re.compile(r"\[[^\]]+\]")


def _normalize(value: str) -> str:
    return NORMALIZE_PATTERN.sub("", value.casefold())


def _load_authored_tokens(script_path: Path) -> list[str]:
    payload = json.loads(script_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("script manifest must be an object")

    rows = payload.get("beats")
    fields = ("phrase", "vo_line")
    if not isinstance(rows, list):
        rows = payload.get("blocks")
        fields = ("vo_line",)
    if not isinstance(rows, list) or not rows:
        raise ValueError("script manifest must contain blocks or beats")

    tokens: list[str] = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"script row {index} must be an object")
        text = next(
            (
                row[field].strip()
                for field in fields
                if isinstance(row.get(field), str) and row[field].strip()
            ),
            "",
        )
        if not text:
            raise ValueError(f"script row {index} has no authored narration")
        spoken_text = NONVERBAL_DIRECTION_PATTERN.sub("", text)
        tokens.extend(TOKEN_PATTERN.findall(spoken_text))
    if not tokens:
        raise ValueError("script manifest contains no authored narration words")
    return tokens


def _timed_script_span(
    script_tokens: list[str],
    *,
    start: float,
    end: float,
) -> list[dict[str, Any]]:
    if not script_tokens:
        return []
    duration = max(end - start, 0.05 * len(script_tokens))
    weights = [max(len(_normalize(token)), 1) for token in script_tokens]
    total_weight = sum(weights)
    timed: list[dict[str, Any]] = []
    cursor = start
    for index, (token, weight) in enumerate(zip(script_tokens, weights, strict=True)):
        token_end = (
            end
            if index == len(script_tokens) - 1
            else cursor + duration * weight / total_weight
        )
        timed.append(
            {
                "word": token,
                "start": round(cursor, 3),
                "end": round(max(token_end, cursor + 0.01), 3),
            }
        )
        cursor = token_end
    return timed


def align_words_to_script(
    words: list[dict[str, Any]],
    script_tokens: list[str],
    *,
    minimum_similarity: float = 0.55,
) -> tuple[list[dict[str, Any]], float]:
    """Return exact script tokens carrying timings derived from Whisper words."""
    whisper_tokens = [_normalize(str(word["word"])) for word in words]
    normalized_script_tokens = [_normalize(token) for token in script_tokens]
    matcher = difflib.SequenceMatcher(
        a=whisper_tokens,
        b=normalized_script_tokens,
        autojunk=False,
    )
    similarity = matcher.ratio()
    if similarity < minimum_similarity:
        raise ValueError(
            f"Whisper/script similarity {similarity:.3f} is below "
            f"{minimum_similarity:.3f}; refusing to burn unverified captions"
        )

    aligned: list[dict[str, Any]] = []
    for tag, whisper_start, whisper_end, script_start, script_end in matcher.get_opcodes():
        authored_span = script_tokens[script_start:script_end]
        if not authored_span:
            continue

        if tag == "equal":
            for offset, token in enumerate(authored_span):
                timed_word = words[whisper_start + offset]
                aligned.append(
                    {
                        "word": token,
                        "start": float(timed_word["start"]),
                        "end": float(timed_word["end"]),
                    }
                )
            continue

        if whisper_end > whisper_start:
            span_start = float(words[whisper_start]["start"])
            span_end = float(words[whisper_end - 1]["end"])
        else:
            previous_end = (
                float(words[whisper_start - 1]["end"])
                if whisper_start > 0
                else 0.0
            )
            next_start = (
                float(words[whisper_start]["start"])
                if whisper_start < len(words)
                else previous_end + 0.05 * len(authored_span)
            )
            span_start = previous_end
            span_end = max(next_start, previous_end + 0.05 * len(authored_span))
        aligned.extend(
            _timed_script_span(
                authored_span,
                start=span_start,
                end=span_end,
            )
        )

    if [_normalize(str(word["word"])) for word in aligned] != normalized_script_tokens:
        raise ValueError("caption alignment did not preserve the complete authored script")
    return aligned, similarity


def group_captions(
    words: list[dict[str, Any]],
    *,
    max_words: int = 3,
    max_gap: float = 0.5,
    max_chars: int = 15,
) -> list[dict[str, Any]]:
    captions: list[dict[str, Any]] = []
    current: list[dict[str, Any]] = []

    def _flush() -> None:
        if not current:
            return
        text = " ".join(str(word["word"]).strip() for word in current).strip()
        text = re.sub(r"\s+([,.!?;:])", r"\1", text)
        captions.append(
            {
                "text": text,
                "start": round(float(current[0]["start"]), 2),
                "end": round(float(current[-1]["end"]), 2),
            }
        )
        current.clear()

    for word in words:
        if current:
            gap = float(word["start"]) - float(current[-1]["end"])
            projected_text = " ".join(
                [*(str(item["word"]) for item in current), str(word["word"])]
            )
            if (
                gap >= max_gap
                or len(current) >= max_words
                or len(projected_text) > max_chars
            ):
                _flush()
        current.append(word)
        if re.search(r"[.!?]$", str(word["word"]).strip()):
            _flush()
    _flush()
    return captions


def _timestamp(seconds: float) -> str:
    total_milliseconds = int(round(seconds * 1000))
    hours, remaining_milliseconds = divmod(total_milliseconds, 3_600_000)
    minutes, remaining_milliseconds = divmod(remaining_milliseconds, 60_000)
    whole_seconds, milliseconds = divmod(remaining_milliseconds, 1000)
    return (
        f"{hours:02d}:{minutes:02d}:{whole_seconds:02d},"
        f"{milliseconds:03d}"
    )


def to_srt(captions: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"{index}\n{_timestamp(caption['start'])} --> "
        f"{_timestamp(caption['end'])}\n{caption['text']}\n"
        for index, caption in enumerate(captions, start=1)
    )


def _words_openai(path: Path) -> list[dict[str, Any]] | None:
    key = os.getenv("VOICE_TOOLS_OPENAI_KEY") or os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    from openai import OpenAI

    base_url = os.getenv("STT_OPENAI_BASE_URL", "https://api.openai.com/v1")
    client = OpenAI(
        api_key=key,
        base_url=base_url,
        timeout=120,
        max_retries=0,
    )
    with path.open("rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json",
            timestamp_granularities=["word"],
        )
    payload = (
        transcript.model_dump()
        if hasattr(transcript, "model_dump")
        else json.loads(transcript.json())
    )
    return [
        {
            "word": str(word["word"]).strip(),
            "start": float(word["start"]),
            "end": float(word["end"]),
        }
        for word in (payload.get("words") or [])
    ]


def _words_faster(path: Path, model_size: str) -> list[dict[str, Any]]:
    from faster_whisper import WhisperModel

    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, _info = model.transcribe(str(path), word_timestamps=True)
    words: list[dict[str, Any]] = []
    for segment in segments:
        for word in segment.words or []:
            words.append(
                {
                    "word": str(word.word).strip(),
                    "start": float(word.start),
                    "end": float(word.end),
                }
            )
    return words


def get_words(path: Path, model_size: str) -> tuple[list[dict[str, Any]], str]:
    try:
        words = _words_openai(path)
        if words:
            return words, "openai"
    except Exception as error:  # noqa: BLE001
        print(
            f"(openai path unavailable: {error}; using faster-whisper)",
            file=sys.stderr,
        )
    return _words_faster(path, model_size), "faster-whisper"


def _resolve_script_path(explicit_path: Path | None) -> Path | None:
    if explicit_path is not None:
        return explicit_path
    default_path = Path("script_manifest.json")
    return default_path if default_path.is_file() else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", type=Path)
    parser.add_argument("--json", type=Path)
    parser.add_argument("--srt", type=Path)
    parser.add_argument(
        "--script",
        type=Path,
        help=(
            "Authored script manifest. Defaults to ./script_manifest.json "
            "when present."
        ),
    )
    parser.add_argument("--max-words", type=int, default=3)
    parser.add_argument("--max-chars", type=int, default=15)
    parser.add_argument("--max-gap", type=float, default=0.4)
    parser.add_argument("--model", default="base")
    parser.add_argument("--minimum-similarity", type=float, default=0.55)
    arguments = parser.parse_args()

    words, provider = get_words(arguments.audio, arguments.model)
    script_path = _resolve_script_path(arguments.script)
    similarity: float | None = None
    if script_path is not None:
        try:
            script_tokens = _load_authored_tokens(script_path)
            words, similarity = align_words_to_script(
                words,
                script_tokens,
                minimum_similarity=arguments.minimum_similarity,
            )
        except (OSError, json.JSONDecodeError, ValueError) as error:
            print(f"ERROR: authored caption alignment failed: {error}", file=sys.stderr)
            return 1

    captions = group_captions(
        words,
        max_words=arguments.max_words,
        max_gap=arguments.max_gap,
        max_chars=arguments.max_chars,
    )
    print(
        f"provider={provider} words={len(words)} captions={len(captions)} "
        f"script_aligned={script_path is not None} similarity={similarity}",
        file=sys.stderr,
    )

    output = {
        "captions": captions,
        "script_aligned": script_path is not None,
        "similarity": similarity,
    }
    serialized_output = json.dumps(output, indent=2, ensure_ascii=False)
    print(serialized_output)
    if arguments.json is not None:
        arguments.json.write_text(serialized_output, encoding="utf-8")
    if arguments.srt is not None:
        arguments.srt.write_text(to_srt(captions), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
