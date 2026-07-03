# Workflow 1：问卷设计 (survey-design)

产出一份题序合理、量表可读、避免常见偏差的问卷，每题带 `construct_measured`——这是 WF2 反推人群的唯一入口，本步最重要的事就是把它填对。

按需从根 `SKILL.md` 加载。不建议单独使用：人群反推依赖本步的 `construct_measured`，跳过本步会让下游无从下手。

## When to use

- 用户提出研究问题，需要设计问卷来量化某个态度 / 行为 / 需求。
- 用户要做问卷预调研但还没成稿。
- 用户拿来的草稿问卷需要按方法论修订（题序 / 偏差 / 量表）。

不适用：用户想"发现未知问题"——那是访谈的活，问卷只确认和量化已知构念，不负责揭示未知。遇到这种请求，说明原因并建议先做定性访谈。

## 先弄清楚三件事

问卷设计能不能开始，取决于用户能不能回答三个问题。缺一个就停下来问，不要猜：

- **要量化什么**（`research_question`）：一句话说清楚。
- **谁在填**（`target_population`）：必须包含行为或经历，不能只有人口统计。"25-35岁"回答不了"这些人为什么会答出不同答案"；"近半年购置过家具的城市租房者"才行。
- **用来干什么**（`purpose`）：`pre-research`（方向判断）还是 `hypothesis-validation`（验证假设）。本工具默认且倡导 `pre-research`——如果用户想要的其实是发表级验证，提醒他们合成样本达不到这个标准。

## 方法

### 题序：筛选 → 行为 → 态度 → 开放

这个顺序不是习惯，是有代价的：开放题费力，放前面会在核心题之前耗尽受访者的耐心；态度题需要先建立行为上下文才有意义，问"你满意吗"之前受访者得先说清楚"你做了什么"。

1. 筛选 / 人口统计（短，开头，筛掉非目标人群）
2. 行为题（用户做了什么，建立上下文）
3. 态度 / 满意度题（有了行为上下文再问）
4. 开放题（放最后）

### 题型：按测量目的选，不按方便选

| type | 用于 | 注意 |
|---|---|---|
| single-choice | 互斥选项 | 选项要穷尽，必要时含 Other |
| multi-select | 多选适用项 | 不要用来排序，不要用于互斥项 |
| likert | 态度 / 同意度 / 满意度 | 方向一致（1 低 5 高），标端点 |
| rating | 单维测量（1-10） | 标明两端含义 |
| nps | 推荐意愿 | 0-10；Promoters 9-10 / Passives 7-8 / Detractors 0-6 |
| ranking | 相对重要性 | 限 5-7 项，认知负担大 |
| open | 解释 / 意外答案 | 少用，分析成本高 |

Likert 默认 5 点（更易答，含中点），必须标端点含义，全问卷方向一致。NPS 只测推荐意愿，别当完整满意度用。若要用 SUS，逐字使用官方 10 题，不改题面。

### 逐题过一遍偏差自检

每道题问自己：这题会不会引导受访者答某个方向？是不是把两件事塞进一道题？有没有加载性形容词？回忆期是不是太长导致记不准？用的是不是内部术语而不是用户自己的话？

| 偏差 | 反例 | 改法 |
|---|---|---|
| 引导题 | "你多喜欢我们的产品？" | "你怎样描述使用我们产品的体验？" |
| 双重题 | "结账有多容易又多愉快？" | 拆两题 |
| 加载语言 | "你对我们的快速发货满意吗？" | 删"快速" |
| 回忆过载 | "过去 12 个月多少次…" | 缩短回忆期 |
| 术语 | 用内部产品名 | 换成用户自己的词 |

### 篇幅：≤15 题，≤5 分钟

超出这个量，完成率和作答质量都会掉。如果用户坚持要更长的问卷，不要默默照做——直接说明代价（"题目越多，后半段答题质量越可能下降，要不要拆成两轮或精简到核心构念？"），让用户自己权衡。

### 模拟规模：主动问，别留白

