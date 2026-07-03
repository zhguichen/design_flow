# Workflow 3：Persona 生成 (persona-generation)

把通过机制校验和任务情境校验的人群原型，按场景覆盖计划展开成具体的模拟受访者。每个受访者带五层信息结构与 `mechanism_trace`；任务摩擦 drivers 要转写成可观察的经历、资源和环境限制，不能附带分数或预期答案。

按需从根 `SKILL.md` 加载。依赖 WF2 (`02-audience-analysis.md`) 产出的 `archetypes.json`、`behavior_mechanisms.json` 与 `task_frictions.json`。

## When to use

- `archetypes.json`、`behavior_mechanisms.json` 与 `task_frictions.json` 已就绪，需要生成具体合成受访者。
- `archetypes.json` 已含 `simulation_plan`，或用户需要调整模拟计算预算。
- WF2 完成后由 pipeline 推进。

不适用：缺 `archetypes.json` → 回 WF2 Phase A；缺 `behavior_mechanisms.json` → 回 WF2 Phase B；缺 `task_frictions.json` → 回 WF2 Phase C。

## 输入

- `runs/<时间戳>/archetypes.json`：原型 + `scenario_weight` + `weight_source` + `simulation_plan`。
- `runs/<时间戳>/behavior_mechanisms.json`：机制的 `logic`/`need_reading`/`evidence`/`scrutiny`。
- `runs/<时间戳>/task_frictions.json`：任务范围、相关维度、可观察 drivers 与题目情境覆盖。
- `runs/<时间戳>/survey.json`：上下文（`construct_measured`、`target_population`）。
- `simulation_n`：合成记录数，优先用 `simulation_plan.simulation_n`；用户可调整，但不能低于基础场景覆盖要求。

## 方法

### 先把因果链读透，再展开个体

读 `behavior_mechanisms.json` 的 `archetype_mechanism_map`，找出每个 archetype 的机制。五层信息必须从这条链长出来：

`环境/事件 → 社会处境 → 资源/能力限制 → 行为机制 → 表层需求 → 假设性潜在动机`

不能只按年龄、专业、城市随机扩写；也不能把结果变量塞进五层当背景——那是 WF2 定的红线，这里继承。

再读 `task_frictions.json` 的 `archetype_friction_map`，把 drivers 转写进五层中的具体事实。个体故事要从这条链长出来：

`任务场景 → 当前行为 → 环境限制 → 资源/能力 → 行为机制`

例如，不写“F2=5”或“尺寸规划是最高痛点”，而写“曾买回尺寸不合的家具、租房不可改造、空间规划能力中低”。WF4 只看到这些事实并独立作答；任何预期高低、排序或逐题答案都不得混入 persona。

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
- **一致性分**：persona 背景设定与 `mechanism_trace`、archetype 变量、任务情境 drivers 不矛盾 → high；有矛盾 → low。

`overall` 是三者综合，`rationale` 写明理由。这个置信度反映的是**模拟质量与场景覆盖**（人像不像、答案会不会一致、每类有没有变体），**不等于研究效度或总体代表性**——增加 `simulation_n` 不会增加真实证据，必须在 `meta.note` 和 WF5 报告里显式声明。

## 输出

写两个文件：

**`runs/<时间戳>/respondents.jsonl`** — 每行一个受访者：

