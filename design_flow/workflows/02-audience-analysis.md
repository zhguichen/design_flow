# Workflow 2：人群分析 (audience-analysis)

三个连续 Phase，把"问卷"变成"可进入模拟的人群依据"：

- **Phase A：人群反推** — 从 `construct_measured` 出发，划出会答出不同答案的人群原型。
- **Phase B：行为机制映射** — 给每个原型找到有证据分级、能被推翻的行为机制解释，而不是拍脑袋贴标签。
- **Phase C：任务摩擦映射** — 把机制落到具体任务环节，让"哪里最麻烦"这类题目有依据可查；同时预注册并封存假设，防止后面的模拟变成自证预言。

三个 Phase 顺序执行，每 Phase 后暂停验收再进下一个。按需从根 `SKILL.md` 加载；WF1 完成后由 pipeline 推进到本步。

## When to use

- `survey.json` 就绪，需要从问卷推导谁在答题、受什么机制影响、哪些任务环节存在摩擦。
- WF1 完成后由 pipeline 自动推进。
- 用户质疑"模拟人是否有依据"或"痛点怎么来的"。

不适用：`survey.json` 不存在或没有 `construct_measured` → 先完成 WF1。

## 输入

- `runs/<时间戳>/survey.json`（必须含每题 `construct_measured`）
- `references/behavior-mechanism-library.md`（Phase B 读取）
- `references/task-friction-framework.md`（Phase C 读取）

## 输出（三 Phase 产出）

| Phase | 产出文件 | 内容 |
|---|---|---|
| A | `archetypes.json` | 人群原型 + 场景覆盖计划 |
| B | `behavior_mechanisms.json` | 机制假设 + 证据等级 + 替代解释 + 证伪条件 |
| C | `task_frictions.json` + `hypotheses.json`（封存） | 任务摩擦分数/规则 + 预注册预测 |

---

## Phase A：人群反推

### 目标

从 `construct_measured` 反推"哪些变量会让不同人答出不同答案"，划出待机制校验的人群原型。原型不是人口统计学的排列组合，而是能解释回答差异的最小分组。

### 方法

**逐题问：谁会答得不一样**

对每道题问：这道题测的构念，什么样的人会答得不一样？差异来自身份、经验、资源、心理还是情境？哪些是结果变量（满意度/使用意愿/推荐意愿/付费意愿）——这些只能是被影响的后果，不能定义原型背景。

**用五类框架提取变量，而不是属性全排列**

变量要从研究问题里长出来：

| 类型 | 说明 | 示例 |
|---|---|---|
| 经验 | 是否做过、是否遇过这事 | 做过真实调研 / 遇过问卷没人填 |
| 情境 | 当下处境与压力 | 时间压力 / 毕业设计阶段 / 导师要求 |
| 心理 | 倾向与态度 | AI 信任 / 造假担心 / 风险偏好 |
| 资源 | 有什么可用 | 社交资源 / 预算 / 真实用户渠道 |
| 能力 | 掌握度与熟练度 | 研究方法掌握度 / AI 工具熟练度 |

每个变量追溯到至少一个 `question_id`。

**收敛到原型**

一个候选分组值不值得成为原型，看三条：能不能解释回答差异（不同原型对同一题会答出不同答案）、背景是否自洽（限制和经验之间不矛盾）、能不能在 Phase B 走完因果链并提出证伪条件。原型数落在 5-8 类比较合适——少于 5 覆盖不足，多于 8 会失去聚合意义，但这是经验区间，不是硬性门槛。

每个原型顺手写 2-4 个候选机制线索（时间压力/身份表达/习惯摩擦这类原因线索，不写结果变量），留给 Phase B 判断保留、合并还是删除。

**场景权重是分配，不是人口普查**

`scenario_weight` 合计 1.0，含义永远是"分配合成场景"，不是目标人群的现实比例。没有真实分布依据时，默认等权（`coverage-default`）——这不是偷懒，是诚实。四种权重来源：

