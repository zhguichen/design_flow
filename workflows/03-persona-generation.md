# Workflow 3：Persona 生成 (persona-generation)

把通过机制校验和任务摩擦校验的人群原型按比例展开成 N 个具体的模拟受访者，每个带五层信息结构、`mechanism_trace` 与 `task_friction_profile`。同类下个体必须有差异，不能复制粘贴。

按需从根 `SKILL.md` 加载。依赖 WF2 的 `archetypes.json`、WF2.5 的 `behavior_mechanisms.json` 与 WF2.6 的 `task_frictions.json`。

## When to use

- `archetypes.json`、`behavior_mechanisms.json` 与 `task_frictions.json` 已就绪，需要生成具体合成受访者
- 用户指定 N（或用 `survey.recommended_n`）
- WF2 完成后由 pipeline 推进

不适用：无 `archetypes.json` → 回 WF2；无 `behavior_mechanisms.json` → 回 WF2.5；无 `task_frictions.json` → 回 WF2.6。

## 输入

- `runs/<时间戳>/archetypes.json`：原型 + 比例。
- `runs/<时间戳>/behavior_mechanisms.json`：机制链、表层需求、潜在动机、作答影响。
- `runs/<时间戳>/task_frictions.json`：任务摩擦维度、分数、drivers、题目作答规则。
- `runs/<时间戳>/survey.json`：上下文（`construct_measured`、`target_population`）。
- N：样本量。优先用户指定，否则取 `survey.recommended_n`。

## 输出

写两个文件：

**`runs/<时间戳>/respondents.jsonl`** — 每行一个受访者：

```jsonl
{"respondent_id":"R001","archetype_id":"A1","基础身份":{"年级":"大三","专业":"环艺","学校类型":"普通本科","城市":"二线","经济条件":"中等"},"社会处境":{"时间压力":"高","导师要求":"严格","社交资源":"少","当前任务阶段":"毕设中期"},"心理倾向":{"AI信任":"中高","焦虑程度":"中","风险偏好":"中低","认真程度":"高","从众倾向":"中"},"行为习惯":{"找资料方式":"小红书+同学","作业习惯":"临 deadline 赶","是否用AI":"是","发问卷方式":"同学互填"},"作答风格":{"认真度":"高","是否会选不确定":"是","价格敏感度":"高","是否会承认不了解":"是"},"mechanism_trace":{"mechanism_ids":["M1","M3"],"surface_need":"提高调研效率","latent_motive":"缓解找不到受访者导致作业失败的压力","demand_authenticity":["surface_need","contextual_need","compensatory_need"],"answer_implications":{"Q7":"使用意愿偏高但会要求仅限预调研","Q10":"信任中等，关注依据和透明度"}},"task_friction_profile":{"top_friction_dimensions":["F1","F3"],"scores":{"F1":5,"F2":3,"F3":4},"drivers":{"F1":["deadline","真实用户渠道不足"]},"likely_pain_answer_pattern":"优先选择耗时、回收和分析负担相关痛点"}}
{"respondent_id":"R002","archetype_id":"A1","基础身份":{...},...}
```

**`runs/<时间戳>/respondents_meta.json`** — 集合元数据 + 自评：

