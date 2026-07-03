# Workflow 4：模拟作答与收集 (response-simulation)

LLM 以每个 persona 的身份认真作答问卷，产出答案 + 机制/任务摩擦可追溯的理由，汇总成数据集。默认"认真目标用户模式"：模拟有限理性、人格差异、不确定性，不模拟无效作答。

按需从根 `SKILL.md` 加载。依赖 WF3 的 `respondents.jsonl`、WF2 Phase B 的 `behavior_mechanisms.json`、Phase C 的 `task_frictions.json` 与 WF1 的 `survey.json`。

## When to use

- `respondents.jsonl` 与 `survey.json` 已就绪，需要让合成受访者"填问卷"。
- WF3 完成后由 pipeline 推进。

不适用：无 `respondents.jsonl` → 回 WF3；无 `survey.json` → 回 WF1。

## 输入

- `runs/<时间戳>/respondents.jsonl`：受访者五层信息。
- `runs/<时间戳>/respondents_meta.json`：集合元数据（可选参考）。
- `runs/<时间戳>/behavior_mechanisms.json`：机制链、触发条件和约束。
- `runs/<时间戳>/task_frictions.json`：任务摩擦维度、分数、drivers、题目作答规则。
- `runs/<时间戳>/survey.json`：要作答的问卷（题型 / 量表 / options）。

**禁止输入**：`hypotheses.json`。即使文件已存在，本步也不读取、不搜索、不摘要、不复述其内容——这是整个方法论防自证预言的关键隔离点。

## 方法

### 作答模式：认真目标用户，不是橡皮章

每个受访者独立、逐题作答，以该 persona 的五层处境、`mechanism_trace` 和 `task_friction_profile` 为依据。哪些行为该模拟、哪些不该，取决于它们是不是真实受访者会做的事：

| 类型 | 是否模拟 | 说明 |
|---|---|---|
| 无效作答 | 不要 | 瞎填 / 反填 / 恶意乱选 / 看都不看直接选——这不是"认真人格"的一种,是噪声 |
| 有限理性 | 要 | 认真答，但受经验 / 预算 / 理解力 / 场景限制 |
| 人格差异 | 要 | 谨慎 / 开放 / 保守 / 价格敏感 / 信任或不信任 AI |
| 不确定性 | 要 | 没经历过就说"不确定"，不强行给专家答案 |
| 社会赞许偏差 | 谨慎降低 | 让模拟人像私下诚实回答，不为讨好而答 |

关键题必须能追溯到 `mechanism_trace`（表层回答、假设性潜在动机、需求真实性假设标签要自洽）；痛点/排序/功能优先级/使用边界/开放题必须能追溯到 `task_friction_profile`（最高痛点从高分摩擦维度推导，不从性格直接猜）。没经历过的题答"不确定/不了解/不适用"并标 `uncertain: true`；关键题（结果变量题/开放题）给简短 `reasoning`。

### 痛点题：先查规则和分数，再作答

题目问"哪个环节更麻烦/最想先解决什么/哪些阻力最大"时，先读 `task_frictions.json` 的 `question_friction_rules`，再读 respondent 的 `task_friction_profile.top_friction_dimensions` 与 `scores`：

- multi-select：优先选 score≥4 对应选项，最多加 1 个 score=3 的次要项
- ranking：按 score 从高到低排序，允许相邻项因个体细节交换
- open：写具体 drivers（"小厨房台面紧张""孩子在厨房走动""清洗拆装麻烦"），不写空泛态度
- likert pain/severity：score 1-2 → 低，3 → 中，4-5 → 高

题目高度依赖个人口味且摩擦依据不足时，标 `uncertain: true` 或在 reasoning 中标低置信，不要硬答一个听起来合理但没依据的答案。

### 盲模拟与假设隔离

WF4 只能读取 persona 的可观察背景、经历、资源、情境、能力、机制链和任务摩擦。`hypotheses.json` 是模拟前封存的预测，只在 WF5 打开。

优先在新的隔离 context / subagent 中运行本步，只传入输入清单里的四个文件，不传递上游对话摘要中的预测内容。如果运行环境做不到隔离，可以在当前 context 执行，但 `responses_meta.blinding.level` 必须写 `procedural`，`quality.overall` 不能是 `high`，并在 WF5 报告里声明模型可能记得上游预测——这不是走形式的降级,是让下游知道这次模拟的证据强度打了折扣。

不知道预期答案方向时仍要根据 persona 的实际处境逐题判断；同 archetype 个体只在经历和约束确实相同的地方才该一致，不同属性该产生有依据的差异；模拟结果不支持预注册假设时不重生成、不纠偏，保留原结果供 WF5 对照。

## 输出

写两个文件：

**`runs/<时间戳>/responses.jsonl`** — 每行一个受访者的全部作答：