- `real-data`：用户提供的可核验真实数据，`detail` 写清来源。
- `user-specified`：用户主动指定，`detail` 记录用户意图。
- `coverage-default`：无分布依据时的等权覆盖。
- `model-assumption`：模型压力测试用的权重，`detail` 必须明示是假设。

`simulation_plan` 默认 `mode=coverage`，每个原型至少 3 个变体。原型数确定后，按"原型数 × variants_per_archetype"算出建议的 `simulation_n`，**主动把这个数字告知用户并确认**："共 N 类原型，按每类至少 3 个变体算，建议生成 X 条模拟记录，要不要调整？"——不要算完就默默定稿。`survey.json` 里 `simulation_n` 已由用户指定的，核对是否够覆盖每类 3 个变体，不够就停下来问要不要加预算或合并场景，别悄悄削减覆盖。

### 输出 schema

精简示例（仅列 2 类，实际应有 5-8 类）。场景沿用 WF1 例 B：近半年购置家具的城市租房者选购摩擦研究。

```json
{
  "research_question": "近半年购置过家具的城市租房者，对家具选购过程中哪些环节摩擦最高",
  "target_population": "近半年购置过家具、居住在租赁房的 25-35 岁城市居民",
  "note": "合成样本 / 仅供预调研",
  "simulation_plan": {
    "mode": "coverage",
    "variants_per_archetype": 3,
    "simulation_n": 6,
    "weight_interpretation": "仅用于分配合成场景，不代表真实人群比例"
  },
  "archetypes": [
    {
      "archetype_id": "A1",
      "name": "预算受限的实用派租房者",
      "核心特征": "预算紧张，优先功能性，对质量真假和退换货顾虑大",
      "scenario_weight": 0.50,
      "weight_source": {
        "type": "coverage-default",
        "detail": "无真实分布依据，2 类原型等权覆盖"
      },
      "变量设定": [
        {"类型": "情境", "变量": "居住稳定性", "取值": "低（短租/合租）", "来源": ["Q1"]},
        {"类型": "资源", "变量": "家具预算", "取值": "低", "来源": ["Q1"]},
        {"类型": "经验", "变量": "退换货经历", "取值": "有过麻烦", "来源": ["Q4"]},
        {"类型": "心理", "变量": "质量不确定感", "取值": "高", "来源": ["Q4"]}
      ],
      "候选机制线索": ["损失规避", "资源稀缺", "风险感知"]
    },
    {
      "archetype_id": "A2",
      "name": "注重风格搭配的设计感租房者",
      "核心特征": "有审美诉求，但租房场景限制风格自由度，尺寸规划是主要痛点",
      "scenario_weight": 0.50,
      "weight_source": {
        "type": "coverage-default",
        "detail": "无真实分布依据，2 类原型等权覆盖"
      },
      "变量设定": [
        {"类型": "心理", "变量": "审美自我表达诉求", "取值": "高", "来源": ["Q2", "Q3"]},
        {"类型": "情境", "变量": "空间改造限制", "取值": "高（不能改墙/固定结构）", "来源": ["Q3"]},
        {"类型": "能力", "变量": "空间规划能力", "取值": "中低", "来源": ["Q4"]},
        {"类型": "经验", "变量": "家具买回尺寸不合经历", "取值": "有", "来源": ["Q4"]}
      ],
      "候选机制线索": ["身份表达", "空间控制感", "习惯摩擦"]
    }
  ]
}
```

### 完成前确认

- **结构与可追溯**：合法 JSON，`archetype_id` 唯一；每条`变量设定`的`来源`都能在 `survey.json` 找到对应 `question_id`。
- **权重记账**：所有 `scenario_weight` 合计 1.0（±0.001 容差），每个原型有 `weight_source.type/detail`；无真实依据时全是 `coverage-default` 且等权，不包装成现实分布。
- **不含结果变量**：`变量设定`与`候选机制线索`都不使用满意度/使用意愿/推荐意愿/付费意愿这类结果变量，也不出现"预期回答倾向"之类预写结果方向的字段——这类字段会让下游模拟提前知道"应该"答什么。
- **原型自洽且可推进**：每个原型的`核心特征`与`变量设定`不矛盾，有`候选机制线索`供 Phase B 判断。

