# Workflow 2.5：行为机制映射 (behavior-mechanism-mapping)

在人群原型和具体 persona 之间加入“人文社科 / 心理学行为机制”推导层。目标不是穷举所有可能人群，而是只保留由真实研究逻辑支撑、会影响问卷回答、且在目标群体中现实自洽的存在类型。

按需从根 `SKILL.md` 加载。依赖 WF1 的 `survey.json` 与 WF2 的 `archetypes.json`。需要机制路由时读取 `references/behavior-mechanism-library.md`。

## When to use

- `archetypes.json` 已就绪，需要判断这些原型为什么真实合理存在
- 用户质疑“模拟人是否有依据”
- 问卷不限于技术接受，可能涉及产品购买、空间体验、视觉审美、服务参与、公共设计、生活方式或潜在需求
- WF2 完成后由 pipeline 自动推进到本步

不适用：没有问卷或没有人群原型。先回 WF1 / WF2。

## 输入

- `runs/<时间戳>/survey.json`
- `runs/<时间戳>/archetypes.json`
- `references/behavior-mechanism-library.md`

## 输出

写 `runs/<时间戳>/behavior_mechanisms.json`，schema：

```json
{
  "research_question": "...",
  "target_population": "...",
  "note": "合成样本 / 仅供预调研 / 机制为推导依据而非真实比例证明",
  "questionnaire_domains": ["technology_tool_adoption", "need_expression"],
  "mechanisms": [
    {
      "mechanism_id": "M1",
      "name": "资源不足下的替代性应对",
      "domain": "need_expression",
      "theory_basis": ["M-STRESS-COPING", "M-SCARCITY"],
      "mechanism_logic": "deadline 与样本渠道不足使调研任务被评估为威胁；当个体资源不足时，会寻找低成本替代性应对方式。",
      "applicable_archetypes": ["A1", "A3"],
      "trigger_environment": ["deadline", "找不到真实受访者", "回收质量不可控"],
      "actor_conditions": ["时间压力高", "真实用户渠道低", "方法掌握度中低"],
      "surface_need": "提高调研效率",
      "latent_motive": "缓解调研无法完成、作业或毕设被否定的压力",
      "demand_authenticity": ["surface_need", "contextual_need", "compensatory_need"],
      "likely_behavior": "愿意把合成样本用于预调研，但付费意愿和规范信心有限",
      "answer_implications": {"使用意愿": "高", "信任": "中", "规范担忧": "中到高", "付费意愿": "低到中"},
      "affects_questions": ["Q7", "Q8", "Q9", "Q10", "Q11"],
      "confidence": "medium",
      "inference_type": "theory-guided inference",
      "inclusion_reason": "该类型由目标群体处境、问卷痛点题和压力/稀缺机制共同推导成立。",
      "exclusion_boundary": "仅有时间压力但不缺渠道或不关心调研质量的人，不归入该机制。",
      "validation_probe": "真实访谈中追问：你说想提高效率，是因为时间不够、找不到人，还是因为你认为合成样本本身更好？"
    }
  ],
  "archetype_mechanism_map": {
    "A1": ["M1"]
  }
}
```

## 方法

### 第一步：识别问卷行为域

读 `survey.json` 的研究问题、题目和 `construct_measured`，判断这份问卷主要在问哪类人类行为问题。不要默认是技术接受。

可选行为域：

| domain | 适用问卷 |
|---|---|
| `technology_tool_adoption` | 工具、AI、软件、平台、数字服务是否被接受 |
| `product_purchase` | 产品购买、价格、品牌、包装、所有权 |
| `spatial_experience` | 空间、环境、场所、展陈、交通、校园/公共场景 |
| `visual_aesthetic_preference` | 视觉风格、审美、包装、品牌形象、符号偏好 |
| `service_participation` | 服务使用、参与、投诉、复购、推荐 |
| `public_social_design` | 公共设计、社会议题、制度信任、公平感 |
| `habit_lifestyle_change` | 习惯、生活方式、持续行为改变 |
| `need_expression` | 需求表达、表层需求、潜在动机、补偿性需求 |
| `survey_response_behavior` | 问卷作答中的不确定、社会赞许、理解/回忆负担 |

