---
description: 跑完整合成样本问卷 pipeline——问卷设计→人群反推→行为机制映射→任务摩擦映射→persona 生成→模拟作答→结果分析。步间暂停确认。
argument-hint: [研究问题，如"设计学生是否愿用 AI 合成样本工具做预调研"]
---

跑完整合成样本问卷 pipeline，串联 1→2→2.5→2.6→3→4→5。**步间暂停确认**：每步产出后**完整展示该步产出**（问卷全部题目 / 全部原型 / 全部机制 / 全部摩擦维度与打分 / 全部 persona 摘要 / 全部作答摘要，不是"举 2-3 个例子"式的摘要），再展示验收结果，问"继续下一步?"再进；早期错误（烂问卷 / 烂原型）能在当步拦下，不污染下游。受访者数量较大（如 persona / 作答超过 20 条）时，全量展示会太长，可展示前几条 + 每个 archetype 至少 1 条完整示例 + 完整 `by_archetype` 统计表，但要明确说明"其余 N 条见 `runs/<时间戳>/xxx.jsonl`"，不能只字不提就默默略过。

步骤：

1. 用 `workflows/01-survey-design.md` 设计问卷 → `runs/<时间戳>/survey.json`。验收通过后问："继续 WF2 人群分析？"
2. 用 `workflows/02-audience-analysis.md` 完成三个 Phase：
   - **Phase A**：反推待机制校验的人群原型 → `runs/<时间戳>/archetypes.json`。Phase A 验收通过后问："继续 Phase B 行为机制映射？"
   - **Phase B**：读取 `references/behavior-mechanism-library.md`，把原型整理为证据分级、存在替代解释且可证伪的机制假设 → `runs/<时间戳>/behavior_mechanisms.json`。Phase B 验收通过后问："继续 Phase C 任务摩擦映射？"
   - **Phase C**：读取 `references/task-friction-framework.md`，说明痛点/麻烦环节/功能优先级如何推导 → `runs/<时间戳>/task_frictions.json`；同时预注册并封存 `runs/<时间戳>/hypotheses.json`。Phase C 验收通过后问："继续 WF3 生成 persona？"
3. 用 `workflows/03-persona-generation.md` 生成带 `mechanism_trace` 与 `task_friction_profile` 的 persona → `runs/<时间戳>/respondents.jsonl` + `respondents_meta.json`。本步不得读取 `hypotheses.json`。验收通过后问："继续 WF4 模拟作答？"
4. 用 `workflows/04-response-simulation.md` 盲模拟作答 → `runs/<时间戳>/responses.jsonl` + `responses_meta.json`。优先在只接收 allowlist 输入的新隔离 context / subagent 中运行；无法隔离时标记 `blinding.level=procedural` 并降级置信度。本步不得读取 `hypotheses.json`，也不得因结果不符合预期而重生成。验收通过后问："继续 WF5 结果分析？"
5. 用 `workflows/05-result-analysis.md` 分析：先 `python3 scripts/analyze.py runs/<时间戳>/` 生成 `stats.json`，再首次读取封存的 `hypotheses.json`，逐条对照后写 `report.md`。

每步满足该 workflow 的验收标准（可机械检查）再进下一步。任一步触发 Stop 条件则停下追问，不臆造。所有产出标注 合成样本 / 仅供预调研。

完成后建议（任选其一）：

- "要不要我基于 `report.md` 的'需真实用户验证的假设'，起草一份真人访谈提纲来验证？"
- "要不要我调整某步参数（如 N、原型比例、题序）重跑某一步？"