```jsonl
{"respondent_id":"R001","answers":[{"question_id":"Q1","answer":"大三","reasoning":null,"uncertain":false},{"question_id":"Q3","answer":4,"reasoning":"当前时间紧、真实问卷回收困难，所以更看重省时。","mechanism_id":"M1","surface_reason":"提高调研效率","hypothesized_latent_motive":"缓解任务失败压力","uncertain":false},{"question_id":"Q4","answer":"没用过不敢说","reasoning":"缺少真实使用经验，所以只能先保留判断。","mechanism_id":"M-SURVEY-RESPONSE","surface_reason":"不了解","hypothesized_latent_motive":"避免装懂导致判断失真","uncertain":true}]}
{"respondent_id":"R002","answers":[...]}
```

**`runs/<时间戳>/responses_meta.json`** — 模拟质量自评：

```json
{
  "count": 60,
  "by_archetype": {"A1": 18, "A2": 11, "...": "..."},
  "blinding": {
    "level": "isolated",
    "hypotheses_loaded": false,
    "allowed_inputs": ["survey.json", "respondents.jsonl", "behavior_mechanisms.json", "task_frictions.json"]
  },
  "quality": {
    "internal_consistency": "high",
    "persona_answer_match": "medium",
    "no_invalid_responding": "pass",
    "overall": "medium",
    "rationale": "..."
  },
  "invalid_patterns_detected": [],
  "note": "合成样本 / 仅供预调研 / 反映模拟质量不等于研究效度"
}
```

### answer 字段格式（强类型，便于 WF5 直接统计）

| type | answer 值 | 例 |
|---|---|---|
| single-choice | 选项文本（须在 survey options 内） | `"大三"` |
| multi-select | 选项文本数组 | `["小红书","同学"]` |
| likert | int（1-points） | `4` |
| rating | int（1-points） | `7` |
| nps | int（0-10） | `8` |
| ranking | 选项文本数组（按排序顺序） | `["效率","规范","成本"]` |
| open | 文本 | `"没用过不敢说"` |

`reasoning` 关键题必给；`mechanism_id` 关键题建议填，来自 respondent 的 `mechanism_trace.mechanism_ids` 或机制库中的 survey-response 机制；`friction_dimension_id` 痛点/排序/优先级/开放题建议填，来自 `task_friction_profile.top_friction_dimensions`；`hypothesized_latent_motive` 由机制链推导，不是受访者自述事实，只在关键题必填；`uncertain` 为 true 时 answer 填"不确定/不了解/不适用"或量表中点。

## 模拟质量自评

写 `responses_meta.json`，三个维度：

- **internal_consistency**：同一受访者跨相关题答案不矛盾。"用过 AI"却说"从没接触 AI"就是矛盾，要降级。
- **persona_answer_match**：答案能追溯到该 persona 的处境、经历、资源、能力、`mechanism_trace` 与 `task_friction_profile`。不能以是否符合任何预注册预测评分——评分标准是"像不像这个人",不是"猜中了没有"。
- **no_invalid_responding**：无直线作答（全选同一项）/ 全选中点 / 逻辑矛盾 / 全 uncertain。`invalid_patterns_detected` 列出发现的无效模式，应为空或少量。

这个自评反映模拟质量，不等于研究效度，`note` 必须声明合成样本/仅供预调研。

## 完成前确认

- **覆盖度与强类型**：`responses.jsonl` 每行含 `respondent_id`+`answers`，与 `respondents.jsonl` 一一对应；`answers` 覆盖 `survey.json` 所有题；每个 answer 值符合强类型表（single-choice 在 options 内、likert/rating/nps 是量程内的 int）。
- **关键题与痛点题可追溯**：结果变量类的 likert/rating/nps/open 题有非空 `reasoning`，能追溯到 `mechanism_trace`；痛点/排序/优先级/开放题能追溯到 `task_friction_profile`，且不与其高分摩擦维度矛盾。
- **无无效作答模式**：没有直线作答(同一受访者所有量表题同值)，没有除非persona真的啥都没经历、否则全部 uncertain 的情况。
- **假设隔离正确**：responses 不含 hypothesis id、`predicted_pattern` 或任何来自 `hypotheses.json` 的内容；`responses_meta.blinding` 含 `level`/`hypotheses_loaded=false`/`allowed_inputs`，`level=procedural` 时 `overall` 不为 high。
- **meta 完整**：`responses_meta.json` 含 `count`/`quality`/`invalid_patterns_detected`/`note`，`note` 含"合成样本"与"预调研"。

## 该停下来问的情况

- 缺 `respondents.jsonl`/`behavior_mechanisms.json`/`task_frictions.json`/`survey.json` 任一个 → 回对应上游步骤。
- `no_invalid_responding` 自评不通过 → 重作答问题受访者，不放过。

## 红线

继承 `SKILL.md` 的跨 workflow 红线（假设封存、结果变量红线）。本步独有：**不模拟无效作答/随机/恶意反填**——这不是一个可以为了"增加数据多样性"而放松的规则，无效作答是噪声，不是人格差异。

## 下一步

作答就绪后进入 `workflows/05-result-analysis.md`：对 `responses.jsonl` 做描述统计 + 开放题主题编码 + 分群交叉分析，产出报告。

## 示例

见上文"输出"段的 `responses.jsonl` 与 `responses_meta.json` 示例。完整 60 人作答见运行时产出。
