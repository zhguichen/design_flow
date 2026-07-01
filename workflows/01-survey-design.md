# Workflow 1：问卷设计 (survey-design)

根据研究目的产出一份结构良好的问卷文件（题序、题型、量表、避免偏差、样本量建议），每题带 `construct_measured` 元数据，为 Workflow 2 反推人群铺垫。

按需从根 `SKILL.md` 加载。不建议单独使用——单独用会丢 pipeline 上下文：人群反推依赖本步的 `construct_measured`。

## When to use

- 用户提出研究问题，需要设计问卷来量化某个态度 / 行为 / 需求
- 用户要做问卷预调研但还没成稿
- 用户拿来的草稿问卷需要按方法论修订（题序 / 偏差 / 量表）

不适用：用户想"发现未知问题"——那是访谈的活。问卷只确认和量化已知构念，不负责揭示未知。

## 输入

必填，缺一不可（缺则触发 Stop 条件）：

- **研究问题** `research_question`：一句话，要量化什么。例："设计学生是否愿意用 AI 合成样本工具做预调研"。
- **目标人群描述** `target_population`：谁在答题。例："国内高校设计类本科 / 研究生"。
- **问卷用途** `purpose`：`pre-research`（预调研 / 方向判断）或 `hypothesis-validation`（验证假设）。本工具默认且倡导 `pre-research`。

可选：样本量意向、已有草稿、必须覆盖的构念。

## 输出

写 `runs/<时间戳>/survey.json`，schema：

```json
{
  "research_question": "...",
  "target_population": "...",
  "purpose": "pre-research",
  "recommended_n": 60,
  "n_rationale": "...",
  "estimated_minutes": 4,
  "questions": [
    {
      "question_id": "Q1",
      "text": "...",
      "type": "single-choice | multi-select | likert | rating | nps | ranking | open",
      "options": ["..."] | null,
      "scale": {"points": 5, "low": "...", "high": "..."} | null,
      "construct_measured": "...",
      "required": true
    }
  ]
}
```

字段：

- `question_id`：全问卷唯一，建议 `Q1..Qn` 按题序。
- `type`：见题型表。
- `scale`：仅 likert / rating / nps 用；Likert 必须标 `low` / `high` 端点含义。
- `construct_measured`：这道题测的构念，取自下方词表。**这是 WF2 反推人群的入口，不能省。**

## 方法

### 题序（固定顺序，不乱排）

1. **筛选 / 人口统计**：短，开头。筛掉非目标人群。
2. **行为题**：用户做什么。在态度题之前建立行为上下文。
3. **态度 / 满意度题**：行为上下文建立后再问。
4. **开放题**：放最后。开放题费力，不能让它在核心题之前耗尽受访者。

### 题型

| type | 用于 | 注意 |
|---|---|---|
| single-choice | 互斥选项 | 选项要穷尽，必要时含 Other |
| multi-select | 多选适用项 | 不要用来排序，不要用于互斥项 |
| likert | 态度 / 同意度 / 满意度 | 方向一致（1 低 5 高），标端点 |
| rating | 单维测量（1-10） | 标明两端含义 |
| nps | 推荐意愿 | 0-10；Promoters 9-10 / Passives 7-8 / Detractors 0-6 |
| ranking | 相对重要性 | 限 5-7 项，认知负担大 |
| open | 解释 / 意外答案 | 少用，分析成本高 |

### 量表

- **Likert**：默认 5 点（更易答）；含中点；**必须标端点**："1=强烈不同意，5=强烈同意"；全问卷方向一致。
- **NPS**："你向朋友 / 同学推荐 [X] 的可能性？" 0-10；NPS = %Promoters − %Detractors；别当完整满意度用。
- **SUS**：逐字使用 10 题，不改题面；0-100，68 平均，>80 好。

### 避免偏差（每题自检）

- **引导题**："你多喜欢我们的产品？" → "你怎样描述使用我们产品的体验？"
- **双重题**："结账有多容易又多愉快？" → 拆两题。
- **加载语言**："你对我们的快速发货满意吗？" → 删"快速"。
- **回忆过载**："过去 12 个月多少次…" → 缩短回忆期更准。
- **术语**：用用户的词，不用内部产品名。

### 样本量

