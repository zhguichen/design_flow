---
description: 跑完整合成样本问卷 pipeline——问卷设计→人群反推→行为机制映射→任务摩擦映射→persona 生成→模拟作答→结果分析。步间暂停确认。
argument-hint: [研究问题，如"设计学生是否愿用 AI 合成样本工具做预调研"]
---

跑完整合成样本问卷 pipeline，串联 1→2→2.5→2.6→3→4→5。**步间暂停确认**：每步产出后展示验收结果，问"继续下一步?"再进；早期错误（烂问卷 / 烂原型）能在当步拦下，不污染下游。

步骤：

1. 用 `workflows/01-survey-design.md` 设计问卷 → `runs/<时间戳>/survey.json`。验收通过后问："继续 WF2 反推人群？"
2. 用 `workflows/02-audience-inference.md` 反推待机制校验的人群 → `runs/<时间戳>/archetypes.json`。验收通过后问："继续 WF2.5 行为机制映射？"
3. 用 `workflows/025-behavior-mechanism-mapping.md` + `references/behavior-mechanism-library.md` 说明原型为什么真实合理存在 → `runs/<时间戳>/behavior_mechanisms.json`。验收通过后问："继续 WF2.6 任务摩擦映射？"
4. 用 `workflows/026-task-friction-mapping.md` + `references/task-friction-framework.md` 说明痛点/麻烦环节/功能优先级如何推导 → `runs/<时间戳>/task_frictions.json`。验收通过后问："继续 WF3 生成 persona？"
5. 用 `workflows/03-persona-generation.md` 生成带 `mechanism_trace` 与 `task_friction_profile` 的 persona → `runs/<时间戳>/respondents.jsonl` + `respondents_meta.json`。验收通过后问："继续 WF4 模拟作答？"
6. 用 `workflows/04-response-simulation.md` 模拟作答 → `runs/<时间戳>/responses.jsonl` + `responses_meta.json`。验收通过后问："继续 WF5 结果分析？"
7. 用 `workflows/05-result-analysis.md` 分析：先 `python3 scripts/analyze.py runs/<时间戳>/` 生成 `stats.json`，再写 `report.md`。

每步满足该 workflow 的验收标准（可机械检查）再进下一步。任一步触发 Stop 条件则停下追问，不臆造。所有产出标注 合成样本 / 仅供预调研。

完成后建议（任选其一）：

- "要不要我基于 `report.md` 的'需真实用户验证的假设'，起草一份真人访谈提纲来验证？"
- "要不要我调整某步参数（如 N、原型比例、题序）重跑某一步？"
