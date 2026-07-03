# Test Strategy

## What we test

`design-flow` 是 Markdown skill + 一个 python3 脚本。测试分两层：脚本验证 + skill 验收清单（可机械检查）。

### scripts/analyze.py（确定性脚本）

已用合成 fixture 测过（3 受访者 / 2 archetype / 全题型含 uncertain）：count / mean / median / 分布 / 交叉表 / ranking 平均排名 / uncertain 排除 均正确。回归检查：改脚本后重跑该 fixture 对比 `stats.json`。

fixture 放 `runs/test/`（gitignore，不入库），重跑：

```bash
# 重建 fixture 后
python3 scripts/analyze.py runs/test/
python3 -m json.tool runs/test/stats.json
```

未来可加 `tests/test_analyze.py`（pytest，离线），当脚本复杂化或出现第二个脚本时引入。

### Acceptance Criteria（每步验收，可机械检查）

**WF1 survey.json**：合法 JSON；含 `research_question` / `target_population` / `purpose` / `simulation_n` / `simulation_n_rationale` / `questions`；`simulation_n` 为正整数或 null，且 rationale 明确它不代表抽样精度；每题 `question_id` 唯一 + `construct_measured` 非空；likert 题 `scale` 含 `low` / `high`；options 互斥穷尽；题序 筛选→行为→态度→开放；题数 ≤ 15、分钟 ≤ 5。

**WF2 archetypes.json**：原型 5-8；`archetype_id` 唯一；含 `simulation_plan`；`scenario_weight` 合计 = 1.0；每个权重有 `weight_source.type/detail`，无真实依据时为 `coverage-default` 等权；每原型 `变量设定` 含类型（五类）/ 变量 / 取值 / 来源（`question_id` 可追溯）；变量类型不含结果构念；每原型有 `候选机制线索`；文件不含 `预期回答倾向` / `预期影响construct` 或其他结果方向。

**WF2.5 behavior_mechanisms.json**：合法 JSON；含 `questionnaire_domains` / `mechanisms` / `archetype_mechanism_map`；每机制含 `logic`（`theory_basis` + `mechanism_logic`）/ `need_reading`（`surface_need` + `hypothesized_latent_motive` + `demand_authenticity`）/ `evidence`（`level` + `note` + `plausibility`）/ `scrutiny`（`scope` + `alternative_explanation` + `falsification_probe`）四组，及顶层 `mechanism_id` / `name` / `domain` / `applicable_archetypes` / `affects_questions`；`affects_questions` 可追溯到问卷；每个 archetype 至少被一个机制覆盖；`evidence.level=model-inference` 时 `evidence.plausibility` 不得为 `supported`，`need_reading.demand_authenticity` 不得含 `real_need`；不含旧平铁字段 `trigger_environment` / `actor_conditions` / `evidence_detail` / `source_refs` / `inclusion_reason` / `exclusion_boundary`，也不含旧字段 `latent_motive` / `confidence` / `validation_probe` / `likely_behavior` / `answer_implications`；非技术问卷不能默认全用 TAM/UTAUT；`note` 含"合成样本"+"预调研"。

**WF2.6 task_frictions.json + hypotheses.json**：`task_frictions.json` 含 `task_scope` / `friction_dimensions` / `archetype_friction_map` / `question_friction_rules`；每个 archetype 被覆盖；每个 score 在 1-5 且含 drivers / mechanism_ids / affects_questions / confidence；所有痛点/排序/开放/使用边界题有规则；不得从性格直接推痛点；不含 `likely_pain_answer_pattern`。`hypotheses.json` 在模拟前写入，含 `created_before_simulation=true` / `status=sealed`，每条假设有目标题、预测、依据、替代解释、证伪规则和置信度。

**WF3 respondents.jsonl + meta**：每行合法 JSON 含 `respondent_id` 唯一 + `archetype_id` 可追溯 + 五层 + `mechanism_trace` + `task_friction_profile`；`mechanism_ids` 可追溯到 WF2.5；`mechanism_trace` 使用 `hypothesized_latent_motive`，并在 `mechanism_evidence` 中逐个继承对应机制的 `evidence.level` / `evidence.plausibility`（作为 `level` / `plausibility`），不得升级；`top_friction_dimensions` 可追溯到 WF2.6；五层均非空；同 archetype 下任意两体 ≥ 3 维不同；行数 = `simulation_n`、每类达到基础覆盖、`by_archetype` 合计 = 行数；五层不含结果构念键；不含 `answer_implications` / `likely_pain_answer_pattern` 或 hypothesis 内容；meta 含 `count` / `simulation_n` / `allocation` / `by_archetype` / `confidence.scenario_coverage` / `anti_pattern_checks` / `note`，不含把 N 当研究证据的 `sample_size` 评分；`note` 含"合成样本"+"预调研"。

