# Workflow 2.6：任务摩擦映射 (task-friction-mapping)

在行为机制和 persona 生成之间加入“任务摩擦”推导层。目标是让“哪个环节更麻烦 / 哪个功能更优先 / 哪些阻力最大”这类个性化题目，有可追溯依据，而不是让 agent 从性格随便猜。

按需从根 `SKILL.md` 加载。依赖 WF1 的 `survey.json`、WF2 的 `archetypes.json`、WF2.5 的 `behavior_mechanisms.json`。需要摩擦维度时读取 `references/task-friction-framework.md`。

## When to use

- 问卷包含痛点、麻烦环节、功能优先级、阻力、使用边界、开放题等问题
- 用户担心“每个人觉得麻烦的环节不同，模拟人凭什么这么答”
- `behavior_mechanisms.json` 已就绪，需要把机制落到具体任务环节
- WF2.5 完成后由 pipeline 自动推进到本步

不适用：问卷只测非常简单的总体态度，且没有任何任务/痛点/优先级问题。但一般设计调研都应包含任务摩擦题。

## 输入

- `runs/<时间戳>/survey.json`
- `runs/<时间戳>/archetypes.json`
- `runs/<时间戳>/behavior_mechanisms.json`
- `references/task-friction-framework.md`

## 输出

写 `runs/<时间戳>/task_frictions.json`，schema：

```json
{
  "research_question": "...",
  "target_population": "...",
  "note": "合成样本 / 仅供预调研 / 任务摩擦为推导依据而非真实个体证明",
  "task_scope": "厨房机器人：备菜、烹饪、火候安全、清洁维护、空间收纳",
  "friction_dimensions": [
    {
      "dimension_id": "F1",
      "name": "清洁维护摩擦",
      "base_dimension": "maintenance_aftercare",
      "description": "清洗、拆装、维护、耗材和售后带来的后续负担",
      "related_questions": ["Q4", "Q5", "Q13", "Q14"]
    }
  ],
  "archetype_friction_map": {
    "A1": {
      "top_friction_dimensions": ["F1", "F2"],
      "scores": {
        "F1": {
          "score": 5,
          "drivers": ["工作日时间压力高", "希望减少收拾负担", "担心省事变成新家务"],
          "mechanism_ids": ["M1"],
          "affects_questions": ["Q4", "Q5", "Q14"],
          "confidence": "high"
        }
      },
      "likely_pain_answer_pattern": "优先选择清洁、备菜、减少收拾；开放题会担心维护麻烦。",
      "low_confidence_items": []
    }
  },
  "question_friction_rules": {
    "Q4": {
      "question_intent": "识别当前痛点",
      "answer_from": ["top_friction_dimensions"],
      "rule": "多选题从 score>=4 的摩擦维度对应选项中选择，允许一个 persona-specific 次要项。"
    }
  }
}
```

## 方法

### 第一步：识别任务型问题

读 `survey.json`，找出会触发任务摩擦的题：

- 痛点题：最麻烦、最困难、最担心、最不愿意
- 行为题：过去做了什么、频率、当前解决方式
- 优先级题：排序、最想解决、功能重要性
- 使用边界题：什么情况下接受/拒绝
- 开放题：为什么、什么情况下、最担心什么

这些题后续不能只按性格回答，必须用 `task_frictions.json`。

### 第二步：定义任务范围与摩擦维度

根据研究对象定义任务范围。例如厨房机器人不是“买不买机器人”一个任务，而是：

`备菜 -> 烹饪 -> 火候/安全 -> 上桌 -> 清洁 -> 收纳 -> 维护`

再把这些环节映射到 `references/task-friction-framework.md` 的稳定维度，例如：

- 清洁维护摩擦 -> `maintenance_aftercare`
- 安全风险摩擦 -> `risk_safety`
- 空间占用摩擦 -> `space_environment`
- 过程控制摩擦 -> `identity_control`
- 价格损失摩擦 -> `money_loss`
- 习惯改变摩擦 -> `habit_disruption`

### 第三步：为每个 archetype 打摩擦分

对每个 archetype，每个相关维度给 1-5 分。分数必须由以下内容共同推导：

- WF2 的 `变量设定`
- WF2.5 的 `mechanism_ids`
- 目标场景里的具体任务
- 可影响问卷题目的具体理由

不要写“谨慎型所以安全摩擦高”这种人格直推。要写：

`与孩子同住 + 经常做饭 + 火/刀/热油风险 + 照护责任 -> risk_safety=5`

### 第四步：生成题目作答规则

对每一道任务型问题写 `question_friction_rules`：

- `answer_from`：从哪个摩擦字段作答
- `rule`：如何从分数转成答案
- `uncertainty_rule`：哪些情况下允许“不确定”
- `variation_rule`：同一 archetype 内如何做小幅差异

示例：

- ranking：按 friction score 从高到低排序，允许相邻项交换
- multi-select：选择 score>=4 的维度对应选项，最多加 1 个 score=3 的次要项
- open：解释 top friction 的 drivers，不写空泛态度
- likert pain/severity：score 1-2 -> 低，3 -> 中，4-5 -> 高

### 第五步：标置信度

任务摩擦的置信度不是“真实比例”，而是“推导强度”：

- `high`：任务场景具体、驱动变量清楚、多题会受影响
- `medium`：机制合理，但仍依赖场景假设
- `low`：高度个人口味/文化偏好/偶然经历，必须真人验证

## 红线

- 不从性格直接推痛点；必须从任务场景、行为经验、环境限制、资源能力和机制链推导。
- 不把“每个可能麻烦的环节”都塞进 top friction；只保留 score 高、会影响问卷回答的摩擦。
- 任务摩擦不证明真实个体一定这么想，只说明这个 archetype 在该任务场景下有合理作答依据。
- 没有 `task_frictions.json` 时，WF4 不能回答痛点/优先级/麻烦环节题。

## 验收标准（可机械检查）

- [ ] 文件是合法 JSON，含 `research_question` / `target_population` / `task_scope` / `friction_dimensions` / `archetype_friction_map` / `question_friction_rules`。
- [ ] `friction_dimensions` 非空，每个含 `dimension_id` / `name` / `base_dimension` / `related_questions`。
- [ ] 每个 archetype 都在 `archetype_friction_map` 中出现。
- [ ] 每个 score 在 1-5 之间，并含 `drivers` / `mechanism_ids` / `affects_questions` / `confidence`。
- [ ] `mechanism_ids` 均能在 `behavior_mechanisms.json` 找到。
- [ ] `affects_questions` 与 `related_questions` 均能在 `survey.json` 找到。
- [ ] 问卷中所有痛点/排序/开放/使用边界题，在 `question_friction_rules` 中有规则。
- [ ] 文件级 `note` 含“合成样本”与“预调研”。

## Stop 条件

- 无 `behavior_mechanisms.json` → 回 WF2.5。
- 问卷没有任何行为/痛点/任务题，只剩“是否愿意” → 回 WF1 重写问卷。
- 某 archetype 的 top friction 无法从变量和机制推导 → 回 WF2 或 WF2.5 修改。

## 下一步

任务摩擦就绪后进入 `workflows/03-persona-generation.md`。WF3 必须读取 `task_frictions.json`，为每个 respondent 写入 `task_friction_profile`，并让痛点、功能优先级、开放题作答从该 profile 中长出来。