### 该停下来问的情况

- `survey.json` 没有 `construct_measured` → 回 WF1。
- 反推不出 5 类以上有意义的变量 → 说明问卷覆盖不足，回 WF1 加题。
- 用户给的目标人群与研究问题矛盾 → 追问澄清。
- 用户指定的 `simulation_n` 明显撑不起每类 3 个变体 → 说明覆盖不足，问要不要加预算或合并场景。
- `survey.json` 的 `simulation_n` 为 `null`（WF1 未定）→ 原型数确定后主动报出建议的 `simulation_n` 并确认，不要默默按建议值定稿。

---

## Phase B：行为机制映射

### 目标

给每个通过 Phase A 的原型找到人文社科/心理学层面的行为机制解释，让场景具备"可检验的合理性"——不是证明这类人真实存在，也不是宣称现实比例，只是说明"为什么这个场景值得纳入模拟、以及什么证据会推翻它"。

### 方法

**先判断问卷的行为域，别默认技术接受**

读研究问题与 `construct_measured`，判断问卷主要涉及哪类人类行为：

| domain | 适用问卷 |
|---|---|
| `technology_tool_adoption` | 工具/AI/软件/平台是否被接受 |
| `product_purchase` | 产品购买/价格/品牌/所有权 |
| `spatial_experience` | 空间/环境/场所/展陈/交通/公共场景 |
| `visual_aesthetic_preference` | 视觉风格/审美/包装/品牌形象/符号偏好 |
| `service_participation` | 服务使用/参与/投诉/复购/推荐 |
| `public_social_design` | 公共设计/社会议题/制度信任/公平感 |
| `habit_lifestyle_change` | 习惯/生活方式/持续行为改变 |
| `need_expression` | 需求表达/表层需求/补偿性需求 |
| `survey_response_behavior` | 作答中的社会赞许/理解负担 |

同一问卷可以有多个 domain。空间体验优先考虑环境控制/拥挤/安全感/路径认知；审美偏好优先考虑身份表达/文化资本/熟悉性；产品购买不要强套 TAM——TAM/UTAUT 是给"工具是否被接受"这类问题用的，不是万能模板。

**读机制库，走一遍完整因果链**

对每个 archetype，从候选机制线索出发，在 `behavior-mechanism-library.md` 里找机制，走完这条链：

`环境/事件 → 社会处境 → 资源/能力限制 → 行为机制 → 表层需求 → 假设性潜在动机`

走不完这条链的类型（没有机制依据、不影响回答、场景不自洽、和别的类型重复）就该被排除或合并——回 Phase A 修改，别硬凑。

**每个机制诚实标注证据等级**

这是整个方法论里最容易被滥用的一步：机制库里的理论卡片本身不是目标场景的证据，只是解释框架。证据等级分三档：

- `user-evidence`：用户提供了访谈/观察/真实问卷，能指向具体材料。
- `cited-research`：有可核验的研究来源。
- `model-inference`：只依据机制库、问卷文本和模型推理——这是本 pipeline 大多数机制会落在的档位，承认这一点比硬说"supported"更有用。

对应的合理性只有三档：`supported`（有直接相关的 user-evidence 或 cited-research，仍不代表现实比例）、`plausible`（因果链连贯但主要靠推断）、`speculative`（依赖强假设或有同样有力的替代解释）。`model-inference` 封顶 `plausible`，不能到 `supported`。

每个机制还要写一个真正有竞争力的替代解释，和一个"什么样的真实观察会推翻这个机制"——这两项不是形式，是让机制保持可证伪。

**需求真实性只是解释假设，不是事实判定**

