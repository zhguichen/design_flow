# Workflow 4：模拟作答与收集 (response-simulation)

LLM 以每个 persona 的身份认真作答问卷，产出答案 + 简短理由，汇总成数据集。默认"认真目标用户模式"：模拟有限理性 / 人格差异 / 不确定性，不模拟无效作答。

按需从根 `SKILL.md` 加载。依赖 WF3 的 `respondents.jsonl` 与 WF1 的 `survey.json`。

## When to use

- `respondents.jsonl` 与 `survey.json` 已就绪，需要让合成受访者"填问卷"
- WF3 完成后由 pipeline 推进

不适用：无 `respondents.jsonl` → 回 WF3；无 `survey.json` → 回 WF1。

## 输入

- `runs/<时间戳>/respondents.jsonl`：受访者五层信息。
- `runs/<时间戳>/respondents_meta.json`：集合元数据（可选参考）。
- `runs/<时间戳>/survey.json`：要作答的问卷（题型 / 量表 / options）。

## 输出

写两个文件：

**`runs/<时间戳>/responses.jsonl`** — 每行一个受访者的全部作答：

```jsonl
{"respondent_id":"R001","answers":[{"question_id":"Q1","answer":"大三","reasoning":null,"uncertain":false},{"question_id":"Q3","answer":4,"reasoning":"赶时间，AI 能省事我愿意试","uncertain":false},{"question_id":"Q4","answer":"没用过不敢说","reasoning":null,"uncertain":true}]}
{"respondent_id":"R002","answers":[...]}
```

**`runs/<时间戳>/responses_meta.json`** — 模拟质量自评：

```json
{
  "count": 60,
  "by_archetype": {"A1": 18, "A2": 11, "...": "..."},
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

### answer 字段格式（强类型）

按 WF1 题型给值，WF5 可直接统计：

| type | answer 值 | 例 |
|---|---|---|
| single-choice | 选项文本（须在 survey options 内） | `"大三"` |
| multi-select | 选项文本数组 | `["小红书","同学"]` |
| likert | int（1-points） | `4` |
| rating | int（1-points） | `7` |
| nps | int（0-10） | `8` |
| ranking | 选项文本数组（按排序顺序） | `["效率","规范","成本"]` |
| open | 文本 | `"没用过不敢说"` |

字段：

- `reasoning`：关键题（结果变量题 / 开放题）必给简短理由，其余可为 null。
- `uncertain`：persona 对该题没经历 / 不了解时为 true，answer 填"不确定 / 不了解 / 不适用"或量表中点。

## 方法

### 作答模式：认真目标用户

每个受访者**独立、逐题**作答。以该 persona 的五层处境为依据，认真回答自己理解的题。

| 类型 | 是否模拟 | 说明 |
|---|---|---|
| 无效作答 | 不要 | 瞎填 / 反填 / 恶意乱选 / 看都不看直接选 |
| 有限理性 | 要 | 认真答，但受经验 / 预算 / 理解力 / 场景限制 |
| 人格差异 | 要 | 谨慎 / 开放 / 保守 / 价格敏感 / 信任或 distrust AI |
| 不确定性 | 要 | 没经历过说"不确定"，不强行给专家答案 |
| 社会赞许偏差 | 谨慎降低 | 让模拟人像私下诚实回答，不为讨好而答 |

### 作答规则

- 不允许瞎填 / 恶意反填 / 随机选择。
- 不允许为制造噪声故意矛盾。
- 必须根据 persona 真实处境回答。
- 没经历过的题答"不确定 / 不了解 / 不适用"，标 `uncertain: true`。
- 关键题（结果变量题 / 开放题）给简短 `reasoning`。

### 不照抄预期倾向

WF2 的 `预期影响construct` 是**方向提示**，不是剧本。WF4 作答时：

- 答案方向应与 persona 处境及 `预期影响construct` 大体一致（persona-答案匹配度）。
- 但**不能 100% 决定论**——同 archetype 不同个体、同一人不同题都应有变异（有限理性）。
- 若答案与预期倾向完全一致、零变异 → 退化为剧本，质量自评降级。

## 模拟质量自评

写 `responses_meta.json`，三维度：

- **internal_consistency**（答案内部一致性）：同一受访者跨相关题答案不矛盾。如"用过 AI"却说"从没接触 AI" → 矛盾，降级。
- **persona_answer_match**（persona-答案匹配度）：答案符合该 persona 的处境与 `预期影响construct` 方向，但非 100%。完全偏离 → low；完全决定论 → 也降级（剧本化）。
- **no_invalid_responding**（拒绝乱填）：无直线作答（全选同一项）/ 全选中点 / 逻辑矛盾 / 全 uncertain。`invalid_patterns_detected` 列出发现的无效模式（应为空或少量）。

> 此自评反映**模拟质量**，不等于研究效度。`note` 必须声明 合成样本 / 仅供预调研。

## 红线

- 不模拟无效作答 / 随机 / 恶意反填。
- 输出标注合成样本：`responses_meta.json` 的 `note`。
- 全 pipeline 红线继承：合成样本 / 样本量 / 置信度 / 仅供预调研。

## 验收标准（可机械检查）

- [ ] `responses.jsonl` 每行是合法 JSON，含 `respondent_id` + `answers`。
- [ ] 每个 `respondent_id` 能在 `respondents.jsonl` 找到（一一对应，数量一致）。
- [ ] 每行 `answers` 覆盖 `survey.json` 所有题（`question_id` 集合相等）。
- [ ] answer 值符合强类型表：single-choice 值在 options 内；likert / rating / nps 为 int 且在量程内。
- [ ] 关键题（type=likert / rating / nps / open 且 construct 为结果变量）有非空 `reasoning`。
- [ ] 无无效作答模式：无直线作答（同一受访者所有量表题同值）、无全 uncertain（除非 persona 真的啥都没经历）。
- [ ] `responses_meta.json` 存在，含 `count` / `quality` / `invalid_patterns_detected` / `note`。
- [ ] `note` 含"合成样本"与"预调研"。

## Stop 条件

- 无 `respondents.jsonl` → 回 WF3。
- 无 `survey.json` → 回 WF1。
- 质量自评 `no_invalid_responding` 不通过 → 重作答问题受访者，不放过。

## 下一步

作答就绪后进入 `workflows/05-result-analysis.md`：对 `responses.jsonl` 做描述统计 + 开放题主题编码 + 分群交叉分析，产出报告。

## 示例

见上文"输出"段的 `responses.jsonl` 与 `responses_meta.json` 示例。完整 60 人作答见运行时产出。
