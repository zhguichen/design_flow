---
name: design-flow
description: 面向设计类学生/从业者的问卷预调研 Skill——设计问卷、反推人群、生成 persona、LLM 模拟填写、分析结果，产出合成样本替代低质量互填。
---

# design-flow

> 合成样本问卷模拟器。**预调研工具，不替代真实用户研究。**

## When To Use / Goal

当用户需要：做问卷预调研但找不到足够目标受访者 / 预检问卷题序与量表 / 在真实调研前快速判断方向时触发。

目标：产出可信、足量、结构合理的合成问卷样本，替代低质量学生式互填。

## Boundaries

**In scope:** 设计问卷 → 反推人群 → 生成 persona → 模拟作答 → 结果分析 的完整链路。
**Out of scope:** 真实用户研究、正式发表级统计、问卷分发平台、替代真人证据。

## Pipeline 全貌

```
1. survey-design       问卷设计        → runs/<ts>/survey.json
2. audience-inference  人群反推        → runs/<ts>/archetypes.json
3. persona-generation  persona 生成    → runs/<ts>/respondents.jsonl
4. response-simulation 模拟作答        → runs/<ts>/responses.jsonl
5. result-analysis     结果分析        → runs/<ts>/report.md
```

## 路由（TODO-6 填充）

5 个 workflow 就位后回填：何时触发哪个 workflow、单步 vs 串联。

- `workflows/01-survey-design.md` —
- `workflows/02-audience-inference.md` —
- `workflows/03-persona-generation.md` —
- `workflows/04-response-simulation.md` —
- `workflows/05-result-analysis.md` —

## 跨 workflow 红线

任何输出（人群画像 / 模拟数据集 / 分析报告）都必须标注：**合成样本 / 样本量 / 置信度 / 仅供预调研**。

## Prerequisites

无外部依赖。纯 Markdown skill，LLM 驱动。

## Acceptance Criteria（Quality Gate）

- 根 skill 是唯一入口，workflows 按需加载（不全局暴露）。
- 每个输出文件含合成样本标注。
- respondents / responses 每行含可追溯 id。
- 分析报告区分"模拟数据显示的模式" vs "需真实用户验证的假设"。

## Commands

- `/design-flow:run-pipeline` — 串联 1→5（见 `commands/run-pipeline.md`，TODO-6）。

## Known Pitfalls

（TODO-6 后随使用补全）

## References

方法论沉淀见 `references/`（按需引用，各阶段填充）。