| 标签 | 含义 |
|---|---|
| `real_need` | 由真实约束/痛点直接产生；只有 user-evidence / cited-research 支持时才能用 |
| `surface_need` | 表层说法真实但不完整 |
| `contextual_need` | 特定事件/压力下才强 |
| `defensive_need` | 为避免指责或规范风险 |
| `socially_desirable_need` | 听起来专业/正确 |
| `compensatory_need` | 补偿能力/资源/信心不足 |
| `pseudo_need` | 场景弱/行动意愿弱/无稳定触发 |

`model-inference` 时不能标 `real_need`——没有真实证据支撑"真实"这个判断。

### 输出 schema

原来的机制对象平铺 19 个字段，读起来像填表。这里按"要回答的问题"分成几组：机制在说什么（`logic`）、它在解释什么需求（`need_reading`）、证据有多硬（`evidence`）、这个解释的边界和反例在哪（`scrutiny`）。信息量不变，负担降低。

延续同一家具选购场景，A1 和 A2 各对应一个机制：

```json
{
  "research_question": "近半年购置过家具的城市租房者，对家具选购过程中哪些环节摩擦最高",
  "target_population": "近半年购置过家具、居住在租赁房的 25-35 岁城市居民",
  "note": "合成样本 / 仅供预调研 / 机制是假设，不证明人群真实存在或现实比例",
  "questionnaire_domains": ["product_purchase", "spatial_experience"],
  "mechanisms": [
    {
      "mechanism_id": "M1",
      "name": "损失规避下的质量风险感知",
      "domain": "product_purchase",
      "applicable_archetypes": ["A1"],
      "affects_questions": ["Q4", "Q5"],
      "logic": {
        "theory_basis": ["M-LOSS-AVERSION", "M-RISK-PERCEPTION"],
        "mechanism_logic": "线上购买无法触摸实物、退货运费自理、租房家具使用周期不确定，使预算有限的个体把选购决策评估为高损失风险；这类人倾向高估质量失败的后果，在质量/材质判断环节产生强摩擦。"
      },
      "need_reading": {
        "surface_need": "买到质量可靠、不会后悔的家具",
        "hypothesized_latent_motive": "避免在有限预算下做出让自己后悔的决策，保护稀缺资源",
        "demand_authenticity": ["surface_need", "contextual_need"]
      },
      "evidence": {
        "level": "model-inference",
        "note": "基于机制库 M-LOSS-AVERSION / M-RISK-PERCEPTION 推断；无该群体一手数据。",
        "plausibility": "plausible"
      },
      "scrutiny": {
        "scope": "适用于预算低、有过退换货麻烦、质量不确定感高的租房者；预算充足或对退换货无顾虑者不归入。",
        "alternative_explanation": "质量摩擦也可能主要来自品牌认知不足，而非损失规避。",
        "falsification_probe": "若访谈发现预算低的租房者质量焦虑并不显著高于预算充足者，则不支持该机制。"
      }
    },
    {
      "mechanism_id": "M2",
      "name": "空间控制感受限下的风格摩擦",
      "domain": "spatial_experience",
      "applicable_archetypes": ["A2"],
      "affects_questions": ["Q3", "Q4", "Q6"],
      "logic": {
        "theory_basis": ["M-IDENTITY-EXPRESSION", "M-SPATIAL-CONTROL"],
        "mechanism_logic": "租房不可改墙/改固定结构的硬性限制，压缩了审美自我表达的空间；有强风格诉求且曾因尺寸踩坑的个体，在尺寸规划和风格搭配判断上会产生更高摩擦，因为每次选择都是在约束内争取认同感。"
      },
      "need_reading": {
        "surface_need": "买到尺寸合适、风格搭调的家具",
        "hypothesized_latent_motive": "在受限的租房空间里维持对生活环境的掌控感和自我认同",
        "demand_authenticity": ["surface_need", "contextual_need", "compensatory_need"]
      },
      "evidence": {
        "level": "model-inference",
        "note": "基于机制库 M-IDENTITY-EXPRESSION / M-SPATIAL-CONTROL 推断；无该群体一手数据。",
        "plausibility": "plausible"
      },
      "scrutiny": {
        "scope": "适用于审美自我表达诉求高、空间改造受限强、有尺寸踩坑经历的租房者；对居住风格无要求或接受将就的用户不归入。",
        "alternative_explanation": "风格摩擦也可能主要来自选择过多（选择悖论），而非身份表达诉求。",
        "falsification_probe": "若访谈发现有强风格诉求的租房者和无诉求者在尺寸/搭配摩擦上无显著差异，则不支持该机制。"
      }
    }
  ],
  "archetype_mechanism_map": {
    "A1": ["M1"],
    "A2": ["M2"]
  }
}
```

