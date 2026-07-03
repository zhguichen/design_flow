# Workflow 3：Persona 生成 (persona-generation)

把通过机制校验和任务摩擦校验的人群原型，按场景覆盖计划展开成具体的模拟受访者。每个受访者带五层信息结构、`mechanism_trace` 与 `task_friction_profile`，同类下的个体必须有差异——不能复制粘贴出来凑数。

按需从根 `SKILL.md` 加载。依赖 WF2 (`02-audience-analysis.md`) 产出的 `archetypes.json`、`behavior_mechanisms.json` 与 `task_frictions.json`。

## When to use

- `archetypes.json`、`behavior_mechanisms.json` 与 `task_frictions.json` 已就绪，需要生成具体合成受访者。
- `archetypes.json` 已含 `simulation_plan`，或用户需要调整模拟计算预算。
- WF2 完成后由 pipeline 推进。

不适用：缺 `archetypes.json` → 回 WF2 Phase A；缺 `behavior_mechanisms.json` → 回 WF2 Phase B；缺 `task_frictions.json` → 回 WF2 Phase C。

## 输入

- `runs/<时间戳>/archetypes.json`：原型 + `scenario_weight` + `weight_source` + `simulation_plan`。
- `runs/<时间戳>/behavior_mechanisms.json`：机制的 `logic`/`need_reading`/`evidence`/`scrutiny`。
- `runs/<时间戳>/task_frictions.json`：任务摩擦维度、分数、drivers、题目作答规则。
- `runs/<时间戳>/survey.json`：上下文（`construct_measured`、`target_population`）。
- `simulation_n`：合成记录数，优先用 `simulation_plan.simulation_n`；用户可调整，但不能低于基础场景覆盖要求。

即使同目录已存在 `hypotheses.json`，本步也不读取或复制其中的预测方向——那是留给 WF5 首次打开的封存文件。

## 方法

### 先把因果链读透，再展开个体

读 `behavior_mechanisms.json` 的 `archetype_mechanism_map`，找出每个 archetype 的机制。五层信息必须从这条链长出来：

`环境/事件 → 社会处境 → 资源/能力限制 → 行为机制 → 表层需求 → 假设性潜在动机`

不能只按年龄、专业、城市随机扩写；也不能把结果变量塞进五层当背景——那是 WF2 定的红线，这里继承。

再读 `task_frictions.json` 的 `archetype_friction_map`，找出每个 archetype 的任务摩擦。个体的痛点相关字段要从这条链长出来：

`任务场景 → 当前行为 → 环境限制 → 资源/能力 → 行为机制 → 摩擦维度 → 可能痛点答案`

同一 archetype 下允许轻微变体（相邻摩擦维度交换、score 4/5 微调），但不能把低分摩擦写成最高痛点。

### 按场景覆盖计划分配，权重只管额外变体投向

先读 `simulation_plan`，每个 archetype 至少分配 `variants_per_archetype` 个体。若 `simulation_n` 高于基础覆盖量，按 `scenario_weight` 分配余量并补齐取整误差，`by_archetype` 记录实际分配。`scenario_weight` 只控制额外变体投向，不代表现实中该类人占多少——报告不能把 `by_archetype / simulation_n` 当成目标人群构成来解释。

### 同类下个体必须有真实差异

同一 archetype 下的个体不能复制粘贴。任意两个体至少在 3 个维度上不同，可以从这些维度变化：专业方向 / 年级 / 学校类型 / 时间压力 / 经济条件 / AI 信任度 / 社交资源 / 方法论意识 / 作答认真度。同类个体共享该原型的核心特征与变量设定，但在这些维度上各自不同——否则 WF4 模拟出来的答案会是同一份文本的复制品，统计上的"差异"就是假的。

### Anti-pattern 自检

这几个失败模式在合成人群生成里特别常见，改编自 persona 方法论。任何一条不过就重生成，不放过：

| anti-pattern | 在合成场景的表现 | 检查 |
|---|---|---|
| Elastic（弹性） | 同类下个体雷同、或一个 persona 啥都包含 | 同 archetype 下任意两个体 ≥3 维不同 |
| Demographic-only（纯人口统计） | 五层只有基础身份有内容 | 社会处境 / 心理倾向 / 行为习惯 / 作答风格 均非空 |
| Ideal user（理想用户） | 全是认真、高信任、高资源的好用户 | 含保守 / 怀疑 / 资源不足等反面个体 |
| Committee（委员会拼凑） | 一个个体塞矛盾特征凑数 | 个体内部特征自洽 |
| Stale（过期） | 未标生成时间 | meta 含 `generated_at`（或由 `runs/<时间戳>` 体现） |