```jsonl
{"respondent_id":"R001","archetype_id":"A1","基础身份":{"年级":"大三","专业":"环艺","学校类型":"普通本科","城市":"二线","经济条件":"中等"},"社会处境":{"时间压力":"高","导师要求":"严格","社交资源":"少","当前任务阶段":"毕设中期","调研限制":"缺少真实用户渠道"},"心理倾向":{"AI信任":"中高","焦虑程度":"中","风险偏好":"中低","认真程度":"高","从众倾向":"中"},"行为习惯":{"找资料方式":"小红书+同学","作业习惯":"临 deadline 赶","是否用AI":"是","发问卷方式":"同学互填","问卷经历":"曾因回收不足延期"},"作答风格":{"认真度":"高","是否会选不确定":"是","价格敏感度":"高","是否会承认不了解":"是"},"mechanism_trace":{"mechanism_ids":["M1","M3"],"individual_expression":"deadline 临近且缺少真实用户渠道，效率诉求与方法风险顾虑同时存在"}}
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
| `individual_expression` | 该机制在此人的具体处境里如何表现；只写个体差异，不复制机制定义或预测答案 |

完整的表层需求、假设性潜在动机、需求标签和证据等级只保留在 `behavior_mechanisms.json`。WF4 按 `mechanism_ids` 动态联结相关机制，再结合 `individual_expression` 和五层故事作答；respondent 不复制这些 archetype 级内容。

### 任务情境 drivers 如何进入 persona

`task_frictions.json` 只作为 WF3 的情境覆盖清单。把其中的 drivers 分散写入`社会处境`、`行为习惯`、`基础身份`或其他合适的五层字段，使用具体、可观察的表述。不要在 respondent 行中保留 `task_friction_profile`、摩擦分数、top friction、答案阈值或题目排序；这些内容会把预测方向泄漏给 WF4。

## 完成前确认

先运行 `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_run.py" runs/<时间戳>/ --stage wf3` 做 JSONL、id、配额、禁止字段和跨文件追溯校验，再判断：

- **五层完整且不含结果变量**：社会处境/心理倾向/行为习惯/作答风格都非空（不是只有基础身份），且不含"满意度/使用意愿/推荐意愿/付费意愿"这类结果构念键。
- **任务情境已事实化**：每个 persona 至少包含与其 archetype 相关的具体经历、资源、能力或环境限制；respondent 行不含 `task_friction_profile`、score、top friction 或答案规则。
- **同类个体强制差异**：同 `archetype_id` 下任意两个体至少 3 维不同，不是复制粘贴。
- **anti-pattern 自检通过**：上面五条逐一过一遍，不过就重生成。

## 该停下来问的情况

- 缺 `archetypes.json` / `behavior_mechanisms.json` / `task_frictions.json` 任一个 → 回对应的 WF2 Phase。
- `simulation_plan` 缺失 → 回 WF2 制定场景覆盖计划。
- `simulation_n` 小于基础覆盖量 → 问用户要不要加预算，或回 WF2 合并有依据的场景——不要静默丢弃 archetype。

## 门 3：选择模拟模式

展示 persona 抽样与完整 `by_archetype` 分配后，让用户二选一：

- `full`：全部 persona 进入 WF4，作为完整场景模拟。
- `stratified-pilot`：用户只指定预演数量 n，具体 persona 由脚本按 archetype 确定性分层抽取。n 不得小于 archetype 数，不能让用户手工挑 respondent id。

在同一展示中明确说明：“WF4 需要开启隔离 subagent，让每个作答模型只看到单个 persona、问卷与允许的机制信息，避免跨人物答案互相影响；这不会增加新的确认门。”同时显示实际可用模式：支持 subagent 时显示 `isolated`；不支持时显示降级为 `procedural` 及其置信度影响，不能静默降级。

运行：

```bash
# 完整模拟
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/select_respondents.py" runs/<时间戳>/ --mode full

# 分层预演；seed 必须记录，默认 42
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/select_respondents.py" runs/<时间戳>/ --mode stratified-pilot --n <n> --seed 42
```

脚本写出 `selection.json`。pilot 必须覆盖每个 archetype；如果未达到每类 `variants_per_archetype`，标记为有限覆盖。pilot 结果只用于低成本预演，不能解释为完整场景覆盖。以后需要正式结果时，重新以 `full` 模式运行 WF4/WF5，不修改 persona pool。

## 红线

继承 `SKILL.md` 的跨 workflow 红线。本步独有：**不照搬 `persona_generator.py` 的固定规则分类**（usage_frequency → archetype）——本项目是 LLM 驱动、按问卷反推变量，archetype 由 WF2 定，这里只展开个体，只借它的 3-part 置信度结构。

## 下一步

`selection.json` 就绪后进入 `workflows/04-response-simulation.md`：LLM 只为入选 persona 作答，产出 `responses.jsonl`。

## 示例

需要独立格式示例时按需读取 `references/output-examples.md`；正常执行不预加载。
