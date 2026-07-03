---
name: design-flow
description: 面向设计类学生/从业者的问卷预调研 Skill——支持用户自带问卷或由 Agent 追问设计背景后生成问卷，再反推人群、用人文社科/心理学行为机制和任务摩擦模型推导合理场景、生成 persona、LLM 模拟填写、分析结果，产出覆盖充分的合成场景用于替代低质量互填。
---

# design-flow

> 合成样本问卷模拟器。**预调研工具，不替代真实用户研究。**

它替代的是低质量、随便发、没人认真填的学生式问卷调研，而不是专业研究中的真实样本采集。

## When To Use / Goal

当用户需要：

- 做问卷预调研但找不到足够目标受访者
- 预检问卷题序、量表、避免偏差
- 在真实调研前快速判断方向、估计分群差异

触发。目标：产出结构合理、场景覆盖充分、带机制依据和任务摩擦依据的合成问卷记录（人群画像 + 行为机制推导 + 任务摩擦推导 + 模拟数据集 + 分析报告），替代低质量互填。

不适用：用户想"发现未知问题"——那是访谈的活；本 skill 量化已知构念，不揭示未知。

## Boundaries

**In scope:** 设计问卷 → 反推人群 → 行为机制映射 → 任务摩擦映射 → 生成 persona → 模拟作答 → 结果分析 的完整链路。
**Out of scope:** 真实用户研究、正式发表级统计、问卷分发平台、替代真人证据。

## Pipeline 全貌

```
1. survey-design       问卷设计        → runs/<ts>/survey.json
2. audience-analysis   人群分析        → runs/<ts>/archetypes.json
  Phase A 人群反推                       └─ archetypes.json
  Phase B 行为机制映射                   └─ behavior_mechanisms.json
  Phase C 任务摩擦映射                   └─ task_frictions.json
3. persona-generation  persona 生成    → respondents.jsonl + meta + selection.json
4. response-simulation 模拟作答        → runs/<ts>/responses.jsonl + responses_meta.json
5. result-analysis     结果分析        → runs/<ts>/stats.json + report.md
```

每步产出物落 `runs/<时间戳>/`。全链只在问卷、audience package + 模拟规模、persona 抽查 + 模拟模式三处暂停确认（见 Commands）。

## 开始方式

先判断用户从哪里开始，避免默认替用户写问卷：

| 开始方式 | 触发 | 处理 |
|---|---|---|
| A. 用户已有问卷 | 用户粘贴问卷、上传表格/截图/文档、或说“我已有问卷” | 进入 WF1 的“已有问卷规范化”：尽量保留原题意，检查题序、偏差、题型、选项和量表，为每题补 `construct_measured`，转成 `survey.json` 后走门 1 |
| B. 用户没有问卷 | 用户只有设计题目、方案、研究问题或说“帮我生成问卷” | WF1 先追问设计对象、目标人群、使用场景、方案/功能和最想验证的不确定点；信息足够后再生成问卷 |
| C. 已有 `survey.json` 或 run | 用户提供已有 `survey.json`、run 目录，或要求继续 WF2/WF3/WF4/WF5 | 验证现有文件结构，缺什么补什么；不要重新生成问卷 |

Agent 生成问卷时不能直接堆“是否愿意使用/购买/推荐”题。必须先围绕用户的设计目标建立行为、情境、痛点、功能优先级、信任/价格/边界等构念，再把结果变量放到后段测量。

## Related workflows（路由）

5 个 workflow 文件按需加载，不全局暴露；WF2 内含 A/B/C 三个 Phase，因此全链共有 7 个执行阶段。按触发条件 load：

| 触发 | 加载 | 产出 |
|---|---|---|
| 用户给研究问题 / 目标人群，需设计问卷；用户提供草稿问卷需规范化；或 `survey.json` 不存在 | `workflows/01-survey-design.md` | `survey.json` |
| `survey.json` 就绪，需反推人群、匹配机制、映射任务摩擦 | `workflows/02-audience-analysis.md` | `archetypes.json` + `behavior_mechanisms.json` + `task_frictions.json` |
| 以上四文件就绪，需展开并选择具体受访者 | `workflows/03-persona-generation.md` | `respondents.jsonl` + meta + `selection.json` |
| `respondents.jsonl` 就绪，需模拟作答 | `workflows/04-response-simulation.md` | `responses.jsonl` + meta |
| `responses.jsonl` 就绪，需分析 | `workflows/05-result-analysis.md` | `stats.json` + `report.md` |

**单步用法**：用户只要某一步（如只设计问卷），直接 load 对应 workflow，不必跑全链。
**串联用法**：用 `/design-flow:run-pipeline` 串 1→2（A→B→C）→3→4→5（三道确认门）。

每步须满足该 workflow 的验收标准（可机械检查）再进下一步；触发 Stop 条件则停下追问，不臆造。

## 跨 workflow 红线

任何输出（人群画像 / 行为机制 / 任务摩擦 / 模拟数据集 / 分析报告）都必须标注：**合成样本 / 合成记录数 / 场景覆盖质量 / 仅供预调研**。`simulation_n` 是计算预算，`scenario_weight` 是场景分配权重；二者都不代表真实总体、抽样精度或现实比例。结果变量（满意度 / 使用意愿 / 推荐意愿 / 付费意愿）不能作为 persona 背景设定，也不能以预期方向传入模拟阶段；只设定影响它们的原因。人群类型必须能追溯到“环境/事件 → 处境/限制 → 行为机制 → 任务摩擦 → 表层需求/假设性潜在动机”的因果输入链。机制只提供可检验合理性，不证明该类人真实存在；没有连贯、可证伪机制或任务摩擦支撑的场景不进入模拟。