### 完成前确认

- **domain 路由合理**：`questionnaire_domains` 不是默认全套 `technology_tool_adoption`（除非问卷真的只测工具接受）；每个 domain 都能在问卷文本里找到对应依据。
- **结构完整且分组清楚**：每个 mechanism 含 `logic`/`need_reading`/`evidence`/`scrutiny` 四组，以及顶层的 `mechanism_id`/`name`/`domain`/`applicable_archetypes`/`affects_questions`。`affects_questions` 能在 `survey.json` 找到，`applicable_archetypes` 能在 `archetypes.json` 找到。
- **每个原型都有机制覆盖**：`archetype_mechanism_map` 完整；某个原型实在配不出连贯机制，回 Phase A 修改或删除该原型，不要硬塞一个凑数机制。
- **证据纪律**：`evidence.level=model-inference` 时 `plausibility` 只能是 `plausible`/`speculative`，且 `demand_authenticity` 不含 `real_need`；`user-evidence`/`cited-research` 时 `evidence.note` 要指向具体材料或引用来源。
- **不预写答案方向**：文件不含"likely_behavior"/"answer_implications"之类预写结果方向的字段。

### 该停下来问的情况

- 某个 archetype 找不到连贯、可证伪的机制假设 → 回 Phase A 修改或删除该原型。
- 问卷过于泛泛，判断不出行为域 → 回 WF1 补充研究问题或构念。

---

## Phase C：任务摩擦映射

### 目标

把 Phase B 的机制链落到具体任务环节，让"哪个环节更麻烦 / 哪个功能更优先 / 哪些阻力最大"这类题目有可追溯的依据——从任务场景和机制推导，不从性格直接猜。同时预注册并封存 `hypotheses.json`，为 WF5 的假设对照做准备。

### 方法

**先找出哪些题需要摩擦依据**

读 `survey.json`，痛点题（最麻烦/最担心）、行为题（过去做了什么）、优先级题（排序/最想解决）、使用边界题（什么情况下接受/拒绝）、开放题（为什么/最担心什么），这些题的答案后续都要依据 `task_frictions.json`，不能凭性格随意回答。

**定义任务范围，映射到稳定维度**

先按研究对象定义任务范围（例：家具选购不是"买不买"一个任务，而是"发现需求→测量规划→风格选择→质量判断→下单→配送安装→售后"这条链），再把环节映射到 `references/task-friction-framework.md` 的稳定维度（如习惯改变→`habit_disruption`，安全风险→`risk_safety`，空间占用→`space_environment`，价格损失→`money_loss`，维护售后→`maintenance_aftercare`，过程控制→`identity_control`）。

**打分要能追溯到具体变量和机制，不能人格直推**

对每个 archetype、每个相关维度打 1-5 分，分数必须由 Phase A 的`变量设定`+ Phase B 的 `mechanism_ids` + 目标场景的具体任务共同推导出来。

不要写"谨慎型所以安全摩擦高"这种人格直推。要写：

`与孩子同住 + 经常做饭 + 火/刀/热油风险 + 照护责任 → risk_safety=5`

**给每道任务型题写作答规则**

`question_friction_rules` 说明从哪个摩擦字段作答、如何把分数转成答案、哪些情况允许"不确定"、同一 archetype 内如何做小幅变体：

- ranking：按 friction score 从高到低排序，允许相邻项交换
- multi-select：选 score≥4 的维度对应选项，最多加 1 个 score=3 的次要项
- open：解释 top friction 的 drivers，不写空泛态度
- likert pain：score 1-2 → 低，3 → 中，4-5 → 高

