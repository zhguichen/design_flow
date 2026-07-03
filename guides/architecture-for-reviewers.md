# Design Flow 架构设计与 Skill 工程方法

> 面向评审老师：本文档解释 Design Flow 项目的**架构设计思路和 Skill 工程方法**，不涉及具体领域内容（问卷设计方法、行为机制库等）。建议配合 `workflow-design.md`（各步骤设计思想）和 `docs/rfc.md`（架构决策记录）一起阅读。

---

## 目录

1. [项目定位](#项目定位)
2. [整体架构](#整体架构)
3. [核心设计模式](#核心设计模式)
4. [Pipeline 设计](#pipeline-设计)
5. [防自证预言的三层隔离](#防自证预言的三层隔离)
6. [确定性工具与模型判断的分工](#确定性工具与模型判断的分工)
7. [渐进式披露与上下文管理](#渐进式披露与上下文管理)
8. [结构化契约与跨阶段校验](#结构化契约与跨阶段校验)
9. [Subagent 隔离机制](#subagent-隔离机制)
10. [三道确认门的放置逻辑](#三道确认门的放置逻辑)
11. [红线设计](#红线设计)
12. [与 grapeot Skill 工程范式的对齐](#与-grapeot-skill-工程范式的对齐)
13. [设计总结](#设计总结)

---

## 项目定位

Design Flow 是一个 **Claude Code Skill**，以单 Skill plugin 形式分发。它的本质是一个**受控的 AI 合成样本生成系统**——让 AI 产生对设计预调研有用的合成场景，同时通过多层契约、验证和隔离机制控制输出的方向和质量。

**一句话：** 用 AI 生成结构合理、可追溯、可证伪的合成受访者，替代低质量互填问卷。

它不替代真实用户研究，而是在真实调研之前的预检工具——帮你发现问卷设计的问题、判断分群差异的方向、预演不同场景下的作答模式。

---

## 整体架构

### 文件布局

```
design-flow/
├── README.md                         ← 给安装者看：这是什么、怎么装、怎么用
├── AGENTS.md                         ← 给维护 Agent 看：项目规约、目录结构、隐私红线
├── CLAUDE.md                         ← 项目入口指令
├── design_flow/                      ← Skill 包（可独立缓存和安装）
│   ├── SKILL.md                      ← 根 Skill：给使用 Agent 看的操作合同（唯一入口）
│   ├── workflows/                    ← 5 个按需加载文件，共 7 个执行阶段
│   │   ├── 01-survey-design.md
│   │   ├── 02-audience-analysis.md   ← 内含 Phase A/B/C 三个子阶段
│   │   ├── 03-persona-generation.md
│   │   ├── 04-response-simulation.md
│   │   └── 05-result-analysis.md
│   ├── commands/
│   │   └── run-pipeline.md           ← 串联 1→2A→2B→2C→3→4→5 的编排命令
│   ├── references/                   ← 方法论沉淀（行为机制库、任务摩擦框架等）
│   └── scripts/                      ← 确定性工具（纯 Python 标准库）
│       ├── validate_run.py           ← 各阶段统一结构与跨文件契约校验
│       ├── select_respondents.py     ← 分层抽样（full / stratified-pilot）
│       └── analyze.py                ← WF5 统计计算
├── docs/                             ← 四份标准项目文档
│   ├── prd.md                        ← 产品需求文档
│   ├── rfc.md                        ← 架构决策记录
│   ├── working.md                    ← 变更日志 + 经验教训
│   └── test.md                       ← 验收标准清单
├── guides/                           ← 面向不同读者的说明文档
│   ├── getting-started.md            ← 小白使用指南
│   ├── workflow-design.md            ← 各步骤设计思想
│   └── architecture-for-reviewers.md ← 本文档
├── reference-docs/                   ← 外部参考资料（gitignore）
└── runs/                             ← 运行时产出（gitignore）
```

### 三个面向，三个文件

这是从 grapeot 的 Skill 工程实践中学到的核心设计决策——**同一个仓库，给三种读者看，用三个不同的文件：**

| 文件 | 读者 | 内容 |
|------|------|------|
| `README.md` | **安装 Skill 的人** | 这个 Skill 做什么、怎么装、怎么用 |
| `AGENTS.md` | **维护仓库的 Agent** | 项目角色、目录结构、环境规则、隐私红线、维护纪律 |
| `SKILL.md` | **使用 Skill 的 Agent** | 触发条件、Pipeline 路由、红线、验收标准、已知坑位 |

这三个文件的分离不是可有可无的文档工作——它保证了每种读者都能在最短时间内获得自己需要的全部信息，不被其他角色的信息淹没。

### 单根 Skill + 按需 Workflow

项目采用 **"单根 Skill + 按需加载 Workflow"** 模式，而非多个独立注册的 Skill。理由：

- **Harness 只暴露一个入口**，用户不会被"选 WF1 还是 WF2"搞晕
- **自然语言触发**，"我想做问卷预调研"比"先 load 01、再 load 02"的用户体验好得多
- **维护一致**，只需更新 workflow 文件，根 Skill 的触发词和路由表保持一致
- **上下游契约集中管理**，5 个 workflow 形成一条完整链路，独立 Skill 会丢失阶段间的契约关系

5 个 workflow 文件共包含 7 个执行阶段（WF2 内含 A/B/C 三个 Phase），按触发条件按需加载，不全局暴露。

---

## 核心设计模式

### 1. 因果链驱动，不做属性穷举

传统 persona 方法容易退化为"给年龄、职业、收入贴一堆标签，然后凭直觉猜他会在乎什么"。Design Flow 改用一条可验证的因果链：

```
环境 / 事件
  → 社会处境（这个人正面临什么局面）
    → 资源 / 能力限制（他能做什么、不能做什么）
      → 行为机制（他为什么会这样想、这样做）
        → 任务摩擦（他在什么环节遇到什么困难）
          → 表层需求（他说他要什么）
            → 假设性潜在动机（他可能真正需要什么）
```

每个 persona 的每个行为倾向都必须能沿着这条链往回追溯。走不完这条链的"人群类型"不会进入模拟——它只是可能存在的标签组合，但没有推导价值。

### 2. 模拟的质量取决于模拟者的质量

如果只是让 AI 随机生成几个年龄/职业标签然后直接填答案，AI 会退化为靠刻板印象瞎猜——"年轻人就选价格低的""中年人就选品质好的"。这不是模拟，这是概率猜测带点偏见。

因此，Design Flow 把 80% 的工作放在了**"制造一个能认真作答的人"**上（WF1-WF3），只有 20% 在"让他填问卷"上（WF4-WF5）。

### 3. 即兴表演，不是剧本朗读

模拟作答（WF4）的本质是"演员拿到角色档案后即兴表演"——角色档案告诉你这个人是谁、经历过什么、在乎什么，但不会告诉你每句台词应该怎么念。好的 reasoning 能追溯到 persona 的具体处境和经历，而不是引用预先算好的分数。

### 4. 有限理性而非无效作答

模拟的是"认真但有局限的人"——有偏见、会犹豫、有时不了解、有时保守——而不是"瞎填/反填/乱选"。无效作答不提供设计洞察。

---

## Pipeline 设计

### 全貌

```
WF1         WF2-A       WF2-B          WF2-C             WF3          WF4          WF5
问卷设计 → 人群反推 → 行为机制映射 → 任务摩擦映射 → Persona 生成 → 模拟作答 → 结果分析
  |           |           |              |                  |            |            |
survey.    archetypes. behavior_     task_frictions. respondents.  responses.  stats.json
json        json        mechanisms.  json              jsonl         jsonl       report.md
                        json
```

### 阶段间数据流

每个阶段的产出都是结构化 JSON/JSONL，有明确的 schema 契约。下游阶段**按字段名机械消费**上游产出，不靠自然语言"理解"上游写了什么。

关键的数据依赖链：

```
WF1 construct_measured（受控词表）
  → WF2-A 反推人群差异来源

WF2-A simulation_plan + scenario_weight（带来源标注）
  → WF2-B 机制校验 → WF3 场景覆盖分配

WF2-B behavior_mechanisms（证据等级 + 替代解释 + 证伪条件）
  → WF2-C 任务摩擦映射

WF2-C task_frictions 的 drivers（可观察事实，不含分数/排名/规则）
  → WF3 事实化写入 persona 五层结构

WF3 persona 的可观察背景 + mechanism_trace（不含结果变量、预测方向、查表规则）
  → WF4 盲模拟作答

WF4 responses.jsonl
  → WF5 scripts/analyze.py 统计 + LLM 主题编码 → report.md
```

### 为什么上游不生成逐题预测方向

如果 WF2 或 WF3 阶段记录了"这类人应该给 Q3 打 4 分、Q5 选 B"，那 WF4 的模拟就退化为查表——AI 只是把自己的预期绕了一圈打印出来。真正的模拟是：告诉模型"这个人 deadline 很赶、导师催得紧、同学群发问卷没人回"，然后让模型自己判断他会不会在"效率 vs 规范"的排序题里把效率排第一。

---

## 防自证预言的三层隔离

这是整个系统最核心的保障机制。自证预言是合成样本最大的陷阱——如果你在生成虚拟受访者时，已经告诉他"你应该给满意度打 4 分"，那他打出来的 4 分就不能证明任何东西。

### 第一层：结果变量不进 persona 背景

满意度、使用意愿、推荐意愿、付费意愿等**结果变量**永远只作为问卷题目出现，不作为人物设定。WF3 只写入可观察的经历、资源、能力和限制。

### 第二层：上游不生成答案方向

`archetypes.json`、`behavior_mechanisms.json`、`task_frictions.json` 都不记录某类人"应该选什么""应该打几分""应该如何排序"。只记录原因和可观察事实。

### 第三层：不做规则查表

WF4 不接收 `task_frictions.json`，不接收摩擦分数、题目规则或预测方向。只接收 persona 的事实化背景和 behavior_mechanisms 的机制描述。WF4 根据"这个人是谁、经历过什么"独立作答。

三层隔离保证了：**模拟出来的答案差异，只能来自 persona 的处境和经历差异，不能来自上游预设的答案方向。**

---

## 确定性工具与模型判断的分工

AI 模型擅长判断和推理，不擅长算术。Design Flow 把"谁说了算"分成两条线：

| 类型 | 谁做 | 工具 | 举例 |
|------|------|------|------|
| **确定性计算** | Python 脚本 | `analyze.py` / `validate_run.py` / `select_respondents.py` | 均值、中位数、分布、交叉表、JSON schema 校验、分层抽样 |
| **需要判断的** | LLM | Workflow 指令 | 因果链自洽性、开放题主题编码、报告洞察归纳、机制合理性评估 |

混在一起会出现 LLM 算错均值还自信满满地写进报告的灾难场景。

### 脚本化原则

- 只用 Python 标准库，零第三方依赖
- 确定性计算出现 3 次以上才提取为独立脚本
- 脚本之间独立，不互相依赖
- 输入输出均为 JSON/JSONL，方便 LLM 消费

---

## 渐进式披露与上下文管理

### 设计动机

LLM Agent 的上下文窗口是有限资源。如果一次性加载所有信息（5 个 workflow + 参考资料 + 方法论），会导致：
- 关键指令被淹没在大量细节中
- Agent 容易"读到后面忘了前面"
- 每次调用的 token 成本过高

### 实现方式

```
SKILL.md（~113 行）           ← 始终加载：全貌 + 路由 + 红线
  │
  ├── 触发 WF1 → load workflows/01-survey-design.md（~150-200 行）
  ├── 触发 WF2 → load workflows/02-audience-analysis.md（含 A/B/C 三 Phase）
  ├── 触发 WF3 → load workflows/03-persona-generation.md
  ├── 触发 WF4 → load workflows/04-response-simulation.md
  └── 触发 WF5 → load workflows/05-result-analysis.md
```

根 SKILL.md 只写"是什么、什么时候用、红线在哪、Pipeline 全貌、跨 workflow 红线"。具体的执行方法、schema 合约、验收标准下沉到各自的 workflow 文件，按触发条件按需加载。

这样每个 Agent 进来只需读完约 100 行的上下文就能知道自己在干什么、不许干什么。需要执行某一步时，再加载对应的约 150-200 行 workflow 文件。

---

## 结构化契约与跨阶段校验

### 为什么用 JSON 而不是自然语言

上游产出散文，下游读散文找信息 → 信息丢失、格式不一致、字段缺失不可检测。

每步产出结构化 JSON，有明确的 schema。下游按字段名读取。`validate_run.py` 在每个阶段结束后做机械校验——缺字段、类型错误、id 不一致全在进下一步之前抓到。LLM 偶尔会写错格式，机械校验做安全网。

### 校验内容

`scripts/validate_run.py` 统一检查：
- 必填字段是否存在
- 字段类型是否正确
- id 链是否完整（`respondent_id` → `archetype_id` → `question_id`）
- 禁止字段是否出现（如上游产出了逐题预测方向）
- 跨文件引用是否一致

---

## Subagent 隔离机制

这是 WF4（模拟作答）最关键的机制设计。每个 persona 的模拟填答在**独立的 subagent** 中运行。

### 每个 subagent 拿到什么

- 该 persona 的五层背景信息（身份、处境、心理倾向、行为习惯、作答风格）
- `mechanism_trace`（该 persona 对应的行为机制描述）
- 所属 archetype 的 `behavior_mechanisms`（知道背后的因果关系，不只知道标签）
- `survey.json`（问卷本身）

### 每个 subagent 拿不到什么

- 其他 persona 的信息（防止对比影响和相互干扰）
- `task_frictions.json`（防止摩擦分数泄漏答案方向）
- 任何"你应该选哪个"的规则、分值或预测方向

### 降级机制

如果当前环境不支持 subagent（如某些 CLI 配置），降级为 procedural blinding，在 meta 中标记降级原因和置信度影响。不静默降级——必须显式告知用户隔离未生效。

---

## 三道确认门的放置逻辑

不是所有步骤都值得停下来确认。三道门的放置逻辑：

| 门 | 位置 | 为什么放这 |
|---|---|---|
| **门 1：问卷确认** | WF1 完成后 | 问卷是整个 pipeline 的根数据。问卷歪了，六步全废。用户需要确认题目本身合理。 |
| **门 2：人群+规模确认** | WF2 完成后 | 此时 WF2 三个 Phase 全做完，信息最全，适合一次性展示完整 audience package。规模确认也只需一次——不在 WF1 确认是因为那时还不知道有多少 archetype。 |
| **门 3：Persona+模式确认** | WF3 完成后 | 具体的人物形象用户需要抽查。模拟模式（full vs pilot）也要用户决定。这一门之后 WF4+WF5 全自动运行。 |

内部 Phase（WF2 的 A→B→C）自动推进不暂停，因为这是连续的推导链，中途停下来打断推理流意义不大——只要验收通过就往前走。结构错误由 `validate_run.py` 和 Stop 条件拦截。

---

## 红线设计

每条红线背后都保护着一个具体的陷阱。这不是"写得严谨一点"的 polish 要求，而是如果缺失就会导致系统性失效的硬约束：

| 红线 | 防止什么 | 如果不防会怎样 |
|---|---|---|
| **所有输出标注合成样本/仅供预调研** | 合成样本伪装成真人证据 | 用户拿合成数据当真实数据做决策 |
| **结果变量不进 persona 背景** | 自证预言 | 设成"高满意"→填出"高满意"→"看，用户满意"→其实是自己骗自己 |
| **行为机制必须标证据等级+替代解释+证伪条件** | 把推测当实证 | "这类人存在"从一个合理推测悄悄变成既定事实 |
| **上游不生成逐题预测方向** | 自证预言 | persona 或机制文件已经告诉 WF4 应该选什么，模拟只是复述设定 |
| **task_frictions 不生成分数/排名/答案规则** | 查表式模拟 | persona 变成 friction 分数的排序结果，WF4 失去判断的独立性 |
| **用户只能选模式和 n，不能手挑 persona** | 确认偏误代入样本选择 | 用户只挑符合预期的人跑模拟，结果当然更接近预期 |
| **统计走脚本不走 LLM 自算** | 算术错误被流畅文字掩盖 | 报告文笔很好但根本数据是错的 |
| **不得为制造分群差异而重生成** | 数据粉饰 | "再跑一次，这次让 A 类人多打几个高分" |
| **场景权重不能解释为现实比例** | 合成数据冒充市场分布 | 报告中出现"占目标人群的 30%"这种无依据的数字 |
| **不模拟无效作答** | 噪声污染分析 | 瞎填的数据跟认真填的混在一起，分析不出有效信号 |

---

## 与 grapeot Skill 工程范式的对齐

本项目在设计上参考了 grapeot 的独立 Skill 仓库工程范式（见 `reference-docs/how to.md`），并在以下方面做了适配：

### 继承的设计决策

| grapeot 范式 | Design Flow 的对应 |
|---|---|
| 三个面向、三个文件（README / AGENTS / SKILL） | ✅ 完全继承 |
| SKILL.md 是 Agent 的操作合同 | ✅ 根 SKILL.md 是唯一入口，含触发、路由、红线、验收标准 |
| YAML frontmatter（name + description） | ✅ 使用 |
| 验收标准可机械检查 | ✅ 每阶段有明确的文件产出 + `validate_run.py` 自动校验 |
| `docs/` 四件套（prd / rfc / working / test） | ✅ 完全继承 |
| `docs/working.md` 持续追加纪律 | ✅ AGENTS.md 中明确写了这条纪律 |
| 公开仓库只用假值 | ✅ 示例 persona/数据集虚构合成；隐私扫描命令写入 AGENTS.md |
| 确定性计算离线可运行 | ✅ 三个脚本只用 Python 标准库，不需要 API key |
| argparse + 子命令 + JSON 输出 | ⚠️ 适配：当前只有三个脚本，未到需要完整 CLI 包的规模（见 RFC 中的"何时提取新 script"标准） |

### 适配和差异

| 差异点 | grapeot 范式 | Design Flow 的选择 | 原因 |
|---|---|---|---|
| Skill 组织 | 一个仓库 = 一个独立 Skill | 单根 Skill + 5 个按需 workflow | 5 个 workflow 组成一条不可拆分的 pipeline，不是独立可复用能力 |
| CLI 工具 | 完整 Python CLI 包（pyproject + src/） | 三个独立标准库脚本 | 脚本数量少、无第三方依赖，待复杂化再升级 |
| 安装方式 | clone + 符号链接 | Claude Code plugin（`.claude-plugin/plugin.json`） | 目标用户是非技术背景的设计学生，plugin 安装门槛更低 |
| `disable-model-invocation` | 用于"必须调 CLI"的 skill | 未使用 | 本项目大部分逻辑是 LLM 驱动判断，脚本只做确定性计算 |
| dry-run 机制 | 所有写操作支持 --dry-run | 通过 `stratified-pilot` 模式实现类似效果 | 本项目的"写操作"是生成模拟数据，pilot 模式就是小规模预演 |

---

## 设计总结

Design Flow 本质上是一个**受控的幻觉系统**。它让 AI 产生对设计有用的"幻觉"（合成受访者、模拟填答），同时通过多层契约、验证和隔离机制控制幻觉的方向和质量。

它不追求"模拟像真人一样"，而是追求"模拟出来的偏差是可追溯、可检验、可证伪的"——你知道这个人的答案从哪来、为什么来、在什么条件下可能不同。这比"看起来像真人"更有工程价值。

### 核心设计原则速查

1. **因果链驱动**：每个 persona 的行为倾向可沿环境→处境→机制→需求的链路追溯
2. **防自证预言**：三层隔离（结果变量不进背景 / 上游不生成预测 / 不做查表）
3. **确定性事实 + 模型判断**：统计走脚本，推理走 LLM
4. **渐进式披露**：根 Skill 精简，细节按需加载
5. **结构化契约**：JSON 合同 + 自动校验，不靠自然语言传递阶段间信息
6. **Subagent 隔离**：每个 persona 独立盲答，不受其他 persona 或预测方向影响
7. **证据纪律**：机制标注证据等级 + 替代解释 + 证伪条件
8. **显式边界**：合成样本标注、场景权重来源记录、不声称现实比例

---

## 延伸阅读

- [getting-started.md](getting-started.md) — 小白使用指南（面向最终用户）
- [workflow-design.md](workflow-design.md) — 各步骤的设计思想（面向想深入理解每一步为什么这样设计的人）
- `design_flow/SKILL.md` — 根 Skill 操作合同（面向使用 Skill 的 Agent）
- `AGENTS.md` — 维护者入口（仓库规约、提交惯例、隐私扫描）
- `docs/rfc.md` — 架构决策记录（为什么选了这些方案、放弃了哪些替代方案）
- `docs/prd.md` — 产品需求文档（问题定义、目标用户、成功标准）
- `docs/working.md` — 变更日志与经验教训（持续追加）
- `reference-docs/how to.md` — grapeot Skill 工程范式参考