### 置信度反映模拟质量，不是研究效度

`Confidence = (场景覆盖分 + 数据质量分 + 一致性分) / 3`，各维 low / medium / high：

- **场景覆盖分**：每个有效 archetype 至少 3 个差异化变体 → high；每类 2 个 → medium；任一类只有 1 个或缺失 → low。只评估情景覆盖，不评估总体代表性。
- **数据质量分**：看 persona 完整度（五层齐）+ 个体差异度（同类不复制）。单源 LLM 生成本身是个局限，这一维**封顶 medium**（除非未来引入多源交叉，本 pipeline 暂无）。
- **一致性分**：persona 背景设定、`mechanism_trace`、`task_friction_profile` 与 archetype 的因果属性不矛盾 → high；有矛盾 → low。

`overall` 是三者综合，`rationale` 写明理由。这个置信度反映的是**模拟质量与场景覆盖**（人像不像、答案会不会一致、每类有没有变体），**不等于研究效度或总体代表性**——增加 `simulation_n` 不会增加真实证据，必须在 `meta.note` 和 WF5 报告里显式声明。

## 输出

写两个文件：

**`runs/<时间戳>/respondents.jsonl`** — 每行一个受访者：

```jsonl
{"respondent_id":"R001","archetype_id":"A1","基础身份":{"年级":"大三","专业":"环艺","学校类型":"普通本科","城市":"二线","经济条件":"中等"},"社会处境":{"时间压力":"高","导师要求":"严格","社交资源":"少","当前任务阶段":"毕设中期"},"心理倾向":{"AI信任":"中高","焦虑程度":"中","风险偏好":"中低","认真程度":"高","从众倾向":"中"},"行为习惯":{"找资料方式":"小红书+同学","作业习惯":"临 deadline 赶","是否用AI":"是","发问卷方式":"同学互填"},"作答风格":{"认真度":"高","是否会选不确定":"是","价格敏感度":"高","是否会承认不了解":"是"},"mechanism_trace":{"mechanism_ids":["M1","M3"],"surface_need":"提高调研效率","hypothesized_latent_motive":"缓解找不到受访者导致作业失败的压力","demand_authenticity":["surface_need","contextual_need","compensatory_need"],"mechanism_evidence":{"M1":{"level":"model-inference","plausibility":"plausible"},"M3":{"level":"model-inference","plausibility":"speculative"}}},"task_friction_profile":{"top_friction_dimensions":["F1","F3"],"scores":{"F1":5,"F2":3,"F3":4},"drivers":{"F1":["deadline","真实用户渠道不足"]}}}
{"respondent_id":"R002","archetype_id":"A1","基础身份":{...},...}
```

**`runs/<时间戳>/respondents_meta.json`** — 集合元数据 + 自评：

```json
{
  "count": 60,
  "simulation_n": 60,
  "generated_at": "2026-07-01",
  "by_archetype": {"A1": 18, "A2": 11, "A3": 12, "A4": 9, "A5": 7, "A6": 3},
  "allocation": {
    "mode": "coverage",
    "variants_per_archetype": 3,
    "weight_interpretation": "场景分配，不代表真实人群比例"
  },
  "confidence": {
    "scenario_coverage": "high",
    "data_quality": "medium",
    "consistency": "high",
    "overall": "medium",
    "rationale": "每个场景至少有 3 个差异化变体；单源 LLM 生成故数据质量中；背景与因果输入一致"
  },
  "anti_pattern_checks": {
    "elastic": "pass",
    "demographic_only": "pass",
    "ideal_user": "pass",
    "committee": "pass",
    "stale": "pass"
  },
  "note": "合成样本 / 仅供预调研 / 反映模拟质量不等于研究效度"
}
```

### 五层结构字段