**置信度反映推导强度，不是真实比例**

- `high`：任务场景具体、变量清楚、多题受影响
- `medium`：机制合理，但依赖场景假设
- `low`：高度个人口味/文化偏好/偶然经历，需真人验证

**预注册并封存假设**

基于前面三步的产出写 `hypotheses.json`，每条假设要能在 WF5 用 `stats.json` 检查，不写无法证伪的泛泛判断。写完把 `status` 设为 `sealed`。从此到 WF4 完成之前：WF3/WF4 的输入清单不得包含 `hypotheses.json`，不把 `predicted_pattern` 复制进任何下游文件，模拟结果不符合假设也不重生成——这条红线是整个方法论防自证预言的核心，比其他检查项都重要。

### 输出 schema

延续同一家具选购场景，A1 和 A2 使用 Phase B 产出的机制推导各自摩擦分。

**`task_frictions.json`**：

```json
{
  "research_question": "近半年购置过家具的城市租房者，对家具选购过程中哪些环节摩擦最高",
  "target_population": "近半年购置过家具、居住在租赁房的 25-35 岁城市居民",
  "note": "合成样本 / 仅供预调研 / 任务摩擦为推导依据而非真实个体证明",
  "task_scope": "家具选购：发现需求→测量/空间规划→风格搭配判断→质量/材质判断→下单→配送安装→退换售后",
  "friction_dimensions": [
    {
      "dimension_id": "F1",
      "name": "质量判断摩擦",
      "base_dimension": "risk_safety",
      "description": "线上无法触摸实物、材质真假难辨、耐用性不确定带来的购前风险感",
      "related_questions": ["Q4", "Q5"]
    },
    {
      "dimension_id": "F2",
      "name": "尺寸与空间规划摩擦",
      "base_dimension": "space_environment",
      "description": "租房空间不规则、无法改造，导致测量和规划环节费力且容易出错",
      "related_questions": ["Q4", "Q6"]
    },
    {
      "dimension_id": "F3",
      "name": "风格搭配判断摩擦",
      "base_dimension": "identity_control",
      "description": "已有家具风格混乱或无法改造硬装，导致风格判断决策成本高",
      "related_questions": ["Q3", "Q4", "Q6"]
    }
  ],
  "archetype_friction_map": {
    "A1": {
      "top_friction_dimensions": ["F1"],
      "scores": {
        "F1": {
          "score": 5,
          "drivers": ["租房预算有限", "退换货成本高", "线上无法验证材质"],
          "mechanism_ids": ["M1"],
          "affects_questions": ["Q4", "Q5"],
          "confidence": "high"
        },
        "F2": {
          "score": 3,
          "drivers": ["合租空间有限", "不常搬家所以规划不熟"],
          "mechanism_ids": ["M1"],
          "affects_questions": ["Q4"],
          "confidence": "medium"
        },
        "F3": {
          "score": 2,
          "drivers": ["对风格要求低，功能优先"],
          "mechanism_ids": [],
          "affects_questions": ["Q4"],
          "confidence": "low"
        }
      },
      "low_confidence_items": ["F3"]
    },
    "A2": {
      "top_friction_dimensions": ["F2", "F3"],
      "scores": {
        "F1": {
          "score": 3,
          "drivers": ["有退换货顾虑但预算相对宽裕"],
          "mechanism_ids": [],
          "affects_questions": ["Q4"],
          "confidence": "medium"
        },
        "F2": {
          "score": 5,
          "drivers": ["租房不可改造", "曾买回尺寸不合", "空间规划能力中低"],
          "mechanism_ids": ["M2"],
          "affects_questions": ["Q4", "Q6"],
          "confidence": "high"
        },
        "F3": {
          "score": 4,
          "drivers": ["审美自我表达诉求高", "已有家具风格混杂", "无法改硬装导致软装压力大"],
          "mechanism_ids": ["M2"],
          "affects_questions": ["Q3", "Q4", "Q6"],
          "confidence": "high"
        }
      },
      "low_confidence_items": []
    }
  },
  "question_friction_rules": {
    "Q4": {
      "question_intent": "识别选购过程中最麻烦的环节（多选，最多3项）",
      "answer_from": ["top_friction_dimensions"],
      "rule": "从 score>=4 的摩擦维度对应选项中选择，允许加 1 个 score=3 的次要项；score<=2 的维度不选。"
    },
    "Q6": {
      "question_intent": "开放题：有什么选购困难上面没提到",
      "answer_from": ["top_friction_dimensions"],
      "rule": "解释 top friction 的 drivers，写具体场景（如'买回来发现窗帘轨道占了30cm'），不写空泛态度。"
    }
  }
}
```