任何阶段都不得生成逐题预测方向、答案阈值或分数查表。WF3 只把可观察经历、资源、能力和限制写进 persona，WF4 再根据人物故事独立作答。

所有 JSON / JSONL 的自然语言字符串如需引用短语，统一使用中文书名号式引号 `「」`，例如 `"描述": "主要考虑「好不好打理」"`。不要在字符串内部直接嵌入未转义的 ASCII 双引号；文件写入后必须先通过 JSON 解析与阶段校验。

## Prerequisites

- 无第三方依赖（skill 主体 Markdown + Python 标准库脚本）。
- 作为 plugin 运行时，所有只读 workflow / reference / script 均以 `${CLAUDE_PLUGIN_ROOT}` 为根解析；运行产出始终写到用户当前项目的 `runs/`，不要写进 plugin 缓存。
- 每阶段用 `scripts/validate_run.py` 做结构校验；门 3 用 `scripts/select_respondents.py` 选择 persona；Workflow 5 用 `scripts/analyze.py` 计算统计。
- 运行时产出写 `runs/`（gitignore，不入库）。

## Quality Gate

整套 skill 完成一次运行的验收：

- 根 skill 是唯一入口，workflows 按需加载（不全局暴露）。
- 每阶段先通过 `scripts/validate_run.py` 的机械校验，再执行 workflow 中保留的方法判断。
- 每步产出文件含合成样本标注（meta.note 或报告头部）。
- `archetypes.json` 使用带来源的 `scenario_weight` 与 `simulation_plan`；无真实依据时等权覆盖，不声称现实比例。
- `behavior_mechanisms.json` 覆盖每个 archetype，并标注证据等级、合理性、表层需求、假设性潜在动机、替代解释和证伪条件；仅模型推断时不得标为 `supported`。
- `task_frictions.json` 覆盖每个 archetype 和所有痛点/排序/开放/使用边界题，并标注可观察 drivers、机制追溯和置信度；不生成分数到答案的查表规则。
- 进入 WF4 前向用户显示 subagent 隔离说明与实际执行模式。环境支持 subagent 时必须为入选 persona 开启隔离 context；无法创建时明确显示降级原因，设置 `responses_meta.blinding.level=procedural` 并降低置信度。
- `selection.json` 记录 `full` 或确定性 `stratified-pilot`；用户只决定 n，不手工挑 persona。pilot 覆盖所有 archetype，并明确不代表完整场景覆盖。
- `respondents.jsonl` / `responses.jsonl` 每行含可追溯 id（`respondent_id` → `archetype_id` → `question_id` 链完整）。
- 分析报告区分“模拟数据显示的模式”“机制推导出的可能解释”和“需真人确认的问题”。
- 统计来自 `scripts/analyze.py`（确定性），非 LLM 自算。

## Commands

- `/design-flow:run-pipeline [研究问题]` — 串联 1→2A→2B→2C→3→4→5，在三道确认门暂停（见 `commands/run-pipeline.md`）。

## Known Pitfalls

- **结果变量硬塞背景**：把满意度 / 使用意愿当 persona 背景设定 → 自证预言、数据失真。只设定影响它们的原因（经验 / 情境 / 心理 / 资源 / 能力）。
- **把机制链当现实证据**：理论卡片只能让场景更明确、可证伪，不能证明某类人真实存在。WF2 Phase B 必须标证据等级、替代解释和证伪条件。
- **痛点题凭性格乱猜**：问“哪个环节更麻烦”时，不能只靠“谨慎型/开放型”作答。WF2 Phase C 先把生活情境、行为经验、环境限制和资源能力整理成可观察 drivers；WF3 将这些事实写进 persona 故事，WF4 再盲作答，不执行分数查表。
- **把所有可能性都塞进样本**：会冲淡结果。只纳入机制链连贯、影响回答、场景自洽的类型；推断薄弱的类型要合并、标 `speculative` 或排除。
- **把场景权重当现实比例**：`scenario_weight` 只分配合成变体。没有真实依据时等权覆盖；模拟百分比不得解释为目标人群发生率。
- **前几个 persona 主导结论**：LLM 分析时易用前几类人下结论。强制 Cross-Interview Sampling——每条观察贴 source id、验证每人至少出现一次、单源标记。
- **看完 persona 后手工挑人**：会把用户预期带入样本选择。用户只能选择 `full` 或指定 pilot n，具体 id 由 `select_respondents.py` 分层选择并记录 seed。
- **LLM 自算统计**：60 行算术易错。统计必须走 `scripts/analyze.py`，LLM 只做主题编码与判断。
- **答案方向泄漏**：把预期高低、排序或逐题答案写进 archetype、persona 或机制文件，会让模拟退化为照表作答。上游只提供原因与可观察事实，不提供结果方向。
- **合成样本当真人证据**：合成样本对真实人群代表性固有局限。报告必须声明仅供预调研、不替代真实研究。

## References

方法论沉淀见 `references/`（尤其 `behavior-mechanism-library.md` 与 `task-friction-framework.md`）。仅在需要格式示例时加载 `references/output-examples.md`。维护仓库见 `AGENTS.md`。