同一问卷可以有多个 domain。

### 第二步：匹配机制，不套模板

读取 `references/behavior-mechanism-library.md`，为每个 domain 选机制。机制必须回答：

- 什么环境触发它？
- 什么样的人受它影响？
- 它解释什么选择？
- 表层需求是什么？
- 潜在动机是什么？
- 会影响哪些题目？

如果是产品购买，不要强行用 TAM；如果是空间体验，优先环境控制、拥挤、安全感、隐私、路径认知；如果是审美偏好，优先身份表达、文化资本、熟悉性、情绪联想。

### 第三步：推导“有逻辑存在”的人群类型

对 WF2 的每个 archetype 做推导链：

`环境/事件 -> 社会处境 -> 资源/能力限制 -> 行为机制 -> 表层需求 -> 潜在动机 -> 作答倾向`

只保留能走完这条链的类型。不要把所有可能组合都放进来。没有机制支撑、不会影响回答、现实不自洽、与其他类型重复的组合要排除或合并。

### 第四步：判断需求真实性

每个机制至少标一个 `demand_authenticity`：

- `real_need`：由真实约束/痛点直接产生
- `surface_need`：表层说法真实但不完整
- `contextual_need`：特定事件或压力下才强
- `defensive_need`：为了避免指责或规范风险
- `socially_desirable_need`：听起来专业/正确
- `compensatory_need`：补偿能力、资源或信心不足
- `pseudo_need`：场景弱、行动意愿弱或没有稳定触发

### 第五步：置信度与验证追问

每个机制给 `confidence`：

- `high`：机制与主题直接匹配，且问卷里有多题支撑
- `medium`：机制合理，会影响回答，但主要来自场景推断
- `low`：推断较弱，只能作为待验证假设；弱到不影响回答时应排除

每个机制必须给 `validation_probe`，用于后续少量真人访谈或真实问卷校准。

## 红线

- 不把机制当作真实比例证明。机制说明“为什么合理存在”，不说明“现实占多少”。
- 不穷举所有可能性。只纳入有机制链、能影响回答、现实自洽的类型。
- 不默认技术接受模型。根据问卷 domain 路由机制。
- 不用结果变量定义机制或 persona。满意度 / 使用意愿 / 付费意愿等仍然是结果，不是背景。
- 没有机制支撑的人群原型不能进入 WF3；要回 WF2 合并、删除或重写。

## 验收标准（可机械检查）

- [ ] 文件是合法 JSON，含 `research_question` / `target_population` / `questionnaire_domains` / `mechanisms` / `archetype_mechanism_map`。
- [ ] `questionnaire_domains` 非空，且不全部默认为 `technology_tool_adoption`，除非问卷确实只问技术/工具接受。
- [ ] 每个 mechanism 含 `mechanism_id` / `name` / `domain` / `theory_basis` / `mechanism_logic` / `applicable_archetypes` / `surface_need` / `latent_motive` / `demand_authenticity` / `answer_implications` / `affects_questions` / `confidence` / `inclusion_reason` / `exclusion_boundary` / `validation_probe`。
- [ ] `affects_questions` 均能在 `survey.json` 找到。
- [ ] `applicable_archetypes` 均能在 `archetypes.json` 找到。
- [ ] 每个 archetype 至少被一个机制覆盖。
- [ ] 每个机制的 `inclusion_reason` 写出“环境/处境/限制/机制”链。
- [ ] 文件级 `note` 含“合成样本”与“预调研”。

## Stop 条件

- 无 `survey.json` 或 `archetypes.json` → 回对应上游。
- 某 archetype 找不到机制支撑 → 回 WF2 修改或删除该原型。
- 问卷过于泛泛，无法判断行为域 → 回 WF1 补充研究问题或构念。

## 下一步

机制映射就绪后进入 `workflows/026-task-friction-mapping.md`。WF2.6 必须读取 `behavior_mechanisms.json`，把机制链进一步落到具体任务环节、痛点维度和作答规则，产出 `task_frictions.json`。通过 WF2.6 后，才进入 WF3 展开具体模拟受访者。