```json
{
  "count": 60,
  "n_requested": 60,
  "generated_at": "2026-07-01",
  "by_archetype": {"A1": 18, "A2": 11, "A3": 12, "A4": 9, "A5": 7, "A6": 3},
  "confidence": {
    "sample_size": "high",
    "data_quality": "medium",
    "consistency": "high",
    "overall": "medium",
    "rationale": "N=60 足够读分布；单源 LLM 生成故数据质量中；背景与预期倾向一致"
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

> 红线：结果变量（满意度 / 使用意愿 / 推荐意愿 / 付费意愿）**不**出现在五层里——它们是问卷要测的结果，不是 persona 背景。五层只设定影响结果的原因。

### mechanism_trace 字段

每个 respondent 必须写 `mechanism_trace`，把五层信息追溯回 WF2.5：

| 字段 | 说明 |
|---|---|
| `mechanism_ids` | 该受访者继承的机制 id，必须存在于 `behavior_mechanisms.json` |
| `surface_need` | 受访者会说出口的表层需求 |
| `latent_motive` | 受环境、资源、能力、身份等影响形成的潜在动机 |
| `demand_authenticity` | 需求真实性标签，取自 WF2.5 |
| `answer_implications` | 机制会影响哪些题，键用 `question_id` |

`mechanism_trace` 不是逐题答案，只是让 WF4 作答时有依据可追。

### task_friction_profile 字段

每个 respondent 必须写 `task_friction_profile`，把痛点/麻烦环节/功能优先级追溯回 WF2.6：

| 字段 | 说明 |
|---|---|
| `top_friction_dimensions` | 该受访者最可能感到麻烦的任务摩擦维度 |
| `scores` | 维度分数，来自 `task_frictions.json`，可做轻微个体变体 |
| `drivers` | 推高摩擦分数的具体生活情境、行为经验、环境限制 |
| `likely_pain_answer_pattern` | 痛点题、排序题、开放题的总体作答依据 |

`task_friction_profile` 也不是逐题答案。它让 WF4 在回答“哪个环节更麻烦”时，不再从性格直接猜。

## 方法

### 第零步：读取机制映射

先读 `behavior_mechanisms.json`，按 `archetype_mechanism_map` 找出每个 archetype 的机制。五层信息必须从机制链中长出来：

`环境/事件 -> 社会处境 -> 资源/能力限制 -> 行为机制 -> 表层需求 -> 潜在动机 -> 作答影响`

不能只按年龄、专业、城市随机扩写；也不能把结果变量塞进五层当背景。

### 第零点五步：读取任务摩擦映射

再读 `task_frictions.json`，按 `archetype_friction_map` 找出每个 archetype 的任务摩擦。个体的痛点相关字段必须从这条链中长出来：

`任务场景 -> 当前行为 -> 环境限制 -> 资源/能力 -> 行为机制 -> 摩擦维度 -> 可能痛点答案`

同一 archetype 下允许轻微变体，例如相邻摩擦维度交换、score 4/5 微调，但不能把低分摩擦写成最高痛点。

### 第一步：按比例分配

每 archetype 生成 `round(proportion × N)` 个个体。取整产生的余数按比例大者补齐至 N。`by_archetype` 记录实际分配。

### 第二步：同类下个体差异（强制）

同一 archetype 下的个体**不能复制粘贴**。从以下维度变化（同类任意两个体至少 3 维不同）：

专业方向 / 年级 / 学校类型 / 时间压力 / 经济条件 / AI 信任度 / 社交资源 / 方法论意识 / 作答认真度

同类个体共享该原型的核心特征与变量设定（来自 `archetypes.json`），但在上述维度上各自不同。

### 第三步：anti-patterns 自检

改编自 persona-methodology，每条不过则重生成：

| anti-pattern | 在合成场景的表现 | 检查 |
|---|---|---|
| Elastic（弹性） | 同类下个体雷同、或一个 persona 啥都包含 | 同 archetype 下任意两个体 ≥3 维不同 |
| Demographic-only（纯人口统计） | 五层只有基础身份有内容 | 社会处境 / 心理倾向 / 行为习惯 / 作答风格 均非空 |
| Ideal user（理想用户） | 全是认真、高信任、高资源的好用户 | 含保守 / 怀疑 / 资源不足等反面个体 |
| Committee（委员会拼凑） | 一个个体塞矛盾特征凑数 | 个体内部特征自洽 |
| Stale（过期） | 未标生成时间 | meta 含 `generated_at`（或由 `runs/<时间戳>` 体现） |

### 第四步：置信度自评（改编 3-part）

`Confidence = (样本量分 + 数据质量分 + 一致性分) / 3`，各维 low / medium / high：

- **样本量分**：N<10 low / 10-30 medium / 30+ high。合成 N 是选择，此项评"够不够读分布"。
- **数据质量分**：看 persona 完整度（五层齐）+ 个体差异度（同类不复制）。单源 LLM 生成本身是局限，故此维**封顶 medium**（除非多源交叉，本 pipeline 暂无）。
- **一致性分**：persona 背景设定、`mechanism_trace`、`task_friction_profile`、`archetypes` 的 `预期回答倾向` 不矛盾 → high；有矛盾 → low。
- `overall` = 三者综合，`rationale` 写明理由。

> **重要标注**：此置信度反映**模拟质量**（人像不像、答案会不会一致），**不等于研究效度**。合成样本对真实人群的代表性固有局限，必须在 `meta.note` 与 WF5 报告中显式声明。

## 红线

- 结果变量不作背景设定（继承 WF2）：满意度 / 使用意愿 / 推荐意愿 / 付费意愿 不出现在五层。
- 每个受访者必须能追溯到至少一个 WF2.5 机制；没有机制链，不生成 persona。
- 每个受访者必须能追溯到 WF2.6 的任务摩擦；痛点/任务偏好不能从性格直接生成。
- 合成样本标注：`respondents_meta.json` 的 `note` 标 合成样本 / 仅供预调研 / 反映模拟质量不等于研究效度。
- **不照搬 `persona_generator.py` 的固定规则分类**（usage_frequency → archetype）：本项目是 LLM 驱动、按问卷反推的变量，archetype 由 WF2 定，WF3 只展开个体。只借其 3-part 置信度结构。

## 验收标准（可机械检查）

- [ ] `respondents.jsonl` 每行是合法 JSON，含 `respondent_id` / `archetype_id` + 五层。
- [ ] 每行含 `mechanism_trace`，且 `mechanism_ids` 能在 `behavior_mechanisms.json` 找到。
- [ ] 每行含 `task_friction_profile`，且 `top_friction_dimensions` / `scores` 能在 `task_frictions.json` 找到。
- [ ] 每个 `respondent_id` 唯一（`R001..RNNN`）。
- [ ] 每个 `archetype_id` 能在 `archetypes.json` 找到。
- [ ] 每个 respondent 的 `archetype_id` 至少映射到一个机制，且五层不与机制链矛盾。
- [ ] 每个 respondent 的痛点/行为习惯不与 `task_friction_profile` 矛盾。
- [ ] 五层字段均非空（社会处境 / 心理倾向 / 行为习惯 / 作答风格 不能只有基础身份）。
- [ ] 同 `archetype_id` 下任意两个体至少 3 维 diff 不同（非复制粘贴）。
- [ ] 行数 = N（±1 容差），`by_archetype` 合计 = 行数。
- [ ] 五层不含"满意度 / 使用意愿 / 推荐意愿 / 付费意愿"等结果构念键（结果变量红线）。
- [ ] `respondents_meta.json` 存在，含 `count` / `by_archetype` / `confidence` / `anti_pattern_checks` / `note`。
- [ ] `note` 含"合成样本"与"预调研"字样。

## Stop 条件

- 无 `archetypes.json` → 回 WF2。
- 无 `behavior_mechanisms.json` → 回 WF2.5。
- 无 `task_frictions.json` → 回 WF2.6。
- N 未定且 `survey.recommended_n` 缺失 → 追问用户要 N，不臆造。
- anti-pattern 自检不通过 → 重生成直至通过，不放过。

## 下一步

受访者就绪后进入 `workflows/04-response-simulation.md`：LLM 以每个 persona 身份，并依据 `mechanism_trace` 与 `task_friction_profile` 认真作答问卷，产出 `responses.jsonl`。

## 示例

见上文"输出"段的 `respondents.jsonl` 与 `respondents_meta.json` 示例。完整 60 人见运行时产出。
