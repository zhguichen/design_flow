#!/usr/bin/env python3
"""Validate design-flow run artifacts with deterministic structural checks."""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


STAGES = ("wf1", "wf2a", "wf2b", "wf2c", "wf3", "wf4", "wf5")
RESULT_CONSTRUCTS = {"满意度", "使用意愿", "推荐意愿", "付费意愿"}
TASK_CONSTRUCTS = {"痛点 / 阻力", "功能优先级"}
FIVE_LAYERS = ("基础身份", "社会处境", "心理倾向", "行为习惯", "作答风格")


class Validator:
    def __init__(self, run_dir):
        self.run = Path(run_dir)
        self.errors = []
        self.warnings = []
        self.cache = {}

    def error(self, message):
        self.errors.append(message)

    def warn(self, message):
        self.warnings.append(message)

    def json_file(self, name):
        if name in self.cache:
            return self.cache[name]
        path = self.run / name
        if not path.exists():
            self.error(f"missing required file: {path}")
            return None
        try:
            with open(path, encoding="utf-8") as f:
                value = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            self.error(f"invalid JSON in {path}: {exc}")
            return None
        self.cache[name] = value
        return value

    def jsonl_file(self, name):
        if name in self.cache:
            return self.cache[name]
        path = self.run / name
        if not path.exists():
            self.error(f"missing required file: {path}")
            return None
        rows = []
        try:
            with open(path, encoding="utf-8") as f:
                for lineno, line in enumerate(f, 1):
                    if not line.strip():
                        continue
                    try:
                        rows.append(json.loads(line))
                    except json.JSONDecodeError as exc:
                        self.error(f"invalid JSONL in {path}:{lineno}: {exc}")
        except OSError as exc:
            self.error(f"cannot read {path}: {exc}")
            return None
        self.cache[name] = rows
        return rows

    def require_keys(self, obj, keys, where):
        if not isinstance(obj, dict):
            self.error(f"{where} must be an object")
            return
        for key in keys:
            if key not in obj:
                self.error(f"{where} missing key: {key}")

    def unique(self, values, where):
        duplicates = [v for v, count in Counter(values).items() if count > 1]
        if duplicates:
            self.error(f"{where} contains duplicate ids: {duplicates}")

    def contains_key(self, value, forbidden):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in forbidden or self.contains_key(child, forbidden):
                    return True
        elif isinstance(value, list):
            return any(self.contains_key(item, forbidden) for item in value)
        return False

    def survey_context(self):
        survey = self.json_file("survey.json")
        if not isinstance(survey, dict):
            return None, {}, set()
        questions = survey.get("questions", [])
        question_map = {
            q.get("question_id"): q for q in questions if isinstance(q, dict)
        }
        return survey, question_map, set(question_map)

    def archetype_context(self):
        data = self.json_file("archetypes.json")
        items = data.get("archetypes", []) if isinstance(data, dict) else []
        return data, {item.get("archetype_id"): item for item in items if isinstance(item, dict)}

    def mechanism_context(self):
        data = self.json_file("behavior_mechanisms.json")
        items = data.get("mechanisms", []) if isinstance(data, dict) else []
        return data, {item.get("mechanism_id"): item for item in items if isinstance(item, dict)}

    def wf1(self):
        survey, question_map, _ = self.survey_context()
        if survey is None:
            return
        self.require_keys(
            survey,
            (
                "research_question",
                "target_population",
                "purpose",
                "simulation_n",
                "simulation_n_rationale",
                "estimated_minutes",
                "questions",
            ),
            "survey.json",
        )
        questions = survey.get("questions", [])
        if not isinstance(questions, list) or not questions:
            self.error("survey.questions must be a non-empty list")
            return
        if len(questions) > 15:
            self.error("survey contains more than 15 questions")
        if survey.get("estimated_minutes", 0) > 5:
            self.error("survey estimated_minutes exceeds 5")
        n = survey.get("simulation_n")
        if n is not None and (not isinstance(n, int) or n <= 0):
            self.error("survey.simulation_n must be a positive integer or null")
        self.unique([q.get("question_id") for q in questions], "survey.questions")
        for index, q in enumerate(questions, 1):
            where = f"survey.questions[{index}]"
            self.require_keys(
                q,
                ("question_id", "text", "type", "construct_measured", "required"),
                where,
            )
            if not q.get("construct_measured"):
                self.error(f"{where}.construct_measured must be non-empty")
            if q.get("type") == "likert":
                scale = q.get("scale")
                if not isinstance(scale, dict) or not scale.get("low") or not scale.get("high"):
                    self.error(f"{where} likert scale requires low/high endpoints")
            if q.get("type") in ("single-choice", "multi-select", "ranking"):
                if not isinstance(q.get("options"), list) or not q.get("options"):
                    self.error(f"{where} requires non-empty options")
        if len(question_map) != len(questions):
            self.error("every survey question requires a unique question_id")

    def wf2a(self):
        _, _, question_ids = self.survey_context()
        data, archetypes = self.archetype_context()
        if not isinstance(data, dict):
            return
        self.require_keys(data, ("research_question", "target_population", "note", "simulation_plan", "archetypes"), "archetypes.json")
        items = data.get("archetypes", [])
        self.unique([item.get("archetype_id") for item in items], "archetypes")
        if not 5 <= len(items) <= 8:
            self.warn(f"archetype count is {len(items)}; recommended range is 5-8")
        weights = []
        forbidden = {"预期回答倾向", "预期影响construct", "likely_behavior", "answer_implications"}
        for aid, item in archetypes.items():
            where = f"archetype {aid}"
            self.require_keys(item, ("name", "核心特征", "scenario_weight", "weight_source", "变量设定", "候选机制线索"), where)
            weight = item.get("scenario_weight")
            if isinstance(weight, (int, float)):
                weights.append(weight)
            else:
                self.error(f"{where}.scenario_weight must be numeric")
            source = item.get("weight_source")
            self.require_keys(source, ("type", "detail"), f"{where}.weight_source")
            for variable in item.get("变量设定", []):
                self.require_keys(variable, ("类型", "变量", "取值", "来源"), f"{where}.变量设定")
                unknown = set(variable.get("来源", [])) - question_ids
                if unknown:
                    self.error(f"{where} references unknown question ids: {sorted(unknown)}")
            if self.contains_key(item, forbidden):
                self.error(f"{where} contains forbidden prediction fields")
        if weights and abs(sum(weights) - 1.0) > 0.001:
            self.error(f"scenario_weight sum is {sum(weights):.4f}, expected 1.0")
        plan = data.get("simulation_plan")
        self.require_keys(plan, ("mode", "variants_per_archetype", "simulation_n", "weight_interpretation"), "simulation_plan")

    def wf2b(self):
        _, archetypes = self.archetype_context()
        _, question_map, _ = self.survey_context()
        data, mechanisms = self.mechanism_context()
        if not isinstance(data, dict):
            return
        self.require_keys(data, ("questionnaire_domains", "mechanisms", "archetype_mechanism_map", "note"), "behavior_mechanisms.json")
        self.unique(list(mechanisms), "mechanisms")
        for mid, item in mechanisms.items():
            where = f"mechanism {mid}"
            self.require_keys(item, ("name", "domain", "applicable_archetypes", "affects_questions", "logic", "need_reading", "evidence", "scrutiny"), where)
            self.require_keys(item.get("logic"), ("theory_basis", "mechanism_logic"), f"{where}.logic")
            self.require_keys(item.get("need_reading"), ("surface_need", "hypothesized_latent_motive", "demand_authenticity"), f"{where}.need_reading")
            self.require_keys(item.get("evidence"), ("level", "note", "plausibility"), f"{where}.evidence")
            self.require_keys(item.get("scrutiny"), ("scope", "alternative_explanation", "falsification_probe"), f"{where}.scrutiny")
            unknown_a = set(item.get("applicable_archetypes", [])) - set(archetypes)
            unknown_q = set(item.get("affects_questions", [])) - set(question_map)
            if unknown_a:
                self.error(f"{where} references unknown archetypes: {sorted(unknown_a)}")
            if unknown_q:
                self.error(f"{where} references unknown questions: {sorted(unknown_q)}")
            evidence = item.get("evidence", {})
            needs = item.get("need_reading", {})
            if evidence.get("level") == "model-inference":
                if evidence.get("plausibility") == "supported":
                    self.error(f"{where}: model-inference cannot be supported")
                if "real_need" in needs.get("demand_authenticity", []):
                    self.error(f"{where}: model-inference cannot claim real_need")
        mapping = data.get("archetype_mechanism_map", {})
        if set(mapping) != set(archetypes):
            self.error("archetype_mechanism_map must cover every archetype exactly")
        for aid, mids in mapping.items():
            unknown = set(mids) - set(mechanisms)
            if unknown:
                self.error(f"archetype {aid} maps unknown mechanisms: {sorted(unknown)}")

    def wf2c(self):
        _, archetypes = self.archetype_context()
        _, mechanisms = self.mechanism_context()
        _, question_map, _ = self.survey_context()
        data = self.json_file("task_frictions.json")
        if not isinstance(data, dict):
            return
        self.require_keys(data, ("task_scope", "friction_dimensions", "archetype_friction_map", "question_context_coverage", "note"), "task_frictions.json")
        dimensions = {
            item.get("dimension_id"): item
            for item in data.get("friction_dimensions", [])
            if isinstance(item, dict)
        }
        self.unique(list(dimensions), "friction_dimensions")
        forbidden = {"score", "scores", "top_friction", "top_friction_dimensions", "question_friction_rules", "likely_pain_answer_pattern"}
        if self.contains_key(data, forbidden):
            self.error("task_frictions.json contains forbidden answer-direction fields")
        mapping = data.get("archetype_friction_map", {})
        if set(mapping) != set(archetypes):
            self.error("archetype_friction_map must cover every archetype exactly")
        for aid, entry in mapping.items():
            relevant = entry.get("relevant_dimensions", {}) if isinstance(entry, dict) else {}
            for fid, context in relevant.items():
                if fid not in dimensions:
                    self.error(f"archetype {aid} references unknown friction dimension {fid}")
                self.require_keys(context, ("drivers", "mechanism_ids", "affects_questions", "confidence"), f"archetype {aid}.{fid}")
                if not context.get("drivers"):
                    self.error(f"archetype {aid}.{fid} requires observable drivers")
                if set(context.get("mechanism_ids", [])) - set(mechanisms):
                    self.error(f"archetype {aid}.{fid} references unknown mechanisms")
                if set(context.get("affects_questions", [])) - set(question_map):
                    self.error(f"archetype {aid}.{fid} references unknown questions")
        task_qids = {
            qid for qid, q in question_map.items()
            if q.get("construct_measured") in TASK_CONSTRUCTS or q.get("type") in ("ranking", "open")
        }
        coverage = data.get("question_context_coverage", {})
        missing = task_qids - set(coverage)
        if missing:
            self.error(f"question_context_coverage missing task questions: {sorted(missing)}")
        hypotheses = self.json_file("hypotheses.json")
        if not isinstance(hypotheses, dict):
            return
        self.require_keys(hypotheses, ("created_before_simulation", "status", "note", "hypotheses"), "hypotheses.json")
        if hypotheses.get("created_before_simulation") is not True or hypotheses.get("status") != "sealed":
            self.error("hypotheses.json must be created_before_simulation=true and status=sealed")
        items = hypotheses.get("hypotheses", [])
        self.unique([item.get("hypothesis_id") for item in items], "hypotheses")
        for item in items:
            self.require_keys(item, ("hypothesis_id", "target_questions", "predicted_pattern", "basis", "alternative_explanation", "falsification_rule", "confidence"), f"hypothesis {item.get('hypothesis_id')}")

    def wf3(self):
        _, archetypes = self.archetype_context()
        _, mechanisms = self.mechanism_context()
        data = self.jsonl_file("respondents.jsonl")
        meta = self.json_file("respondents_meta.json")
        if data is None or not isinstance(meta, dict):
            return
        ids = [row.get("respondent_id") for row in data]
        self.unique(ids, "respondents")
        forbidden = {"task_friction_profile", "score", "scores", "top_friction", "top_friction_dimensions", "answer_implications", "likely_pain_answer_pattern", "predicted_pattern", "hypothesis_id"}
        by_arch = defaultdict(list)
        for row in data:
            rid = row.get("respondent_id")
            aid = row.get("archetype_id")
            self.require_keys(row, ("respondent_id", "archetype_id", *FIVE_LAYERS, "mechanism_trace"), f"respondent {rid}")
            if aid not in archetypes:
                self.error(f"respondent {rid} references unknown archetype {aid}")
            if any(not isinstance(row.get(layer), dict) or not row.get(layer) for layer in FIVE_LAYERS):
                self.error(f"respondent {rid} has an empty persona layer")
            trace = row.get("mechanism_trace", {})
            self.require_keys(trace, ("mechanism_ids", "individual_expression"), f"respondent {rid}.mechanism_trace")
            if set(trace.get("mechanism_ids", [])) - set(mechanisms):
                self.error(f"respondent {rid} references unknown mechanisms")
            duplicated = {"surface_need", "hypothesized_latent_motive", "demand_authenticity", "mechanism_evidence"} & set(trace)
            if duplicated:
                self.error(f"respondent {rid}.mechanism_trace duplicates mechanism fields: {sorted(duplicated)}")
            if self.contains_key(row, forbidden):
                self.error(f"respondent {rid} contains forbidden prediction fields")
            by_arch[aid].append(row)
        self.require_keys(meta, ("count", "simulation_n", "by_archetype", "allocation", "confidence", "anti_pattern_checks", "note"), "respondents_meta.json")
        if meta.get("count") != len(data) or meta.get("simulation_n") != len(data):
            self.error("respondents_meta count/simulation_n must equal JSONL row count")
        if sum(meta.get("by_archetype", {}).values()) != len(data):
            self.error("respondents_meta.by_archetype must sum to row count")

    def wf4(self):
        respondents = self.jsonl_file("respondents.jsonl")
        responses = self.jsonl_file("responses.jsonl")
        meta = self.json_file("responses_meta.json")
        _, mechanisms = self.mechanism_context()
        _, question_map, _ = self.survey_context()
        if respondents is None or responses is None or not isinstance(meta, dict):
            return
        respondent_ids = {row.get("respondent_id") for row in respondents}
        response_ids = [row.get("respondent_id") for row in responses]
        self.unique(response_ids, "responses")
        if set(response_ids) != respondent_ids:
            self.error("responses must correspond one-to-one with respondents")
        forbidden = {
            "hypothesis_id",
            "predicted_pattern",
            "task_friction_profile",
            "score",
            "scores",
            "top_friction",
            "surface_reason",
            "hypothesized_latent_motive",
            "demand_authenticity",
            "mechanism_evidence",
        }
        for row in responses:
            rid = row.get("respondent_id")
            answers = row.get("answers", [])
            answer_map = {answer.get("question_id"): answer for answer in answers if isinstance(answer, dict)}
            if set(answer_map) != set(question_map):
                self.error(f"respondent {rid} answers do not cover every survey question")
            if self.contains_key(row, forbidden):
                self.error(f"response {rid} contains forbidden prediction fields")
            for qid, answer in answer_map.items():
                q = question_map[qid]
                value = answer.get("answer")
                uncertain = answer.get("uncertain") is True
                if not uncertain:
                    if q.get("type") in ("likert", "rating", "nps") and not isinstance(value, (int, float)):
                        self.error(f"response {rid}/{qid} requires numeric answer")
                    if q.get("type") == "single-choice" and value not in q.get("options", []):
                        self.error(f"response {rid}/{qid} is not a declared option")
                    if q.get("type") in ("multi-select", "ranking") and not isinstance(value, list):
                        self.error(f"response {rid}/{qid} requires a list answer")
                if q.get("construct_measured") in RESULT_CONSTRUCTS | TASK_CONSTRUCTS or q.get("type") == "open":
                    if not answer.get("reasoning"):
                        self.error(f"response {rid}/{qid} requires reasoning")
                mid = answer.get("mechanism_id")
                if mid and mid not in mechanisms:
                    self.error(f"response {rid}/{qid} references unknown mechanism {mid}")
        self.require_keys(meta, ("count", "blinding", "quality", "invalid_patterns_detected", "note"), "responses_meta.json")
        if meta.get("count") != len(responses):
            self.error("responses_meta.count must equal responses row count")
        blinding = meta.get("blinding", {})
        if blinding.get("hypotheses_loaded") is not False or blinding.get("task_frictions_loaded") is not False:
            self.error("responses_meta.blinding must record hypotheses/task_frictions as not loaded")
        if blinding.get("level") == "procedural" and meta.get("quality", {}).get("overall") == "high":
            self.error("procedural blinding cannot have high overall quality")

    def wf5(self):
        stats = self.json_file("stats.json")
        report_path = self.run / "report.md"
        if isinstance(stats, dict):
            self.require_keys(stats, ("total_n", "by_archetype", "per_question", "cross_tabs_by_archetype", "note"), "stats.json")
        if not report_path.exists():
            self.error(f"missing required file: {report_path}")
            return
        text = report_path.read_text(encoding="utf-8")
        for marker in ("合成样本", "仅供预调研", "这批人整体怎么想", "我们当初的猜测对不对", "这份报告能信多少"):
            if marker not in text:
                self.error(f"report.md missing required marker: {marker}")

    def run_stage(self, stage):
        getattr(self, stage)()


def main():
    parser = argparse.ArgumentParser(description="Validate design-flow run artifacts")
    parser.add_argument("run_dir", help="runs/<timestamp>/ directory")
    parser.add_argument("--stage", choices=(*STAGES, "all"), default="all")
    args = parser.parse_args()

    validator = Validator(args.run_dir)
    stages = STAGES if args.stage == "all" else (args.stage,)
    for stage in stages:
        validator.run_stage(stage)

    for warning in validator.warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    if validator.errors:
        for error in validator.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"validation failed: {len(validator.errors)} error(s)", file=sys.stderr)
        return 1
    print(f"validation passed: {args.stage}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
