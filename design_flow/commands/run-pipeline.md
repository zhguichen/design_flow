---
description: 跑完整合成样本问卷 pipeline——问卷设计→人群反推→行为机制映射→任务摩擦映射→persona 生成→模拟作答→结果分析。使用三道确认门。
argument-hint: [研究问题，如"设计学生是否愿用 AI 合成样本工具做预调研"]
---

跑完整合成样本问卷 pipeline，串联 1→2A→2B→2C→3→4→5。只设置三道用户确认门：问卷、完整 audience package + 模拟规模、persona 抽查 + 模拟模式。每道门先完整展示自上次确认以来的产出和验收结果，再询问是否继续；内部 Phase 验收通过时自动推进，触发 Stop 条件才停下追问。

受访者数量较大（persona 超过 20 条）时，可展示前几条 + 每个 archetype 至少 1 条完整示例 + 完整 `by_archetype` 统计表，但要明确说明“其余 N 条见 `runs/<时间戳>/xxx.jsonl`”。WF4 作答和 WF5 分析在第三道门确认后连续运行；最终交付完整统计与报告，不在两者之间增加形式化确认。

## 入口判定

开始时先判断用户输入属于哪类，不要默认由 Agent 写问卷：

- **已有问卷**：用户粘贴题目、上传问卷、提供表格/截图/文档，或说“我已有问卷”。走 WF1 的问卷规范化：保留原题意，补 `construct_measured`，修正明显偏差和结构问题，转成 `survey.json`。
- **没有问卷**：用户只有设计题目、研究问题、方案设想或说“帮我生成问卷”。WF1 先追问设计对象、目标人群、使用场景、已有方案和最想验证的不确定点；信息足够后再生成问卷。
- **已有 `survey.json` / run**：用户提供标准文件、run 目录，或要求继续 WF2/WF3/WF4/WF5。先校验已有文件，缺什么补什么，不重新生成问卷。

如果用户没有明确选择，但上下文已经足够判断，直接按对应入口执行；只有缺少研究问题、目标人群或设计目的导致无法生成/规范化问卷时才停下来问。

步骤：

所有 workflow、reference 和 script 都从 `${CLAUDE_PLUGIN_ROOT}` 读取；`runs/` 始终写到用户当前项目目录，不要写进 plugin 目录。

1. 用 `${CLAUDE_PLUGIN_ROOT}/workflows/01-survey-design.md` 生成、规范化或校验问卷 → `runs/<时间戳>/survey.json`。**门 1：问卷确认**。展示入口类型、全部题目、保留/修改说明和验收结果后问：“确认问卷并进入人群分析吗？”
2. 用 `${CLAUDE_PLUGIN_ROOT}/workflows/02-audience-analysis.md` 完成三个 Phase：
   - **Phase A**：反推待机制校验的人群原型 → `runs/<时间戳>/archetypes.json`。验收通过后自动进入 Phase B。
   - **Phase B**：读取 `${CLAUDE_PLUGIN_ROOT}/references/behavior-mechanism-library.md`，把原型整理为证据分级、存在替代解释且可证伪的机制假设 → `runs/<时间戳>/behavior_mechanisms.json`。验收通过后自动进入 Phase C。
   - **Phase C**：读取 `${CLAUDE_PLUGIN_ROOT}/references/task-friction-framework.md`，整理任务情境与 drivers → `runs/<时间戳>/task_frictions.json`。不生成逐题预测方向、答案阈值或排序规则。
   - **门 2：audience package + 模拟规模确认**。完整展示全部原型、机制、任务情境与验收结果；说明基础覆盖量、用户此前预算偏好和最终建议 `simulation_n`，一次确认后更新 `simulation_plan` 并进入 WF3。
3. 用 `${CLAUDE_PLUGIN_ROOT}/workflows/03-persona-generation.md` 生成带 `mechanism_trace` 的 persona，并把任务情境 drivers 转写成五层中的可观察事实 → `runs/<时间戳>/respondents.jsonl` + `respondents_meta.json`。respondent 不含摩擦分数、top friction、预测方向或答案规则。**门 3：persona 抽样与模式确认**。展示前几条、每个 archetype 至少 1 条和完整分配统计，让用户选择 `full`，或只指定 n 运行 `stratified-pilot`。同时显示：“WF4 需要开启隔离 subagent，让每个作答模型只看到单个 persona、问卷与允许的机制信息，避免跨人物答案互相影响；这不会增加新的确认门。”若当前环境不支持 subagent，必须在这里说明将降级为 procedural blinding。用户不得手工挑 persona；运行 `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/select_respondents.py" runs/<时间戳>/ ...` 写出 `selection.json`。
4. 用 `${CLAUDE_PLUGIN_ROOT}/workflows/04-response-simulation.md` 只为 `selection.json` 中的 persona 隔离模拟作答 → `runs/<时间戳>/responses.jsonl` + `responses_meta.json`。环境支持 subagent 时必须开启只接收 allowlist 输入的隔离 context；无法创建时向用户显示原因，标记 `blinding.level=procedural` 并降级置信度。pilot 必须标注有限覆盖；验收通过后自动进入 WF5。
5. 用 `${CLAUDE_PLUGIN_ROOT}/workflows/05-result-analysis.md` 分析：先 `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/analyze.py" runs/<时间戳>/` 生成 `stats.json`，再结合回答原文、机制和任务情境写 `report.md`。

每步满足该 workflow 的验收标准（可机械检查）再进下一步。只有三道确认门或 Stop 条件会中断；其余阶段自动推进。所有产出标注 合成样本 / 仅供预调研。

完成后建议（任选其一）：

- "要不要我基于 `report.md` 的'需真人确认的问题'，起草一份真人访谈提纲？"
- "要不要我调整某步参数（如 N、原型比例、题序）重跑某一步？"
