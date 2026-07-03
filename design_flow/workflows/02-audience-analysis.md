# Workflow 2：人群分析 (audience-analysis)

把问卷变成可进入模拟的人群依据，连续执行三个 Phase：

- Phase A 人群反推：输出 `archetypes.json`
- Phase B 行为机制映射：输出 `behavior_mechanisms.json`
- Phase C 任务情境映射：输出 `task_frictions.json` 与封存的 `hypotheses.json`

三个 Phase 共用一个 workflow 文件。内部验收通过时自动推进；任一 Phase 触发 Stop 条件才回退。Phase C 完成后通过 audience package 门禁一次性展示全部产出并确认最终 `simulation_n`。

## When to use

`survey.json` 已就绪，需要推导谁会答得不同、这种差异可能由什么机制解释、哪些任务情境必须写进 persona。

不适用：`survey.json` 不存在或题目缺 `construct_measured`，先回 WF1。

## 输入

- `runs/<时间戳>/survey.json`
- Phase B 按需读取 `references/behavior-mechanism-library.md`
- Phase C 按需读取 `references/task-friction-framework.md`

---

## Phase A：人群反推

### 目标

从每题的 `construct_measured` 反推“哪些输入变量会让回答不同”，形成待机制校验的最小原型集合。原型不是人口统计属性的排列组合。

### 方法

逐题判断差异来自哪类输入：

| 类型 | 含义 | 例 |
|---|---|---|
| 经验 | 是否做过、是否遇过 | 做过真实调研、退换货踩坑 |
| 情境 | 当前处境与压力 | deadline、短租、导师要求 |
| 心理 | 倾向与风险判断 | AI 信任、风险偏好 |
| 资源 | 可调用的渠道与预算 | 社交资源、预算、空间 |
| 能力 | 熟练度与理解力 | 研究方法、空间规划能力 |

每个变量追溯到至少一个 `question_id`。满意度、使用意愿、推荐意愿、付费意愿是结果变量，不能定义原型，也不能出现“预期回答倾向”等方向字段。

候选原型通常收敛到 5–8 类。保留条件：

1. 能解释同一道题为何会答得不同。
2. 经验、限制与资源之间自洽。
3. 能在 Phase B 形成连贯、可证伪的机制。

每个原型记录 2–4 个候选机制线索，供 Phase B 合并、删除或重写。

### 场景覆盖计划

`scenario_weight` 只分配合成变体，不代表现实比例，合计 1.0。来源只能是：

- `real-data`：用户提供可核验数据
- `user-specified`：用户主动指定
- `coverage-default`：无依据时等权覆盖
- `model-assumption`：明确标注的压力测试假设

`simulation_plan.mode=coverage`，默认每个 archetype 至少 3 个变体。Phase A 按“原型数 × 每类变体数”生成 proposed plan，但不在这里询问用户；最终规模在 Phase C 后只确认一次。

### 输出合同

`archetypes.json` 顶层包含：

- `research_question`、`target_population`、`note`
- `simulation_plan`
- `archetypes[]`

每个 archetype 包含 `archetype_id`、`name`、`核心特征`、`scenario_weight`、`weight_source`、`变量设定[]`、`候选机制线索[]`。完整示例按需读取 `references/output-examples.md`。

### 完成前确认