**`hypotheses.json`**：

```json
{
  "research_question": "近半年购置过家具的城市租房者，对家具选购过程中哪些环节摩擦最高",
  "created_before_simulation": true,
  "status": "sealed",
  "note": "预注册假设 / 不得供 WF3 或 WF4 读取 / 仅供 WF5 对照",
  "hypotheses": [
    {
      "hypothesis_id": "H1",
      "target_questions": ["Q4"],
      "comparison": {"archetype_ids": ["A1", "A2"]},
      "predicted_pattern": "A1 选择'质量/材质难以判断'的比例高于 A2；A2 选择'尺寸测量和空间规划'及'风格搭配判断'的比例高于 A1",
      "basis": {"mechanism_ids": ["M1", "M2"], "friction_dimension_ids": ["F1", "F2", "F3"]},
      "alternative_explanation": "差异也可能来自购买渠道（线上 vs 线下）而非预算或风格诉求",
      "falsification_rule": "若 A1 和 A2 在'质量/材质'与'尺寸规划/风格搭配'两类选项的选择率无显著差异，则不支持 H1",
      "confidence": "medium"
    }
  ]
}
```

### 完成前确认

- **结构完整**：`task_frictions.json` 含 `task_scope`/`friction_dimensions`/`archetype_friction_map`/`question_friction_rules`；每个 archetype 出现在 `archetype_friction_map` 中。
- **打分可追溯**：每个 score 在 1-5 之间，都带 `drivers`/`mechanism_ids`/`affects_questions`/`confidence`；`mechanism_ids` 能在 `behavior_mechanisms.json` 找到，`affects_questions` 能在 `survey.json` 找到。
- **覆盖所有任务型题**：问卷里所有痛点/排序/开放/使用边界题都在 `question_friction_rules` 里有规则；不含"likely_pain_answer_pattern"之类预期答案字段。
- **假设正确封存**：`hypotheses.json` 存在，`created_before_simulation=true`、`status=sealed`；每条假设有唯一 `hypothesis_id`、可检验的 `predicted_pattern`、`basis`、`alternative_explanation`、`falsification_rule`、`confidence`，且都能追溯到上游文件。

### 该停下来问的情况

- 没有 `behavior_mechanisms.json` → 先完成 Phase B。
- 问卷没有任何行为/痛点/任务题 → 回 WF1 重写问卷。
- 某个 archetype 的 top friction 推不出来（变量或机制不够） → 回 Phase A/B 修改。

---

## 跨 Phase 红线

三个 Phase 都继承 `SKILL.md` 的跨 workflow 红线（结果变量不作背景、场景权重不是现实比例、假设封存不可读）。本步独有的提醒：

- **Phase A 输出是候选，不是定论**：Phase B 有权要求某个原型回退合并、删除或重写；没通过 Phase B 的原型不进 WF3。
- **`model-inference` 不能升级为 `supported`**：没有真实数据支撑时，`plausibility` 最高到 `plausible`——这条在 Phase B 和 WF5 引用机制时都适用。

## 下一步

三 Phase 全部通过后，进入 `workflows/03-persona-generation.md`：读取 `archetypes.json` + `behavior_mechanisms.json` + `task_frictions.json`，展开具体模拟受访者。**WF3 不得读取同目录的 `hypotheses.json`**；后者只在 WF5 首次加载。
