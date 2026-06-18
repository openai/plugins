"""SQLite schema history for the Codex Security workbench."""

import argparse

MIGRATIONS = (
    (
        1,
        "initial workbench schema",
        """
        CREATE TABLE workspaces (
            id TEXT PRIMARY KEY,
            target_path TEXT,
            target_title TEXT,
            target_summary TEXT,
            default_scope TEXT NOT NULL DEFAULT '.',
            default_mode TEXT NOT NULL DEFAULT 'standard'
                CHECK (default_mode IN ('diff', 'standard', 'deep')),
            user_context TEXT,
            diff_target_kind TEXT
                CHECK (diff_target_kind IN ('working_tree', 'commit', 'range')),
            diff_base_revision TEXT,
            diff_head_revision TEXT,
            diff_content_digest TEXT,
            diff_resolution_id TEXT,
            submitted INTEGER NOT NULL DEFAULT 0 CHECK (submitted IN (0, 1)),
            active_scan_id TEXT REFERENCES scans(id) ON DELETE SET NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE scans (
            id TEXT PRIMARY KEY,
            workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
            target_path TEXT NOT NULL,
            target_revision TEXT NOT NULL,
            target_snapshot_digest TEXT,
            scope TEXT NOT NULL,
            mode TEXT NOT NULL CHECK (mode IN ('diff', 'standard', 'deep')),
            user_context TEXT,
            diff_target_kind TEXT
                CHECK (diff_target_kind IN ('working_tree', 'commit', 'range')),
            diff_base_revision TEXT,
            diff_head_revision TEXT,
            diff_content_digest TEXT,
            scan_dir TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL CHECK (status IN ('running', 'complete', 'failed')),
            phase TEXT NOT NULL CHECK (
                phase IN ('preflight', 'threat_model', 'discovery', 'validation', 'attack_path', 'reporting')
            ),
            handoff_status TEXT NOT NULL DEFAULT 'pending'
                CHECK (handoff_status IN ('pending', 'delivered')),
            failure_message TEXT,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE scan_progress (
            scan_id TEXT PRIMARY KEY REFERENCES scans(id) ON DELETE CASCADE,
            review_items_total INTEGER NOT NULL DEFAULT 0 CHECK (review_items_total >= 0),
            review_items_completed INTEGER NOT NULL DEFAULT 0
                CHECK (review_items_completed >= 0 AND review_items_completed <= review_items_total),
            reportable_findings_count INTEGER NOT NULL DEFAULT 0
                CHECK (reportable_findings_count >= 0),
            deep_review_pass INTEGER CHECK (deep_review_pass IS NULL OR deep_review_pass >= 1),
            updated_at TEXT NOT NULL
        );

        CREATE TABLE scan_artifacts (
            scan_id TEXT NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
            kind TEXT NOT NULL CHECK (
                kind IN ('coverage', 'findings', 'manifest', 'markdownReport')
            ),
            path TEXT NOT NULL,
            created_at TEXT NOT NULL,
            PRIMARY KEY (scan_id, kind)
        );

        CREATE TABLE findings (
            id TEXT PRIMARY KEY,
            fingerprint TEXT NOT NULL UNIQUE,
            rule_id TEXT NOT NULL,
            identity_anchor TEXT NOT NULL,
            identity_instance TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE finding_occurrences (
            id TEXT PRIMARY KEY,
            finding_id TEXT NOT NULL REFERENCES findings(id),
            scan_id TEXT NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            summary TEXT NOT NULL,
            severity TEXT NOT NULL,
            confidence TEXT NOT NULL,
            remediation TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE (scan_id, finding_id)
        );

        CREATE TABLE finding_locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            occurrence_id TEXT NOT NULL REFERENCES finding_occurrences(id) ON DELETE CASCADE,
            relative_path TEXT NOT NULL,
            start_line INTEGER NOT NULL CHECK (start_line >= 1),
            end_line INTEGER NOT NULL CHECK (end_line >= start_line),
            role TEXT,
            sort_order INTEGER NOT NULL CHECK (sort_order >= 0),
            UNIQUE (occurrence_id, sort_order)
        );

        CREATE UNIQUE INDEX scans_one_running_per_workspace
        ON scans(workspace_id)
        WHERE status = 'running';
        """,
    ),
    (
        2,
        "persist capability preflight summaries",
        """
        ALTER TABLE workspaces ADD COLUMN capability_preflight_json TEXT;
        """,
    ),
    (
        3,
        "finding management schema",
        """
        CREATE TABLE finding_triage (
            occurrence_id TEXT PRIMARY KEY REFERENCES finding_occurrences(id) ON DELETE CASCADE,
            status TEXT NOT NULL CHECK (status IN ('open', 'closed')),
            close_reason TEXT CHECK (
                close_reason IS NULL OR close_reason IN ('already_fixed', 'wont_fix', 'false_positive')
            ),
            note TEXT,
            updated_at TEXT NOT NULL,
            CHECK (
                (status = 'open' AND close_reason IS NULL)
                OR (status = 'closed' AND close_reason IS NOT NULL)
            )
        );

        CREATE TABLE finding_remediation_attempts (
            request_id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL REFERENCES finding_occurrences(id) ON DELETE CASCADE,
            state TEXT NOT NULL CHECK (
                state IN ('idle', 'requested', 'generated', 'applied', 'verifying', 'verified', 'failed', 'superseded')
            ),
            version INTEGER NOT NULL CHECK (version >= 1),
            base_revision TEXT NOT NULL,
            base_content_digest TEXT,
            applied_content_digest TEXT,
            pending_action TEXT CHECK (
                pending_action IS NULL OR pending_action IN ('generate', 'apply', 'verify')
            ),
            patch_path TEXT,
            patch_digest TEXT,
            summary TEXT,
            verification_summary TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE INDEX finding_remediation_attempts_by_occurrence
        ON finding_remediation_attempts(occurrence_id, created_at DESC);

        ALTER TABLE finding_occurrences
        ADD COLUMN details_json TEXT NOT NULL DEFAULT '{}';

        """,
    ),
    (
        4,
        "scan handoff delivery claims",
        """
        ALTER TABLE scans
        ADD COLUMN handoff_claimed_at TEXT;

        ALTER TABLE scans
        ADD COLUMN handoff_claim_token TEXT;
        """,
    ),
    (
        5,
        "finding remediation action claims",
        """
        ALTER TABLE finding_remediation_attempts
        ADD COLUMN pending_action_claimed_at TEXT;

        ALTER TABLE finding_remediation_attempts
        ADD COLUMN pending_action_claim_token TEXT;
        """,
    ),
    (
        6,
        "thread-scoped workspaces",
        """
        ALTER TABLE workspaces
        ADD COLUMN thread_id TEXT;

        CREATE INDEX workspaces_by_thread_and_updated_at
        ON workspaces(thread_id, updated_at DESC);
        """,
    ),
    (
        7,
        "remediation host delivery state",
        """
        ALTER TABLE finding_remediation_attempts
        ADD COLUMN pending_action_delivered_at TEXT;
        """,
    ),
    (
        8,
        "sealed manifest digests",
        """
        ALTER TABLE scans
        ADD COLUMN seal_manifest_digest TEXT;
        """,
    ),
    (
        9,
        "scan target filesystem identity",
        """
        ALTER TABLE scans
        ADD COLUMN target_device INTEGER;

        ALTER TABLE scans
        ADD COLUMN target_inode INTEGER;
        """,
    ),
    (
        10,
        "scan cancellation state",
        """
        ALTER TABLE scans
        ADD COLUMN canceled_at TEXT;
        """,
    ),
)


def main() -> None:
    argparse.ArgumentParser(description=__doc__).parse_args()


if __name__ == "__main__":
    main()
