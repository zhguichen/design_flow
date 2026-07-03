#!/usr/bin/env python3
"""
design-flow — deterministic stats for Workflow 5 (result-analysis).

Reads a run directory (responses.jsonl + survey.json + respondents.jsonl + selection.json)
and writes stats.json: per-question descriptive stats + cross-tabs by archetype.

Phase 1 of WF5. The LLM (phase 2) reads stats.json + responses.jsonl to do
theme coding and write report.md. This script supplies facts; the model
supplies judgment.

Usage:
    python3 scripts/analyze.py <run_dir>
    python3 scripts/analyze.py <run_dir> --output stats.json

Stdlib only. No external dependencies.
"""

import argparse
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path


class AnalyzeError(Exception):
    """Raised when required inputs are missing or malformed."""


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def numeric_stats(values):
    """count/mean/median/min/max/distribution for likert/rating/nps."""
    if not values:
        return {"count": 0}
    return {
        "count": len(values),
        "mean": round(statistics.mean(values), 2),
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values),
        "distribution": {str(k): v for k, v in sorted(Counter(values).items())},
    }


def categorical_stats(values):
    """count per option for single-choice/multi-select."""
    c = Counter(values)
    return {
        "count": sum(c.values()),
        "distribution": {k: v for k, v in sorted(c.items(), key=lambda x: -x[1])},
    }


def ranking_stats(entries):
    """average rank per item (1 = ranked first)."""
    ranks = defaultdict(list)
    for _, ans, _ in entries:
        if isinstance(ans, list):
            for i, item in enumerate(ans, 1):
                ranks[item].append(i)
    return {item: round(statistics.mean(rs), 2) for item, rs in ranks.items()}


def analyze(run_dir):
    run = Path(run_dir)
    required = ["survey.json", "respondents.jsonl", "responses.jsonl", "selection.json"]
    for name in required:
        if not (run / name).exists():
            raise AnalyzeError(f"missing required file: {run / name}")

    survey = load_json(run / "survey.json")
    respondents = load_jsonl(run / "respondents.jsonl")
    responses = load_jsonl(run / "responses.jsonl")

    arch_map = {r["respondent_id"]: r.get("archetype_id") for r in respondents}
    response_ids = [response["respondent_id"] for response in responses]
    arch_counts = Counter(arch_map.get(rid) for rid in response_ids)

    questions = survey.get("questions", [])
    answers_by_q = defaultdict(list)  # qid -> [(respondent_id, answer, uncertain)]
    for resp in responses:
        rid = resp["respondent_id"]
        for a in resp.get("answers", []):
            answers_by_q[a.get("question_id")].append(
                (rid, a.get("answer"), a.get("uncertain", False))
            )

    per_question = {}
    cross_tabs = {}

    for q in questions:
        qid = q["question_id"]
        qtype = q.get("type")
        entries = answers_by_q.get(qid, [])
        certain = [e for e in entries if not e[2]]
        uncertain_count = sum(1 for e in entries if e[2])

        if qtype in ("likert", "rating", "nps"):
            values = [e[1] for e in certain if isinstance(e[1], (int, float))]
            per_question[qid] = {
                "type": qtype,
                "construct_measured": q.get("construct_measured"),
                "uncertain_count": uncertain_count,
                **numeric_stats(values),
            }
            by_arch = defaultdict(list)
            for e in certain:
                if isinstance(e[1], (int, float)):
                    by_arch[arch_map.get(e[0])].append(e[1])
            cross_tabs[qid] = {str(a): numeric_stats(v) for a, v in by_arch.items()}

        elif qtype in ("single-choice", "multi-select"):
            vals = []
            for e in certain:
                if isinstance(e[1], list):
                    vals.extend(e[1])
                else:
                    vals.append(e[1])
            per_question[qid] = {
                "type": qtype,
                "construct_measured": q.get("construct_measured"),
                "uncertain_count": uncertain_count,
                **categorical_stats(vals),
            }
            by_arch = defaultdict(list)
            for e in certain:
                items = e[1] if isinstance(e[1], list) else [e[1]]
                by_arch[arch_map.get(e[0])].extend(items)
            cross_tabs[qid] = {str(a): categorical_stats(v) for a, v in by_arch.items()}

        elif qtype == "open":
            per_question[qid] = {
                "type": qtype,
                "construct_measured": q.get("construct_measured"),
                "count": len(certain),
                "uncertain_count": uncertain_count,
                "answers": [e[1] for e in certain if e[1]],
                "note": "open-ended; theme coding done by LLM in phase 2",
            }

        elif qtype == "ranking":
            per_question[qid] = {
                "type": qtype,
                "construct_measured": q.get("construct_measured"),
                "count": len(certain),
                "uncertain_count": uncertain_count,
                "average_rank": ranking_stats(certain),
            }

        else:
            per_question[qid] = {
                "type": qtype,
                "count": len(certain),
                "note": "unsupported type",
            }

    result = {
        "total_n": len(responses),
        "by_archetype": {str(k): v for k, v in arch_counts.items()},
        "per_question": per_question,
        "cross_tabs_by_archetype": cross_tabs,
        "note": (
            "deterministic stats over synthetic scenario records; counts and percentages "
            "describe this simulation only and are not population estimates; "
            "theme coding & insights by LLM"
        ),
    }
    selection = load_json(run / "selection.json")
    result["selection"] = {
        key: selection.get(key)
        for key in (
            "mode",
            "pool_n",
            "selected_n",
            "seed",
            "by_archetype",
            "excluded_count",
            "coverage",
        )
    }
    return result


def main():
    parser = argparse.ArgumentParser(
        description="design-flow WF5 deterministic stats"
    )
    parser.add_argument("run_dir", help="path to runs/<ts>/ with responses.jsonl etc.")
    parser.add_argument("--output", help="output path (default <run_dir>/stats.json)")
    args = parser.parse_args()

    try:
        result = analyze(args.run_dir)
    except AnalyzeError as e:
        print(f"AnalyzeError: {e}", file=sys.stderr)
        sys.exit(1)

    out = Path(args.output) if args.output else Path(args.run_dir) / "stats.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
