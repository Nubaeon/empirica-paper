#!/usr/bin/env python3
"""Extract clean dataset from Empirica production DB for paper v2.

Filters out test/default AI IDs, exports to CSV matching existing structure.
"""

import csv
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

# Configuration
PROD_DB = Path("/home/yogapad/empirical-ai/empirica/.empirica/sessions/sessions.db")
OUTPUT_DIR = Path("/home/yogapad/empirical-ai/empirica-paper/data")
EMPIRICA_VERSION = "1.6.0"

# AI IDs to exclude (test/default agents)
EXCLUDE_AI_IDS = {
    "test-ai", "test_agent", "test-ai-agent", "test-goal-agent",
    "default", "default-agent", "demo", "demo-agent",
}

# Subagent AI IDs — include in dataset (they represent real system behavior)
# Explore, Bash, Plan, general-purpose, claude-code-guide are real subagents


def get_conn():
    conn = sqlite3.connect(str(PROD_DB))
    conn.row_factory = sqlite3.Row
    return conn


def get_clean_session_ids(conn):
    """Get session IDs excluding test/default AI IDs."""
    placeholders = ",".join("?" for _ in EXCLUDE_AI_IDS)
    rows = conn.execute(
        f"SELECT session_id FROM sessions WHERE ai_id NOT IN ({placeholders})",
        list(EXCLUDE_AI_IDS)
    ).fetchall()
    return {r["session_id"] for r in rows}