- 公式基准：±5% 误差 @95% 置信，大总体需 ~385 份。
- **合成场景缩放**：本工具生成合成受访者，`recommended_n` 远小于 385（建议 30–60），按人群原型数分配（每类约 5–10 人）。`n_rationale` 写清缩放理由。
- 简短原则：<5 分钟、<10–15 题；超过则完成率与质量双降。

## construct_measured 词表

受控词表 + 允许补充。每题必填，从下表取或自定义：

| 构念 | 示例题 |
|---|---|
| 基础身份 | 年级 / 专业 / 学校类型（筛选 + 分层用，非结果变量） |
| 行为 | 使用频率 / 做过没做过 |
| 需求 | 缺什么 / 卡在哪 |
| 满意度 | 对现状多满意 |
| 使用意愿 | 愿不愿用 |
| 付费意愿 | 愿不愿付 |
| 信任 | 信不信 / 担不担心 |
| 体验 | 用起来怎样 |

> **红线提醒**：满意度 / 使用意愿 / 推荐意愿是**结果变量**，只能作为问卷要测的构念（标在这里），**不能**提前塞给 persona 当背景——那是 WF2 的红线。基础身份类（年级 / 专业）是分层变量，可作 persona 背景。

## 验收标准（可机械检查）

不满足 = 未完成：

- [ ] 文件是合法 JSON，含 `research_question` / `target_population` / `purpose` / `recommended_n` / `questions`。
- [ ] 每题有 `question_id` 且全问卷唯一。
- [ ] 每题有非空 `construct_measured`。
- [ ] 所有 `type=likert` 题，`scale` 含 `low` 与 `high` 端点含义。
- [ ] `single-choice` / `multi-select` 题 `options` 非空；互斥题含 Other 或穷尽。
- [ ] 题序符合 筛选→行为→态度→开放（开放题不在前）。
- [ ] 题数 ≤ 15，`estimated_minutes` ≤ 5。
- [ ] 逐题过避免偏差自检（无引导 / 双重 / 加载 / 回忆过载 / 术语）。

## Stop 条件

触发即停，追问，不臆造：

- 无 `research_question` → 问"你想量化什么？一句话。"
- 无 `target_population` → 问"谁在填这份问卷？"
- 研究问题其实是"发现未知问题"（探索性）→ 建议先访谈，问卷不适用，说明原因。

## 红线

- 问卷文件 `purpose` 标注预调研 / 验证假设；本工具默认且倡导 `pre-research`。
- 全 pipeline 红线继承：后续所有输出（人群画像 / 数据集 / 报告）须标注 合成样本 / 样本量 / 置信度 / 仅供预调研。本步产出的是问卷设计本身，不属合成数据，但 `purpose` 字段为下游标注铺垫。

## 下一步

问卷就绪后进入 `workflows/02-audience-inference.md`：读 `survey.json` 的 `construct_measured`，反推影响回答的关键变量，划 5-8 类人群原型 + 比例。

## 示例

精简示例（完整文件见运行时产出）：

```json
{
  "research_question": "设计学生是否愿意用 AI 合成样本工具做预调研",
  "target_population": "国内高校设计类本科及研究生",
  "purpose": "pre-research",
  "recommended_n": 60,
  "n_rationale": "±5%@95% 基准 385；合成场景缩放至 60，分 6 类原型各约 10 人",
  "estimated_minutes": 4,
  "questions": [
    {"question_id":"Q1","text":"你目前的学习阶段？","type":"single-choice","options":["大一","大二","大三","大四","研究生"],"scale":null,"construct_measured":"基础身份","required":true},
    {"question_id":"Q2","text":"过去半年你做过几次问卷调研？","type":"rating","options":null,"scale":{"points":10,"low":"0 次","high":"10 次以上"},"construct_measured":"行为","required":true},
    {"question_id":"Q3","text":"我愿意用 AI 合成样本做预调研","type":"likert","options":null,"scale":{"points":5,"low":"强烈不同意","high":"强烈同意"},"construct_measured":"使用意愿","required":true},
    {"question_id":"Q4","text":"什么情况下你不敢用合成样本？","type":"open","options":null,"scale":null,"construct_measured":"信任","required":false}
  ]
}
```