`simulation_n` 是生成多少条合成记录的计算预算，不是真实样本量，不对应置信区间或总体代表性。这个数字直接决定 WF3 生成多少 persona、WF4 模拟多少份作答——问卷定稿前主动问一句："打算生成多少条合成记录？没概念的话可以先按场景数 × 3 起步，等 WF2 定出原型数后再给你算出具体数字。"不要不问就默默填 `null` 往下走。

用户给出具体数字，记下来交给 WF2 核对是否够覆盖每个场景；用户明确表示没有偏好（不是没问到，是问过之后说"随便"），才填 `null` 并在 `simulation_n_rationale` 写明"用户无偏好，交由 WF2 按场景数 × 每场景变体数计算"。

## construct_measured 词表

受控词表，每题必填，取自下表或自定义补充：

| 构念 | 示例题 | 备注 |
|---|---|---|
| 基础身份 | 年级 / 专业 / 学校类型 / 城市 / 居住状况 | 筛选 + 分层用，非结果变量 |
| 行为 | 使用频率 / 做过没做过 / 当前解决方式 | |
| 情境 | 使用场景 / 触发条件 / 当时在做什么 | 建立行为上下文 |
| 痛点 / 阻力 | 哪个环节最麻烦 / 最不愿意做什么 | WF2 Phase C 任务摩擦的来源题 |
| 功能优先级 | 最想先解决什么 / 哪个更重要 | 排序 / ranking 题常用 |
| 需求 | 缺什么 / 卡在哪 | |
| 满意度 | 对现状多满意 | 结果变量，见下方红线 |
| 使用意愿 | 愿不愿用 | 结果变量，见下方红线 |
| 付费意愿 | 愿不愿付 / 价格感受 / 划不划算 | 结果变量，见下方红线 |
| 信任 | 信不信 / 担不担心 | |
| 体验 | 用起来怎样 / 整体感受 | |
| 空间体验 | 场所感受 / 路径认知 / 拥挤感 / 安全感 | 空间 / 环境类问卷 |
| 审美偏好 | 风格偏好 / 视觉感受 / 品牌形象认知 | 视觉 / 产品 / 包装类问卷 |
| 价格 / 损失感知 | 定价合理性 / 沉没成本 / 换用成本 | 产品 / 服务类问卷 |

满意度 / 使用意愿 / 推荐意愿 / 付费意愿是**结果变量**：这里只是把它们标为要测的构念，WF2 生成人群画像时绝不能把它们塞进 persona 背景——那会让模拟变成自证预言。基础身份类是分层变量，可以进 persona 背景。

## 输出

写 `runs/<时间戳>/survey.json`：