def export_query(conn, query, params, filepath, headers=None):
    """Execute query and export to CSV."""
    rows = conn.execute(query, params).fetchall()
    if not rows:
        # Write empty file with headers if provided
        if headers:
            with open(filepath, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(headers)
        return 0

    cols = headers or [desc[0] for desc in conn.execute(query, params).description]
    with open(filepath, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for row in rows:
            w.writerow(list(row))
    return len(rows)


def export_sessions(conn, clean_ids):
    """Export sessions table."""
    placeholders = ",".join("?" for _ in clean_ids)
    q = f"""SELECT session_id, ai_id, user_id, start_time, end_time,
            components_loaded, total_turns, total_cascades, avg_confidence,
            drift_detected, session_notes, created_at, project_id, subject,
            bootstrap_level, instance_id, parent_session_id
            FROM sessions WHERE session_id IN ({placeholders})
            ORDER BY created_at"""
    return export_query(conn, q, list(clean_ids),
                       OUTPUT_DIR / "sessions" / "sessions.csv")


def export_cascades(conn, clean_ids):
    """Export cascades table."""
    placeholders = ",".join("?" for _ in clean_ids)
    q = f"""SELECT cascade_id, session_id, task, context_json, goal_id, goal_json,
            preflight_completed, think_completed, plan_completed,
            investigate_completed, check_completed, act_completed,
            postflight_completed, final_action, final_confidence,
            investigation_rounds, duration_ms, started_at, completed_at,
            engagement_gate_passed, bayesian_active, drift_monitored,
            epistemic_delta
            FROM cascades WHERE session_id IN ({placeholders})
            ORDER BY started_at"""
    return export_query(conn, q, list(clean_ids),
                       OUTPUT_DIR / "calibration" / "cascades.csv")


def export_bayesian_beliefs(conn, clean_ids):
    """Export bayesian_beliefs — linked through cascades."""
    placeholders = ",".join("?" for _ in clean_ids)
    q = f"""SELECT b.belief_id, b.cascade_id, b.vector_name, b.mean, b.variance,
            b.evidence_count, b.prior_mean, b.prior_variance, b.last_updated
            FROM bayesian_beliefs b
            JOIN cascades c ON b.cascade_id = c.cascade_id
            WHERE c.session_id IN ({placeholders})
            ORDER BY b.vector_name, b.evidence_count"""
    return export_query(conn, q, list(clean_ids),
                       OUTPUT_DIR / "calibration" / "bayesian_beliefs.csv")


def export_calibration_convergence(conn, clean_ids):
    """Export calibration convergence data (beliefs sorted by evidence)."""
    placeholders = ",".join("?" for _ in clean_ids)
    q = f"""SELECT b.vector_name, b.mean, b.variance, b.evidence_count,
            b.prior_mean, b.prior_variance
            FROM bayesian_beliefs b
            JOIN cascades c ON b.cascade_id = c.cascade_id
            WHERE c.session_id IN ({placeholders})
            ORDER BY b.vector_name, b.evidence_count"""
    return export_query(conn, q, list(clean_ids),
                       OUTPUT_DIR / "calibration" / "calibration_convergence.csv")


def export_convergence_summary(conn, clean_ids):
    """Export calibration convergence summary per vector."""
    placeholders = ",".join("?" for _ in clean_ids)
    q = f"""SELECT b.vector_name,
            COUNT(*) as observations,
            AVG(b.mean) as avg_mean,
            AVG(b.variance) as avg_variance,
            MAX(b.evidence_count) as max_evidence
            FROM bayesian_beliefs b
            JOIN cascades c ON b.cascade_id = c.cascade_id
            WHERE c.session_id IN ({placeholders})
            GROUP BY b.vector_name
            ORDER BY b.vector_name"""
    return export_query(conn, q, list(clean_ids),
                       OUTPUT_DIR / "calibration" / "calibration_convergence_summary.csv")


def export_epistemic_snapshots(conn, clean_ids):
    """Export epistemic snapshots."""
    placeholders = ",".join("?" for _ in clean_ids)
    q = f"""SELECT snapshot_id, session_id, ai_id, timestamp, cascade_phase,
            cascade_id, vectors, delta, previous_snapshot_id, context_summary,
            evidence_refs, db_session_ref, domain_vectors,
            original_context_tokens, snapshot_tokens, compression_ratio,
            information_loss_estimate, fidelity_score, transfer_count, created_at
            FROM epistemic_snapshots WHERE session_id IN ({placeholders})
            ORDER BY timestamp"""
    return export_query(conn, q, list(clean_ids),
                       OUTPUT_DIR / "sessions" / "epistemic_snapshots.csv")


def export_learning_deltas(conn, clean_ids):
    """Export clean learning deltas (PREFLIGHT->POSTFLIGHT pairs with non-null deltas)."""
    placeholders = ",".join("?" for _ in clean_ids)
    q = f"""SELECT snapshot_id, session_id, timestamp, vectors as postflight_vectors,
            delta as preflight_to_postflight_delta
            FROM epistemic_snapshots
            WHERE session_id IN ({placeholders})
            AND cascade_phase = 'POSTFLIGHT'
            AND delta IS NOT NULL
            AND delta != '{{}}'
            AND delta != 'null'
            ORDER BY timestamp"""
    rows = conn.execute(q, list(clean_ids)).fetchall()

    filepath = OUTPUT_DIR / "sessions" / "learning_deltas_clean.csv"
    headers = ["session_id", "snapshot_id", "timestamp",
               "postflight_vectors", "preflight_to_postflight_delta"]
    with open(filepath, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(headers)
        for row in rows:
            # Only include if delta has actual non-zero values
            try:
                delta = json.loads(row["preflight_to_postflight_delta"])
                if delta and any(abs(v) > 0.001 for v in delta.values() if isinstance(v, (int, float))):
                    w.writerow([row["session_id"], row["snapshot_id"],
                               row["timestamp"], row["postflight_vectors"],
                               row["preflight_to_postflight_delta"]])
            except (json.JSONDecodeError, TypeError, AttributeError):
                continue
    # Count written rows
    with open(filepath) as f:
        return sum(1 for _ in f) - 1


def export_goals(conn, clean_ids):
    """Export goals."""
    placeholders = ",".join("?" for _ in clean_ids)
    q = f"""SELECT id, session_id, objective, scope, estimated_complexity,
            created_timestamp, completed_timestamp, is_completed, goal_data,
            status, beads_issue_id, project_id, ai_id, transaction_id
            FROM goals WHERE session_id IN ({placeholders})
            ORDER BY created_timestamp"""
    return export_query(conn, q, list(clean_ids),
                       OUTPUT_DIR / "sessions" / "goals.csv")


def export_subtasks(conn, clean_ids):
    """Export subtasks (linked through goals)."""
    placeholders = ",".join("?" for _ in clean_ids)
    q = f"""SELECT s.id, s.goal_id, s.description, s.status,
            s.epistemic_importance, s.estimated_tokens, s.actual_tokens,
            s.completion_evidence, s.notes, s.created_timestamp,
            s.completed_timestamp, s.subtask_data
            FROM subtasks s
            JOIN goals g ON s.goal_id = g.id
            WHERE g.session_id IN ({placeholders})
            ORDER BY s.created_timestamp"""
    return export_query(conn, q, list(clean_ids),
                       OUTPUT_DIR / "sessions" / "subtasks.csv")


def export_handoff_reports(conn, clean_ids):
    """Export handoff reports."""
    placeholders = ",".join("?" for _ in clean_ids)
    q = f"""SELECT session_id, ai_id, timestamp, task_summary, duration_seconds,
            epistemic_deltas, key_findings, knowledge_gaps_filled,
            remaining_unknowns, investigation_tools, next_session_context,
            recommended_next_steps, artifacts_created, calibration_status,
            overall_confidence_delta, compressed_json, markdown_report,
            created_at, noetic_tools
            FROM handoff_reports WHERE session_id IN ({placeholders})
            ORDER BY created_at"""
    return export_query(conn, q, list(clean_ids),
                       OUTPUT_DIR / "sessions" / "handoff_reports.csv")


def export_lessons(conn):
    """Export lessons (not session-scoped, include all)."""
    q = """SELECT id, name, version, description, domain, tags,
           source_confidence, teaching_quality, reproducibility,
           step_count, prereq_count, replay_count, success_rate,
           suggested_tier, suggested_price, created_by,
           created_timestamp, updated_timestamp, lesson_data
           FROM lessons ORDER BY created_timestamp"""
    return export_query(conn, q, [], OUTPUT_DIR / "sessions" / "lessons.csv")


def export_reflexes(conn, clean_ids):
    """Export reflexes."""
    placeholders = ",".join("?" for _ in clean_ids)
    q = f"""SELECT id, session_id, cascade_id, phase, round, timestamp,
            engagement, know, do, context, clarity, coherence, signal,
            density, state, change, completion, impact, uncertainty,
            reflex_data, reasoning, evidence, project_id, transaction_id
            FROM reflexes WHERE session_id IN ({placeholders})
            ORDER BY timestamp"""
    return export_query(conn, q, list(clean_ids),
                       OUTPUT_DIR / "findings" / "reflexes.csv")


def export_project_findings(conn, clean_ids):
    """Export project findings."""
    placeholders = ",".join("?" for _ in clean_ids)
    q = f"""SELECT id, project_id, session_id, goal_id, subtask_id, finding,
            created_timestamp, finding_data, subject, impact, transaction_id
            FROM project_findings WHERE session_id IN ({placeholders})
            ORDER BY created_timestamp"""
    return export_query(conn, q, list(clean_ids),
                       OUTPUT_DIR / "findings" / "project_findings.csv")


def export_session_findings(conn, clean_ids):
    """Export session-scoped findings (project_findings without project_id)."""
    # In the DB, session findings are stored in project_findings with NULL project_id
    # or we can check entity_type. For compatibility, export those with NULL project_id.
    placeholders = ",".join("?" for _ in clean_ids)
    q = f"""SELECT id, session_id, goal_id, subtask_id, finding,
            created_timestamp, finding_data, subject, impact
            FROM project_findings
            WHERE session_id IN ({placeholders})
            AND (project_id IS NULL OR project_id = '')
            ORDER BY created_timestamp"""
    count = export_query(conn, q, list(clean_ids),
                        OUTPUT_DIR / "findings" / "session_findings.csv")
    if count == 0:
        # If no null project_id findings, export all as session findings too
        # (some extractions included all findings in session_findings)
        q2 = f"""SELECT id, session_id, goal_id, subtask_id, finding,
                created_timestamp, finding_data, subject, impact
                FROM project_findings
                WHERE session_id IN ({placeholders})
                ORDER BY created_timestamp"""
        count = export_query(conn, q2, list(clean_ids),
                            OUTPUT_DIR / "findings" / "session_findings.csv")
    return count


def export_dead_ends(conn, clean_ids):
    """Export dead ends."""
    placeholders = ",".join("?" for _ in clean_ids)
    q = f"""SELECT id, project_id, session_id, goal_id, subtask_id, approach,
            why_failed, created_timestamp, dead_end_data, subject, transaction_id
            FROM project_dead_ends WHERE session_id IN ({placeholders})
            ORDER BY created_timestamp"""
    return export_query(conn, q, list(clean_ids),
                       OUTPUT_DIR / "findings" / "dead_ends.csv")


def export_mistakes(conn, clean_ids):
    """Export project-scoped mistakes."""
    placeholders = ",".join("?" for _ in clean_ids)
    q = f"""SELECT id, session_id, goal_id, mistake, why_wrong, cost_estimate,
            root_cause_vector, prevention, created_timestamp, mistake_data,
            project_id, transaction_id
            FROM mistakes_made
            WHERE session_id IN ({placeholders})
            AND project_id IS NOT NULL AND project_id != ''
            ORDER BY created_timestamp"""
    return export_query(conn, q, list(clean_ids),
                       OUTPUT_DIR / "findings" / "mistakes.csv")


def export_session_mistakes(conn, clean_ids):
    """Export session-scoped mistakes (no project_id)."""
    placeholders = ",".join("?" for _ in clean_ids)
    q = f"""SELECT id, session_id, goal_id, mistake, why_wrong, cost_estimate,
            root_cause_vector, prevention, created_timestamp, mistake_data
            FROM mistakes_made
            WHERE session_id IN ({placeholders})
            AND (project_id IS NULL OR project_id = '')
            ORDER BY created_timestamp"""
    return export_query(conn, q, list(clean_ids),
                       OUTPUT_DIR / "findings" / "session_mistakes.csv")


def export_project_unknowns(conn, clean_ids):
    """Export project unknowns."""
    placeholders = ",".join("?" for _ in clean_ids)
    q = f"""SELECT id, project_id, session_id, goal_id, subtask_id, unknown,
            is_resolved, resolved_by, created_timestamp, resolved_timestamp,
            unknown_data, subject, impact, transaction_id
            FROM project_unknowns WHERE session_id IN ({placeholders})
            ORDER BY created_timestamp"""
    return export_query(conn, q, list(clean_ids),
                       OUTPUT_DIR / "unknowns" / "project_unknowns.csv")


def export_session_unknowns(conn, clean_ids):
    """Export session unknowns (project_unknowns without project_id)."""
    placeholders = ",".join("?" for _ in clean_ids)
    q = f"""SELECT id, session_id, goal_id, subtask_id, unknown,
            is_resolved, resolved_by, created_timestamp, resolved_timestamp,
            unknown_data, subject, impact
            FROM project_unknowns
            WHERE session_id IN ({placeholders})
            AND (project_id IS NULL OR project_id = '')
            ORDER BY created_timestamp"""
    count = export_query(conn, q, list(clean_ids),
                        OUTPUT_DIR / "unknowns" / "session_unknowns.csv")
    if count == 0:
        q2 = f"""SELECT id, session_id, goal_id, subtask_id, unknown,
                is_resolved, resolved_by, created_timestamp, resolved_timestamp,
                unknown_data, subject, impact
                FROM project_unknowns
                WHERE session_id IN ({placeholders})
                ORDER BY created_timestamp"""
        count = export_query(conn, q2, list(clean_ids),
                            OUTPUT_DIR / "unknowns" / "session_unknowns.csv")
    return count


def export_grounded_beliefs(conn, clean_ids):
    """Export grounded beliefs."""
    placeholders = ",".join("?" for _ in clean_ids)
    q = f"""SELECT belief_id, session_id, ai_id, vector_name, mean, variance,
            evidence_count, last_observation, last_observation_source,
            self_referential_mean, divergence, last_updated
            FROM grounded_beliefs WHERE session_id IN ({placeholders})
            ORDER BY vector_name"""
    return export_query(conn, q, list(clean_ids),
                       OUTPUT_DIR / "grounded" / "grounded_beliefs.csv")


def export_grounded_verifications(conn, clean_ids):
    """Export grounded verifications."""
    placeholders = ",".join("?" for _ in clean_ids)
    q = f"""SELECT verification_id, session_id, ai_id, self_assessed_vectors,
            grounded_vectors, calibration_gaps, grounded_coverage,
            overall_calibration_score, evidence_count, sources_available,
            sources_failed, domain, goal_id, created_at
            FROM grounded_verifications WHERE session_id IN ({placeholders})
            ORDER BY created_at"""
    return export_query(conn, q, list(clean_ids),
                       OUTPUT_DIR / "grounded" / "grounded_verifications.csv")


def export_verification_evidence(conn, clean_ids):
    """Export verification evidence."""
    placeholders = ",".join("?" for _ in clean_ids)
    q = f"""SELECT evidence_id, session_id, source, metric_name, raw_value,
            normalized_value, quality, supports_vectors, collected_at, metadata
            FROM verification_evidence WHERE session_id IN ({placeholders})
            ORDER BY collected_at"""
    return export_query(conn, q, list(clean_ids),
                       OUTPUT_DIR / "grounded" / "verification_evidence.csv")


def export_calibration_trajectory(conn, clean_ids):
    """Export calibration trajectory."""
    placeholders = ",".join("?" for _ in clean_ids)
    q = f"""SELECT point_id, session_id, ai_id, vector_name, self_assessed,
            grounded, gap, domain, goal_id, timestamp
            FROM calibration_trajectory WHERE session_id IN ({placeholders})
            ORDER BY timestamp"""
    return export_query(conn, q, list(clean_ids),
                       OUTPUT_DIR / "grounded" / "calibration_trajectory.csv")


def compute_aggregate_stats(conn, clean_ids):
    """Compute aggregate statistics for the paper."""
    placeholders = ",".join("?" for _ in clean_ids)
    ids = list(clean_ids)

    stats = {}

    # Total sessions
    stats["total_sessions"] = len(clean_ids)

    # Date range
    row = conn.execute(
        f"SELECT MIN(created_at), MAX(created_at) FROM sessions WHERE session_id IN ({placeholders})",
        ids
    ).fetchone()
    stats["date_range"] = {"start": row[0], "end": row[1]}

    # Total evidence observations
    row = conn.execute(
        f"""SELECT SUM(b.evidence_count) FROM bayesian_beliefs b
            JOIN cascades c ON b.cascade_id = c.cascade_id
            WHERE c.session_id IN ({placeholders})""",
        ids
    ).fetchone()
    stats["total_evidence_observations"] = int(row[0] or 0)

    # Bayesian beliefs count
    row = conn.execute(
        f"""SELECT COUNT(*) FROM bayesian_beliefs b
            JOIN cascades c ON b.cascade_id = c.cascade_id
            WHERE c.session_id IN ({placeholders})""",
        ids
    ).fetchone()
    stats["bayesian_beliefs_count"] = row[0]

    # Clean sessions (those with POSTFLIGHT snapshots with non-null deltas)
    row = conn.execute(
        f"""SELECT COUNT(DISTINCT session_id) FROM epistemic_snapshots
            WHERE session_id IN ({placeholders})
            AND cascade_phase = 'POSTFLIGHT'
            AND delta IS NOT NULL AND delta != '{{}}' AND delta != 'null'""",
        ids
    ).fetchone()
    stats["clean_sessions"] = row[0]

    # Improvement rate (sessions where KNOW delta > 0)
    rows = conn.execute(
        f"""SELECT delta FROM epistemic_snapshots
            WHERE session_id IN ({placeholders})
            AND cascade_phase = 'POSTFLIGHT'
            AND delta IS NOT NULL AND delta != '{{}}' AND delta != 'null'""",
        ids
    ).fetchall()

    improved = 0
    total_deltas = 0
    know_deltas = []
    for row in rows:
        try:
            delta = json.loads(row[0])
            if delta and isinstance(delta, dict):
                total_deltas += 1
                know_delta = delta.get("know", 0)
                if isinstance(know_delta, (int, float)):
                    know_deltas.append(know_delta)
                    if know_delta > 0:
                        improved += 1
        except (json.JSONDecodeError, TypeError):
            continue

    stats["improvement_count"] = improved
    stats["total_deltas"] = total_deltas
    stats["improvement_rate"] = round(improved / total_deltas * 100, 1) if total_deltas > 0 else 0
    stats["mean_know_delta"] = round(sum(know_deltas) / len(know_deltas), 3) if know_deltas else 0

    # Per-vector belief statistics
    vector_stats = conn.execute(
        f"""SELECT b.vector_name,
                COUNT(*) as count,
                SUM(b.evidence_count) as total_evidence,
                AVG(b.prior_mean) as avg_prior,
                AVG(b.mean) as avg_posterior,
                AVG(b.mean) - AVG(b.prior_mean) as avg_delta,
                AVG(b.variance) as avg_variance,
                MAX(b.evidence_count) as max_evidence
            FROM bayesian_beliefs b
            JOIN cascades c ON b.cascade_id = c.cascade_id
            WHERE c.session_id IN ({placeholders})
            GROUP BY b.vector_name
            ORDER BY avg_delta DESC""",
        ids
    ).fetchall()

    stats["per_vector"] = {}
    for row in vector_stats:
        stats["per_vector"][row[0]] = {
            "count": row[1],
            "total_evidence": int(row[2] or 0),
            "avg_prior": round(row[3], 3),
            "avg_posterior": round(row[4], 3),
            "avg_delta": round(row[5], 3),
            "avg_variance": round(row[6], 6),
            "max_evidence": row[7],
        }

    # Convergence analysis
    convergence = conn.execute(
        f"""SELECT
                CASE
                    WHEN b.evidence_count <= 5 THEN '5'
                    WHEN b.evidence_count <= 15 THEN '15'
                    WHEN b.evidence_count <= 40 THEN '40'
                    WHEN b.evidence_count <= 87 THEN '87'
                    ELSE '175+'
                END as evidence_bucket,
                COUNT(*) as beliefs,
                AVG(b.variance) as avg_variance
            FROM bayesian_beliefs b
            JOIN cascades c ON b.cascade_id = c.cascade_id
            WHERE c.session_id IN ({placeholders})
            GROUP BY evidence_bucket
            ORDER BY MIN(b.evidence_count)""",
        ids
    ).fetchall()

    stats["convergence"] = []
    baseline_var = None
    for row in convergence:
        entry = {
            "evidence_level": row[0],
            "beliefs": row[1],
            "avg_variance": round(row[2], 6),
        }
        if baseline_var is None:
            baseline_var = row[2]
            entry["reduction_factor"] = "1x (baseline)"
        else:
            factor = round(baseline_var / row[2], 0) if row[2] > 0 else "inf"
            entry["reduction_factor"] = f"{int(factor)}x"
        stats["convergence"].append(entry)

    # Grounded calibration stats
    row = conn.execute(
        f"""SELECT COUNT(*) FROM grounded_verifications
            WHERE session_id IN ({placeholders})""",
        ids
    ).fetchone()
    stats["grounded_verifications"] = row[0]

    row = conn.execute(
        f"""SELECT COUNT(*) FROM calibration_trajectory
            WHERE session_id IN ({placeholders})""",
        ids
    ).fetchone()
    stats["calibration_trajectory_points"] = row[0]

    # Artifact counts
    for table, label in [
        ("goals", "goals"),
        ("project_findings", "project_findings"),
        ("project_dead_ends", "dead_ends"),
        ("mistakes_made", "mistakes"),
        ("project_unknowns", "project_unknowns"),
        ("reflexes", "reflexes"),
        ("cascades", "cascades"),
        ("epistemic_snapshots", "epistemic_snapshots"),
    ]:
        row = conn.execute(
            f"SELECT COUNT(*) FROM {table} WHERE session_id IN ({placeholders})",
            ids
        ).fetchone()
        stats[f"artifact_{label}"] = row[0]

    return stats


def write_manifest(stats, counts):
    """Write DATA_MANIFEST.json."""
    manifest = {
        "extraction_date": datetime.now().isoformat(),
        "source_db": str(PROD_DB),
        "empirica_version": EMPIRICA_VERSION,
        "dataset_version": "2.0.0",
        "collection_period": stats["date_range"],
        "excluded_ai_ids": sorted(EXCLUDE_AI_IDS),
        "statistics": {
            "total_sessions": stats["total_sessions"],
            "clean_sessions": stats["clean_sessions"],
            "total_evidence_observations": stats["total_evidence_observations"],
            "bayesian_beliefs": stats["bayesian_beliefs_count"],
            "improvement_rate_pct": stats["improvement_rate"],
            "mean_know_delta": stats["mean_know_delta"],
            "grounded_verifications": stats["grounded_verifications"],
            "calibration_trajectory_points": stats["calibration_trajectory_points"],
        },
        "per_vector_statistics": stats["per_vector"],
        "convergence_analysis": stats["convergence"],
        "artifact_counts": {k: v for k, v in stats.items() if k.startswith("artifact_")},
        "file_row_counts": counts,
    }
    with open(OUTPUT_DIR / "DATA_MANIFEST.json", "w") as f:
        json.dump(manifest, f, indent=2)
    return manifest


def main():
    print(f"Extracting data from {PROD_DB}")
    print(f"Output directory: {OUTPUT_DIR}")

    # Ensure output directories exist
    for subdir in ["calibration", "sessions", "findings", "unknowns", "grounded"]:
        (OUTPUT_DIR / subdir).mkdir(parents=True, exist_ok=True)

    conn = get_conn()
    clean_ids = get_clean_session_ids(conn)
    print(f"\nClean sessions: {len(clean_ids)} (excluded {EXCLUDE_AI_IDS})")

    counts = {}
    exports = [
        ("sessions/sessions.csv", lambda: export_sessions(conn, clean_ids)),
        ("calibration/cascades.csv", lambda: export_cascades(conn, clean_ids)),
        ("calibration/bayesian_beliefs.csv", lambda: export_bayesian_beliefs(conn, clean_ids)),
        ("calibration/calibration_convergence.csv", lambda: export_calibration_convergence(conn, clean_ids)),
        ("calibration/calibration_convergence_summary.csv", lambda: export_convergence_summary(conn, clean_ids)),
        ("sessions/epistemic_snapshots.csv", lambda: export_epistemic_snapshots(conn, clean_ids)),
        ("sessions/learning_deltas_clean.csv", lambda: export_learning_deltas(conn, clean_ids)),
        ("sessions/goals.csv", lambda: export_goals(conn, clean_ids)),
        ("sessions/subtasks.csv", lambda: export_subtasks(conn, clean_ids)),
        ("sessions/handoff_reports.csv", lambda: export_handoff_reports(conn, clean_ids)),
        ("sessions/lessons.csv", lambda: export_lessons(conn)),
        ("findings/reflexes.csv", lambda: export_reflexes(conn, clean_ids)),
        ("findings/project_findings.csv", lambda: export_project_findings(conn, clean_ids)),
        ("findings/session_findings.csv", lambda: export_session_findings(conn, clean_ids)),
        ("findings/dead_ends.csv", lambda: export_dead_ends(conn, clean_ids)),
        ("findings/mistakes.csv", lambda: export_mistakes(conn, clean_ids)),
        ("findings/session_mistakes.csv", lambda: export_session_mistakes(conn, clean_ids)),
        ("unknowns/project_unknowns.csv", lambda: export_project_unknowns(conn, clean_ids)),
        ("unknowns/session_unknowns.csv", lambda: export_session_unknowns(conn, clean_ids)),
        ("grounded/grounded_beliefs.csv", lambda: export_grounded_beliefs(conn, clean_ids)),
        ("grounded/grounded_verifications.csv", lambda: export_grounded_verifications(conn, clean_ids)),
        ("grounded/verification_evidence.csv", lambda: export_verification_evidence(conn, clean_ids)),
        ("grounded/calibration_trajectory.csv", lambda: export_calibration_trajectory(conn, clean_ids)),
    ]

    for name, fn in exports:
        count = fn()
        counts[name] = count
        print(f"  {name}: {count} rows")

    print("\nComputing aggregate statistics...")
    stats = compute_aggregate_stats(conn, clean_ids)

    print(f"\n=== KEY STATISTICS ===")
    print(f"  Sessions: {stats['total_sessions']}")
    print(f"  Clean sessions (with learning deltas): {stats['clean_sessions']}")
    print(f"  Total evidence observations: {stats['total_evidence_observations']:,}")
    print(f"  Bayesian beliefs: {stats['bayesian_beliefs_count']:,}")
    print(f"  Improvement rate: {stats['improvement_rate']}%")
    print(f"  Mean KNOW delta: {stats['mean_know_delta']}")
    print(f"  Date range: {stats['date_range']['start']} to {stats['date_range']['end']}")
    print(f"\n  Per-vector deltas:")
    for vec, vs in sorted(stats["per_vector"].items(), key=lambda x: -x[1]["avg_delta"]):
        print(f"    {vec}: {vs['avg_prior']:.3f} -> {vs['avg_posterior']:.3f} (delta={vs['avg_delta']:+.3f}, evidence={vs['total_evidence']:,})")
    print(f"\n  Convergence:")
    for c in stats["convergence"]:
        print(f"    Evidence {c['evidence_level']}: {c['beliefs']} beliefs, variance={c['avg_variance']:.6f} ({c['reduction_factor']})")

    print("\nWriting DATA_MANIFEST.json...")
    manifest = write_manifest(stats, counts)

    conn.close()
    print("\nDone! Dataset v2.0.0 extracted successfully.")
    return stats


if __name__ == "__main__":
    main()