**WF4 responses.jsonl + meta**：每行含 `respondent_id`（一一对应 respondents）+ `answers`；`answers` 覆盖 survey 所有题；answer 强类型（likert int 量程内 / single-choice 在 options 内）；关键题有 `reasoning`，并能追溯到 `mechanism_trace` 或明确的 survey-response 机制；如记录潜在动机只能使用 `hypothesized_latent_motive`，不得写成事实；痛点/排序/功能优先级/开放题能追溯到 `task_friction_profile`；不含 hypothesis id 或预测内容；无直线作答 / 全 uncertain；meta 含 `count` / `blinding` / `quality` / `invalid_patterns_detected` / `note`；`blinding.hypotheses_loaded=false`，无法隔离上下文时标记 `level=procedural` 且 overall 不为 high；`note` 含"合成样本"+"预调研"。

**WF5 stats.json + report.md**：`stats.json` 含 `total_n` / `per_question` / `cross_tabs_by_archetype`；`report.md` 含 7 章节；报告头部含"合成样本"+"预调研"+合成记录数+场景覆盖质量；列出权重来源并声明不代表真实比例；每条开放观察贴 source id 且覆盖全部 `respondent_id`；单源模式有标记；每统计结论附有效合成记录数 n；报告含"机制与任务摩擦解释"与"需真实用户验证的假设"段；逐条对照封存假设并标记 `supported / not_supported / inconclusive`。

### Pipeline 手动 QA 场景

| # | 场景 | 期望 |
|---|---|---|
| 1 | 给研究问题跑 run-pipeline 全链 | 7 步产出齐全、步间暂停、report.md 区分模拟 / 机制与任务摩擦解释 / 假设 |
| 2 | WF1 给烂问卷（双重题） | 验收拦下、要求修订 |
| 3 | WF2 把"使用意愿"塞进变量设定 | 红线触发、拒绝 |
| 4 | WF3 同 archetype 个体复制 | anti-pattern elastic 拦下、重生成 |
| 5 | WF4 全 uncertain 作答 | `no_invalid_responding` 降级 |
| 6 | WF5 LLM 自算统计而非调脚本 | 拦下、要求走 `analyze.py` |
| 7 | 非技术问卷 WF2.5 默认套 TAM/UTAUT | 拦下，要求按 domain 路由机制 |
| 8 | WF2 原型没有机制支撑 | WF2.5 要求删除、合并或重写，不能进 WF3 |
| 9 | WF2 把所有可能组合都纳入 | 拦下，要求只保留有机制链且影响回答的类型 |
| 10 | WF4 对“哪个环节更麻烦”只按性格作答 | 拦下，要求先有 WF2.6 摩擦分数与 drivers |
| 11 | 问卷只有“是否愿意”没有痛点/任务题 | 回 WF1 重写问卷，不能进入 WF2.6 |
| 12 | WF3 / WF4 读取 `hypotheses.json` 或复制预测方向 | 拦下；清除预测字段后重新生成，WF5 前保持封存 |
| 13 | 模拟结果不支持预注册假设 | 保留原结果，WF5 标记 `not_supported` 或 `inconclusive`，不得重生成 |
| 14 | WF2 没有真实分布依据却给出不等权“现实比例” | 拦下；改用 `coverage-default` 等权，或要求明确标注用户设定/模型假设 |
| 15 | WF5 把模拟百分比解释为目标总体发生率 | 拦下；改写为本次合成场景内模式并声明不可外推 |
| 16 | WF2.5 只套理论卡片就标 `supported` | 拦下；改为 `model-inference` + `plausible/speculative`，补替代解释与证伪条件 |
| 17 | 报告把假设性潜在动机写成受访者事实 | 拦下；改用“可能解释/待验证”，并显示证据等级 |
| 18 | run-pipeline 每步暂停时只给验收结果、不给完整产出 | 拦下；要求先完整展示该步产出（超 20 条允许降级展示但须声明） |
| 19 | WF1 用户未提模拟规模，问卷直接定稿 | 拦下；要求主动问打算生成多少条合成记录 |
| 20 | WF2 Phase A 算出建议 `simulation_n` 后直接写入 archetypes.json | 拦下；要求先报出建议值问用户确认 |

### 回归检查（发布前）

1. 跑隐私扫描（见下）
2. 重跑 `analyze.py` 合成 fixture 对比 `stats.json`
3. 确认根 SKILL ≤ ~200 行
4. 确认 7 个 workflow 验收标准仍可机械检查
5. 确认安装目录名为 `design-flow`（kebab），与 skill `name` 一致（带空格的目录名会触发 linter 警告；改名会改 cwd，在会话停顿点做）

## 隐私扫描（发布前必跑）

```bash
rg -n "op://|sk-[a-zA-Z0-9]{10,}|/Users/" .
```

扫描 1Password 引用（`op://`）、API key 风格串（`sk-` + 10+ 字符）、绝对用户路径（`/Users/`）。任何匹配都是红线。本命令会在 `AGENTS.md` 与 `docs/test.md` 自匹配（命令本身含 `op://` 与 `/Users/`），忽略这两处。`rg` 默认跳过 gitignore 文件，故 `reference-docs/`、`构建路线图.md`、`runs/` 不扫。本 skill 无 env 变量，故无 `.env.example`；示例 persona / 数据集必须虚构合成。

## What we don't test (yet)

- CI 自动化（skill 主体是 Markdown，无 build）
- LLM 作答质量的客观回归（需真实对照样本，本工具定位预调研，不强求）
