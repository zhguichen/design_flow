# Workflow 4：模拟作答与收集 (response-simulation)

LLM 以每个 persona 的身份认真作答问卷，产出答案 + 机制可追溯的理由，汇总成数据集。默认"认真目标用户模式"：模拟有限理性、人格差异、不确定性，不模拟无效作答。

按需从根 `SKILL.md` 加载。依赖 WF3 的 `respondents.jsonl`、WF2 Phase B 的 `behavior_mechanisms.json` 与 WF1 的 `survey.json`。

## When to use

- `respondents.jsonl` 与 `survey.json` 已就绪，需要让合成受访者"填问卷"。
- WF3 完成后由 pipeline 推进。

不适用：无 `respondents.jsonl` → 回 WF3；无 `survey.json` → 回 WF1。

## 输入

- `runs/<时间戳>/respondents.jsonl`：受访者五层信息 + mechanism_trace；不得含摩擦分数、top friction 或答案规则。
- `runs/<时间戳>/respondents_meta.json`：集合元数据（可选参考）。
- `runs/<时间戳>/selection.json`：`full` 或 `stratified-pilot` 的确定性入选 id、seed 与分层计数。
- `runs/<时间戳>/behavior_mechanisms.json`：机制链、触发条件和约束（帮助理解 persona 心理，不是作答规则）。
- `runs/<时间戳>/survey.json`：要作答的问卷（题型 / 量表 / options）。

**禁止输入**：
- `hypotheses.json`：即使文件已存在，本步也不读取。
- `task_frictions.json`：任务情境映射不传入 subagent。方案 A 只把已事实化的经历、资源、能力和环境限制放进 persona，不传维度强弱或预测方向。

## 方法

### 启动前显示隔离说明

执行 WF4 前先向用户显示：“WF4 需要开启隔离 subagent，让作答模型只看到 persona、问卷与允许的机制信息，避免接触封存预测。”这是一条执行说明，不新增确认门。

随后显示实际模式：

- 当前环境支持 subagent：显示 `执行模式：isolated`，并为每个入选 persona 开启不共享上游对话的隔离 context。
- 当前环境不支持 subagent：显示 `执行模式：procedural`、无法隔离的具体原因和置信度降级；不得静默降级，也不得把共享上下文标为 `isolated`。

### 作答模式：凭 persona 背景故事答题，不执行规则表

只处理 `selection.json.selected_respondent_ids` 中的 persona。每个入选受访者独立、逐题作答。**subagent 只拿到该 persona 的五层背景信息（基础身份、社会处境、心理倾向、行为习惯、作答风格）和 mechanism_trace（心理机制描述），不拿到未入选 persona、任务摩擦文件、维度强弱、分数或作答规则。**

subagent 的任务是：**读这个人的故事，然后以这个人的身份回答问卷**。就像演员拿到角色档案后即兴表演——角色档案告诉你这个人是谁、经历过什么、在乎什么，但不会告诉你每句台词应该怎么念。

| 类型 | 是否模拟 | 说明 |
|---|---|---|
| 无效作答 | 不要 | 瞎填 / 反填 / 恶意乱选 / 看都不看直接选 |
| 有限理性 | 要 | 认真答，但受经验 / 预算 / 理解力 / 场景限制 |
| 人格差异 | 要 | 谨慎 / 开放 / 保守 / 价格敏感 / 信任或不信任 AI |
| 不确定性 | 要 | 没经历过就说"不确定"，不强行给专家答案 |
| 社会赞许偏差 | 谨慎降低 | 让模拟人像私下诚实回答，不为讨好而答 |

### 关键题和痛点题：从 persona 故事推导，不是从分数查表

关键题（结果变量类的 likert/rating/nps/open 题）和痛点题（问"哪个环节更麻烦/最想先解决什么/哪些阻力最大"）必须有 `reasoning`，且 reasoning 必须能追溯到 persona 的具体处境、经历、性格——不是引用一个分数，而是讲一个"为什么这个人会这么想"的故事。

例如：
- ❌ 坏的 reasoning："F2=5 所以打 5 分"——这是查表，不是模拟
- ✅ 好的 reasoning："每天骑车通勤 8 公里，车棚里刮了蹭了无数次，对我来说车就是会动的椅子——椅子好看当然好，但谁会因为椅子好看多花一千块？"——这是从 R001 的处境推导的

### 盲模拟与假设隔离

WF4 只能读取 persona 的**可观察背景、经历、资源、情境、能力、心理倾向和 mechanism_trace**。不读取 `hypotheses.json`，不读取 `task_frictions.json`。

当前环境支持 subagent 时，必须在新的隔离 context 中运行本步。每个 subagent 只传入：该 persona 的五层信息 + mechanism_trace + 所属 archetype 的 behavior_mechanisms + survey.json。不传入跨 persona 的比较信息、不传入摩擦分数、不传入任何预测方向。