| 层 | 字段示例 |
|---|---|
| 基础身份 | 年级 / 专业 / 学校类型 / 城市 / 经济条件 |
| 社会处境 | 时间压力 / 导师要求 / 社交资源 / 当前任务阶段 / 家庭支持 |
| 心理倾向 | AI 信任 / 焦虑程度 / 风险偏好 / 认真程度 / 从众倾向 |
| 行为习惯 | 找资料方式 / 作业习惯 / 是否用 AI / 发问卷方式 |
| 作答风格 | 认真度 / 是否会选不确定 / 价格敏感度 / 是否会承认不了解 |

结果变量（满意度 / 使用意愿 / 推荐意愿 / 付费意愿）**不**出现在五层里——它们是问卷要测的结果，不是 persona 背景。五层只设定影响结果的原因。

### mechanism_trace 字段

把五层信息追溯回 `behavior_mechanisms.json`：

| 字段 | 说明 |
|---|---|
| `mechanism_ids` | 该受访者继承的机制 id，必须存在于 `behavior_mechanisms.json` |
| `surface_need` | 受访者会说出口的表层需求 |
| `hypothesized_latent_motive` | 由机制推断的潜在动机假设，不是受访者事实 |
| `demand_authenticity` | 需求真实性假设标签，继承自机制的 `need_reading.demand_authenticity` |
| `mechanism_evidence` | 按 mechanism id 逐个继承对应机制 `evidence.level` / `evidence.plausibility`，不得升级 |

`mechanism_trace` 不含逐题答案、结果方向或 `hypotheses.json` 内容，只提供 WF4 可追溯的因果背景。

### task_friction_profile 字段

把痛点/麻烦环节/功能优先级追溯回 `task_frictions.json`：

| 字段 | 说明 |
|---|---|
| `top_friction_dimensions` | 该受访者最可能感到麻烦的任务摩擦维度 |
| `scores` | 维度分数，来自 `task_frictions.json`，可做轻微个体变体 |
| `drivers` | 推高摩擦分数的具体生活情境、行为经验、环境限制 |

这也不是逐题答案，让 WF4 在回答"哪个环节更麻烦"时依据具体摩擦分数与 drivers，而不是从性格直接猜。

## 完成前确认

- **id 双向可追溯**：`respondent_id` 唯一（`R001..RNNN`）；`archetype_id` 能在 `archetypes.json` 找到；`mechanism_trace.mechanism_ids` 能在 `behavior_mechanisms.json` 找到；`task_friction_profile.top_friction_dimensions` 能在 `task_frictions.json` 找到。
- **五层完整且不含结果变量**：社会处境/心理倾向/行为习惯/作答风格都非空（不是只有基础身份），且不含"满意度/使用意愿/推荐意愿/付费意愿"这类结果构念键。
- **同类个体强制差异**：同 `archetype_id` 下任意两个体至少 3 维不同，不是复制粘贴。
- **场景覆盖配额算对**：行数 = `simulation_plan.simulation_n`，`by_archetype` 合计 = 行数，每个 archetype 不少于 `variants_per_archetype`。
- **anti-pattern 自检通过**：上面五条逐一过一遍，不过就重生成。
- **meta 完整**：`respondents_meta.json` 含 `count`/`by_archetype`/`confidence`/`anti_pattern_checks`/`note`，`note` 含"合成样本"与"预调研"，且不把 `simulation_n` 包装成研究证据（不打 `sample_size` 分）。

## 该停下来问的情况

- 缺 `archetypes.json` / `behavior_mechanisms.json` / `task_frictions.json` 任一个 → 回对应的 WF2 Phase。
- `simulation_plan` 缺失 → 回 WF2 制定场景覆盖计划。
- `simulation_n` 小于基础覆盖量 → 问用户要不要加预算，或回 WF2 合并有依据的场景——不要静默丢弃 archetype。

## 红线

继承 `SKILL.md` 的跨 workflow 红线。本步独有：**不照搬 `persona_generator.py` 的固定规则分类**（usage_frequency → archetype）——本项目是 LLM 驱动、按问卷反推变量，archetype 由 WF2 定，这里只展开个体，只借它的 3-part 置信度结构。

## 下一步

受访者就绪后进入 `workflows/04-response-simulation.md`：LLM 以每个 persona 身份，依据 `mechanism_trace` 与 `task_friction_profile` 认真作答问卷，产出 `responses.jsonl`。

## 示例

见上文"输出"段的 `respondents.jsonl` 与 `respondents_meta.json` 示例。完整 60 人见运行时产出。
