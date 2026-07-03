---
description: 跑完整合成样本问卷 pipeline——问卷设计→人群反推→行为机制映射→任务摩擦映射→persona 生成→模拟作答→结果分析。使用三道确认门。
argument-hint: [研究问题，如"设计学生是否愿用 AI 合成样本工具做预调研"]
---

跑完整合成样本问卷 pipeline，串联 1→2A→2B→2C→3→4→5。只设置三道用户确认门：问卷、完整 audience package + 模拟规模、persona 抽查 + 模拟模式。每道门先完整展示自上次确认以来的产出和验收结果，再询问是否继续；内部 Phase 验收通过时自动推进，触发 Stop 条件才停下追问。

受访者数量较大（persona 超过 20 条）时，可展示前几条 + 每个 archetype 至少 1 条完整示例 + 完整 `by_archetype` 统计表，但要明确说明“其余 N 条见 `runs/<时间戳>/xxx.jsonl`”。WF4 作答和 WF5 分析在第三道门确认后连续运行；最终交付完整统计与报告，不在两者之间增加形式化确认。

步骤：

所有 workflow、reference 和 script 都从 `${CLAUDE_PLUGIN_ROOT}` 读取；`runs/` 始终写到用户当前项目目录，不要写进 plugin 目录。

1. 用 `${CLAUDE_PLUGIN_ROOT}/workflows/01-survey-design.md` 设计问卷 → `runs/<时间戳>/survey.json`。**门 1：问卷确认**。展示全部题目和验收结果后问：“确认问卷并进入人群分析吗？”
2. 用 `${CLAUDE_PLUGIN_ROOT}/workflows/02-audience-analysis.md` 完成三个 Phase：
   - **Phase A**：反推待机制校验的人群原型 → `runs/<时间戳>/archetypes.json`。验收通过后自动进入 Phase B。
   - **Phase B**：读取 `${CLAUDE_PLUGIN_ROOT}/references/behavior-mechanism-library.md`，把原型整理为证据分级、存在替代解释且可证伪的机制假设 → `runs/<时间戳>/behavior_mechanisms.json`。验收通过后自动进入 Phase C。
   - **Phase C**：读取 `${CLAUDE_PLUGIN_ROOT}/references/task-friction-framework.md`，整理任务情境与 drivers → `runs/<时间戳>/task_frictions.json`；同时预注册并封存 `runs/<时间戳>/hypotheses.json`。
   - **门 2：audience package + 模拟规模确认**。完整展示全部原型、机制、任务情境与验收结果；说明基础覆盖量、用户此前预算偏好和最终建议 `simulation_n`，一次确认后更新 `simulation_plan` 并进入 WF3。
3. 用 `${CLAUDE_PLUGIN_ROOT}/workflows/03-persona-generation.md` 生成带 `mechanism_trace` 的 persona，并把任务情境 drivers 转写成五层中的可观察事实 → `runs/<时间戳>/respondents.jsonl` + `respondents_meta.json`。respondent 不含摩擦分数、top friction 或答案规则；本步不得读取 `hypotheses.json`。**门 3：persona 抽样与模式确认**。展示前几条、每个 archetype 至少 1 条和完整分配统计，让用户选择 `full`，或只指定 n 运行 `stratified-pilot`。用户不得手工挑 persona；运行 `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/select_respondents.py" runs/<时间戳>/ ...` 写出 `selection.json`。
4. 用 `${CLAUDE_PLUGIN_ROOT}/workflows/04-response-simulation.md` 只为 `selection.json` 中的 persona 盲模拟作答 → `runs/<时间戳>/responses.jsonl` + `responses_meta.json`。优先在只接收 allowlist 输入的新隔离 context / subagent 中运行；无法隔离时标记 `blinding.level=procedural` 并降级置信度。本步不得读取 `hypotheses.json`，也不得因结果不符合预期而重生成。pilot 必须标注有限覆盖；验收通过后自动进入 WF5。
5. 用 `${CLAUDE_PLUGIN_ROOT}/workflows/05-result-analysis.md` 分析：先 `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/analyze.py" runs/<时间戳>/` 生成 `stats.json`，再首次读取封存的 `hypotheses.json`，逐条对照后写 `report.md`。

每步满足该 workflow 的验收标准（可机械检查）再进下一步。只有三道确认门或 Stop 条件会中断；其余阶段自动推进。所有产出标注 合成样本 / 仅供预调研。

完成后建议（任选其一）：

- "要不要我基于 `report.md` 的'需真实用户验证的假设'，起草一份真人访谈提纲来验证？"
- "要不要我调整某步参数（如 N、原型比例、题序）重跑某一步？"