如果能做到每个 subagent 在独立会话中运行（不共享上游对话），`responses_meta.blinding.level` 可以写 `isolated`，`quality.overall` 可以到 `high`。如果共享会话上下文，降级为 `procedural`。

不知道预期答案方向时仍要根据 persona 的实际处境逐题判断；同 archetype 个体只在经历和约束确实相同的地方才该一致，不同属性该产生有依据的差异；模拟结果不支持预注册假设时不重生成、不纠偏，保留原结果供 WF5 对照。

## 输出

写两个文件：

**`runs/<时间戳>/responses.jsonl`** — 每行一个受访者的全部作答：

```jsonl
{"respondent_id":"R001","answers":[{"question_id":"Q1","answer":"大三","reasoning":null,"uncertain":false},{"question_id":"Q3","answer":4,"reasoning":"当前时间紧、真实问卷回收困难，所以更看重省时。","mechanism_id":"M1","uncertain":false},{"question_id":"Q4","answer":"没用过不敢说","reasoning":"缺少真实使用经验，所以只能先保留判断。","uncertain":true}]}
{"respondent_id":"R002","answers":[...]}
```

**`runs/<时间戳>/responses_meta.json`** — 模拟质量自评：

```json
{
  "count": 12,
  "selection": {
    "mode": "stratified-pilot",
    "pool_n": 60,
    "selected_n": 12,
    "seed": 42,
    "by_archetype": {"A1": 3, "A2": 2, "A3": 2, "A4": 2, "A5": 2, "A6": 1},
    "excluded_count": 48
  },
  "blinding": {
    "level": "isolated",
    "hypotheses_loaded": false,
    "task_frictions_loaded": false,
    "allowed_inputs": ["survey.json", "respondents.jsonl (persona only)", "behavior_mechanisms.json"]
  },
  "quality": {
    "internal_consistency": "high",
    "persona_answer_match": "medium",
    "no_invalid_responding": "pass",
    "overall": "medium",
    "rationale": "..."
  },
  "invalid_patterns_detected": [],
  "note": "合成样本 / 分层预演 / 仅供预调研 / 不代表完整场景覆盖或研究效度"
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

`reasoning` 关键题必给，从 persona 的处境/经历/性格推导，不引用分数；`mechanism_id` 关键题建议填，来自 respondent 的 `mechanism_trace.mechanism_ids`。表层需求、假设性潜在动机和证据等级不复制进每条 answer，WF5 按 `mechanism_id` 联结 `behavior_mechanisms.json`。`uncertain` 为 true 时 answer 填"不确定/不了解/不适用"或量表中点。

## 模拟质量自评

写 `responses_meta.json`，三个维度：

- **internal_consistency**：同一受访者跨相关题答案不矛盾。
- **persona_answer_match**：答案能追溯到该 persona 的处境、经历、资源、能力、性格倾向。**不能以是否符合任何预注册预测评分**——评分标准是"像不像这个人"，不是"猜中了没有"。
- **no_invalid_responding**：无直线作答（全选同一项）/ 全选中点 / 逻辑矛盾 / 全 uncertain。`invalid_patterns_detected` 列出发现的无效模式，应为空或少量。

这个自评反映模拟质量，不等于研究效度，`note` 必须声明合成样本/仅供预调研。

## 完成前确认

先运行 `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_run.py" runs/<时间戳>/ --stage wf4` 做覆盖、强类型、id、reasoning 和隔离元数据校验，再判断：

- **关键题可追溯**：结果变量类的题有非空 `reasoning`，能追溯到 persona 的具体处境、经历或性格倾向——不是引用分数。
- **无无效作答模式**：没有直线作答，没有除非 persona 真的啥都没经历、否则全部 uncertain 的情况。
- **选择边界正确**：responses 与 `selection.json` 一一对应；pilot 覆盖所有 archetype，并在 meta 中记录 pool/selected/excluded、seed 和分层计数。

## 该停下来问的情况

- 缺 `respondents.jsonl`/`selection.json`/`behavior_mechanisms.json`/`survey.json` 任一个 → 回对应上游步骤。
- `no_invalid_responding` 自评不通过 → 重作答问题受访者，不放过。
- pilot 的 n 小于 archetype 数，或 selection 未覆盖全部 archetype → 回门 3 重新选择 n。

## 红线

继承 `SKILL.md` 的跨 workflow 红线（假设封存、结果变量红线）。本步独有：**不模拟无效作答/随机/恶意反填**；**不传入摩擦分数或作答规则**——subagent 只凭 persona 背景故事答题，不执行查找表。

## 下一步

作答就绪后进入 `workflows/05-result-analysis.md`：对 `responses.jsonl` 做描述统计 + 开放题主题编码 + 分群交叉分析，产出报告。
