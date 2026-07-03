#!/usr/bin/env python3
"""Create a deterministic full or stratified-pilot respondent selection."""

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path


class SelectionError(Exception):
    pass


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def allocate_counts(groups, n, rng):
    archetypes = list(groups)
    rng.shuffle(archetypes)
    counts = {aid: 1 for aid in archetypes}
    total = sum(len(rows) for rows in groups.values())

    while sum(counts.values()) < n:
        eligible = [aid for aid in archetypes if counts[aid] < len(groups[aid])]
        if not eligible:
            raise SelectionError("not enough respondent capacity for requested n")
        aid = max(
            eligible,
            key=lambda key: (n * len(groups[key]) / total) - counts[key],
        )
        counts[aid] += 1
    return counts


def select(run_dir, mode, n=None, seed=42):
    run = Path(run_dir)
    respondents_path = run / "respondents.jsonl"
    meta_path = run / "respondents_meta.json"
    if not respondents_path.exists() or not meta_path.exists():
        raise SelectionError("respondents.jsonl and respondents_meta.json are required")

    respondents = load_jsonl(respondents_path)
    meta = load_json(meta_path)
    if not respondents:
        raise SelectionError("respondents.jsonl is empty")

    groups = defaultdict(list)
    for row in respondents:
        rid = row.get("respondent_id")
        aid = row.get("archetype_id")
        if not rid or not aid:
            raise SelectionError("every respondent requires respondent_id and archetype_id")
        groups[aid].append(rid)

    pool_n = len(respondents)
    rng = random.Random(seed)

    if mode == "full":
        selected_ids = [row["respondent_id"] for row in respondents]
        counts = {aid: len(ids) for aid, ids in groups.items()}
        effective_seed = None
    else:
        if n is None:
            raise SelectionError("--n is required for stratified-pilot mode")
        if n < len(groups):
            raise SelectionError(
                f"pilot n={n} is smaller than archetype count={len(groups)}"
            )
        if n == pool_n:
            raise SelectionError(
                f"pilot n={n} equals persona pool; use --mode full instead"
            )
        if n > pool_n:
            raise SelectionError(f"pilot n={n} exceeds persona pool={pool_n}")
        counts = allocate_counts(groups, n, rng)
        chosen = set()
        for aid, count in counts.items():
            chosen.update(rng.sample(groups[aid], count))
        selected_ids = [
            row["respondent_id"]
            for row in respondents
            if row["respondent_id"] in chosen
        ]
        effective_seed = seed

    variants = meta.get("allocation", {}).get("variants_per_archetype", 3)
    variants_met = all(count >= variants for count in counts.values())
    selected_n = len(selected_ids)
    return {
        "mode": mode,
        "pool_n": pool_n,
        "selected_n": selected_n,
        "requested_n": selected_n if mode == "full" else n,
        "seed": effective_seed,
        "selected_respondent_ids": selected_ids,
        "by_archetype": dict(sorted(counts.items())),
        "excluded_count": pool_n - selected_n,
        "coverage": {
            "all_archetypes_included": set(counts) == set(groups)
            and all(count > 0 for count in counts.values()),
            "variants_per_archetype_target": variants,
            "variants_target_met": variants_met,
            "interpretation": (
                "完整 persona pool"
                if mode == "full"
                else "分层预演子集，不代表完整场景覆盖或真实比例"
            ),
        },
        "note": "合成样本选择 / 仅供预调研 / 用户只决定数量，具体 persona 由确定性分层抽样选择",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Select respondents for full simulation or stratified pilot"
    )
    parser.add_argument("run_dir", help="runs/<timestamp>/ directory")
    parser.add_argument(
        "--mode", choices=("full", "stratified-pilot"), default="full"
    )
    parser.add_argument("--n", type=int, help="pilot respondent count")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", help="default: <run_dir>/selection.json")
    args = parser.parse_args()

    try:
        result = select(args.run_dir, args.mode, args.n, args.seed)
    except (OSError, json.JSONDecodeError, SelectionError) as exc:
        print(f"SelectionError: {exc}", file=sys.stderr)
        return 1

    output = Path(args.output) if args.output else Path(args.run_dir) / "selection.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