先运行：

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_run.py" runs/<时间戳>/ --stage wf2a
```

再判断权重语义是否诚实、原型是否自洽、是否真的会影响回答。通过后自动进入 Phase B。

### Stop

- 问卷缺 `construct_measured`：回 WF1。
- 无法形成有意义的输入差异：回 WF1 补构念或题目。
- 目标人群与研究问题矛盾：追问用户。

---

## Phase B：行为机制映射

### 目标

给每个原型建立“可检验的合理性”，说明为什么值得纳入模拟，以及什么真实观察会推翻解释。机制不证明人群存在或现实比例。

### 方法

先根据问卷内容选择 domain，不能默认套技术接受模型：

`technology_tool_adoption`、`product_purchase`、`spatial_experience`、`visual_aesthetic_preference`、`service_participation`、`public_social_design`、`habit_lifestyle_change`、`need_expression`、`survey_response_behavior`。

从 Phase A 的候选线索出发，读取机制库并走完：

`环境/事件 → 社会处境 → 资源/能力限制 → 行为机制 → 表层需求 → 假设性潜在动机`

走不完、不会影响回答、场景不自洽或与其他类型重复的原型，回 Phase A 合并、删除或重写。

### 证据纪律

- `user-evidence`：指向用户提供的访谈、观察或真实问卷
- `cited-research`：有可核验来源
- `model-inference`：仅依据问卷、机制库与模型推理

`plausibility` 使用 `supported`、`plausible`、`speculative`。`model-inference` 最高只能是 `plausible`，且 `demand_authenticity` 不能含 `real_need`。

每个机制必须包含有竞争力的 `alternative_explanation` 和可执行的 `falsification_probe`。文件不写逐题答案、结果方向或 `answer_implications`。

### 输出合同

`behavior_mechanisms.json` 包含：

- `questionnaire_domains`
- `mechanisms[]`：顶层 id/domain/适用对象/相关题目，以及 `logic`、`need_reading`、`evidence`、`scrutiny`
- `archetype_mechanism_map`
- 合成样本边界 `note`

完整示例按需读取 `references/output-examples.md`。

### 完成前确认

先运行：

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_run.py" runs/<时间戳>/ --stage wf2b
```

再判断 domain 路由、因果链、竞争解释与证伪条件是否合理。通过后自动进入 Phase C。

### Stop

- 某个 archetype 无法形成连贯、可证伪的机制：回 Phase A 修改或删除。
- 问卷过泛，无法判断行为域：回 WF1 补研究问题或构念。

---

## Phase C：任务情境映射

### 目标

把机制落到具体任务环节，整理会影响痛点、排序、优先级、使用边界和开放题回答的可观察经历、资源、能力与环境限制。它为 WF3 提供人物故事素材，不为 WF4 生成答案规则。

### 方法

先定义任务范围，例如家具选购可拆成：

`发现需求 → 测量/规划 → 风格与质量判断 → 下单 → 配送安装 → 售后`

再映射稳定维度，如 `time_effort`、`cognitive_load`、`risk_safety`、`money_loss`、`space_environment`、`identity_control`、`social_coordination`、`maintenance_aftercare`、`habit_disruption`。

每个 archetype 的 relevant dimension 只记录：

- `drivers`：可写进 persona 的具体事实
- `mechanism_ids`
- `affects_questions`
- `confidence`

不要写分数、top friction、答案阈值或排序规则。`question_context_coverage` 只说明一道任务型题需要哪些维度和 persona 输入。

强弱排序与 archetype 间的预测差异只写入 `hypotheses.json`。该文件必须在模拟前设为 `status=sealed`；WF3/WF4 不读取，不把 `predicted_pattern` 同义改写到 persona，结果不符合预测时也不重生成。

### 输出合同

`task_frictions.json` 包含：

- `task_scope`
- `friction_dimensions[]`
- `archetype_friction_map`
- `question_context_coverage`
- 合成样本边界 `note`

`hypotheses.json` 包含 `created_before_simulation=true`、`status=sealed`，以及每条假设的目标题、比较对象、预测、依据、替代解释、证伪规则和置信度。完整示例按需读取 `references/output-examples.md`。

### 完成前确认

先运行：

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_run.py" runs/<时间戳>/ --stage wf2c
```

再判断 drivers 是否可观察、情境覆盖是否充分、预测是否可证伪。

通过后展示完整 audience package：全部原型、机制、任务情境、三阶段验收结果，以及 archetype 数、基础覆盖量、用户此前预算偏好和建议 `simulation_n`。用户只在这里确认一次最终规模；确认后更新 `simulation_plan`。

### Stop

- 没有行为、痛点或任务题：回 WF1。
- 某 archetype 缺少可观察 drivers：回 Phase A/B。
- audience package 尚未确认最终 `simulation_n`：不进入 WF3。

## 跨 Phase 红线

- Phase A 原型只是候选，Phase B 可以要求回退、合并或删除。
- `model-inference` 不得升级为 `supported`。
- 结果变量不作背景；场景权重不解释为现实比例。
- `hypotheses.json` 在 WF5 前保持封存。

## 下一步

确认 audience package 后进入 `workflows/03-persona-generation.md`。WF3 读取 `archetypes.json`、`behavior_mechanisms.json`、`task_frictions.json`，不得读取 `hypotheses.json`。