```json
{
  "research_question": "...",
  "target_population": "...",
  "purpose": "pre-research",
  "simulation_n": null,
  "simulation_n_rationale": "WF2 根据最终场景数与每场景变体数确定；本字段不代表真实样本量或抽样精度",
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

`question_id` 全问卷唯一（建议 `Q1..Qn` 按题序）；`scale` 只用于 likert / rating / nps。

## 完成前确认

四组判断关卡，每组都是"为什么这件事重要"而不是走过场：

- **结构完整可追溯**：JSON 合法，每题有唯一 `question_id` 与非空 `construct_measured`。后者是 WF2 反推人群的唯一入口——缺了它 WF2 没法工作，这条不能打折扣。
- **量表可读**：所有 likert 题标出 `low`/`high` 端点。没有端点说明的 1-5 分是无法解释的数字，受访者和分析者都猜不出方向。
- **题序与偏差自检**：筛选→行为→态度→开放；逐题过一遍上面五种偏差。
- **篇幅合理**：≤15 题、预估≤5 分钟；超出时已经跟用户说明代价，不是静默放行。

## 该停下来问的情况

- 没有 `research_question` → "你想量化什么？一句话。"
- 没有 `target_population`，或只有人口统计缺行为/经历描述 → "他们做过什么、遇到过什么？"
- 研究问题实际是探索性的（"发现未知问题"）→ 说明问卷不适用，建议先做访谈。
- 还没问过 `simulation_n` → 主动问一句"打算生成多少条合成记录"，不要静默填 `null`。

## 红线

继承 `SKILL.md` 的跨 workflow 红线（合成样本标注、结果变量不作背景）。本步独有：`purpose` 字段要如实标注，不能因为用户想要发表级结论就默认写 `hypothesis-validation`——合成样本撑不起那个标准。

## 下一步

问卷就绪后进入 `workflows/02-audience-analysis.md`：读 `construct_measured` 反推影响回答的关键变量，划人群原型、匹配行为机制、映射任务摩擦。

## 示例

**例 A：工具接受度（技术接受类）**

```json
{
  "research_question": "做过问卷调研但遭遇过没人填困境的设计学生，是否愿意用 AI 合成样本工具做预调研",
  "target_population": "做过问卷调研、遭遇过没人填困境的设计类本科 / 研究生",
  "purpose": "pre-research",
  "simulation_n": null,
  "simulation_n_rationale": "待 WF2 确定场景数后，按每场景至少 3 个变体计算；仅用于覆盖情景，不代表真实人群",
  "estimated_minutes": 4,
  "questions": [
    {"question_id":"Q1","text":"你目前的学习阶段？","type":"single-choice","options":["大一","大二","大三","大四","研究生"],"scale":null,"construct_measured":"基础身份","required":true},
    {"question_id":"Q2","text":"过去半年你做过几次问卷调研？","type":"rating","options":null,"scale":{"points":10,"low":"0 次","high":"10 次以上"},"construct_measured":"行为","required":true},
    {"question_id":"Q3","text":"发问卷时你通常遇到哪些困难？（多选）","type":"multi-select","options":["找不到足够受访者","回收质量差（随便填）","发出去没人理","互填群质量低","其他"],"scale":null,"construct_measured":"痛点 / 阻力","required":true},
    {"question_id":"Q4","text":"我愿意用 AI 合成样本做预调研","type":"likert","options":null,"scale":{"points":5,"low":"强烈不同意","high":"强烈同意"},"construct_measured":"使用意愿","required":true},
    {"question_id":"Q5","text":"什么情况下你不敢用合成样本？","type":"open","options":null,"scale":null,"construct_measured":"信任","required":false}
  ]
}
```

**例 B：空间 / 产品体验类**

```json
{
  "research_question": "近半年购置过家具的城市租房者，对家具选购过程中哪些环节摩擦最高",
  "target_population": "近半年购置过家具、居住在租赁房的 25-35 岁城市居民",
  "purpose": "pre-research",
  "simulation_n": null,
  "simulation_n_rationale": "待 WF2 确定场景数后计算；仅覆盖情景，不代表真实人群",
  "estimated_minutes": 4,
  "questions": [
    {"question_id":"Q1","text":"你目前的居住类型？","type":"single-choice","options":["租房（合租）","租房（独租）","自购房","其他"],"scale":null,"construct_measured":"基础身份","required":true},
    {"question_id":"Q2","text":"过去半年你购置家具的主要渠道？（多选）","type":"multi-select","options":["线上平台（淘宝/京东等）","品牌官网/旗舰店","二手平台","宜家等大型卖场","本地家居市场","其他"],"scale":null,"construct_measured":"行为","required":true},
    {"question_id":"Q3","text":"选购家具时你通常处于什么情境？","type":"single-choice","options":["搬新家需要一次配齐","租房补充单件","旧家具坏了替换","纯粹想换风格","其他"],"scale":null,"construct_measured":"情境","required":true},
    {"question_id":"Q4","text":"选购过程中哪些环节让你觉得最麻烦？（最多选 3 项）","type":"multi-select","options":["尺寸测量和空间规划","风格搭配判断","质量 / 材质难以判断","配送和安装","退换货麻烦","其他"],"scale":null,"construct_measured":"痛点 / 阻力","required":true},
    {"question_id":"Q5","text":"整体来看，你对上次家具选购体验的满意程度？","type":"likert","options":null,"scale":{"points":5,"low":"非常不满意","high":"非常满意"},"construct_measured":"满意度","required":true},
    {"question_id":"Q6","text":"有什么选购困难是上面没提到的？","type":"open","options":null,"scale":null,"construct_measured":"痛点 / 阻力","required":false}
  ]
}
```
