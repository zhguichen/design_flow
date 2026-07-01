---
name: design-flow
description: 面向设计类学生/从业者的问卷预调研 Skill——设计问卷、反推人群、生成 persona、LLM 模拟填写、分析结果，产出合成样本替代低质量互填。
---

# design-flow

> 合成样本问卷模拟器。**预调研工具，不替代真实用户研究。**

它替代的是低质量、随便发、没人认真填的学生式问卷调研，而不是专业研究中的真实样本采集。

## When To Use / Goal

当用户需要：

- 做问卷预调研但找不到足够目标受访者
- 预检问卷题序、量表、避免偏差
- 在真实调研前快速判断方向、估计分群差异

触发。目标：产出可信、足量、结构合理的合成问卷样本（人群画像 + 模拟数据集 + 分析报告），替代低质量互填。

不适用：用户想"发现未知问题"——那是访谈的活；本 skill 量化已知构念，不揭示未知。

## Boundaries

**In scope:** 设计问卷 → 反推人群 → 生成 persona → 模拟作答 → 结果分析 的完整链路。
**Out of scope:** 真实用户研究、正式发表级统计、问卷分发平台、替代真人证据。

## Pipeline 全貌

```
1. survey-design       问卷设计        → runs/<ts>/survey.json
2. audience-inference  人群反推        → runs/<ts>/archetypes.json
3. persona-generation  persona 生成    → runs/<ts>/respondents.jsonl + respondents_meta.json
4. response-simulation 模拟作答        → runs/<ts>/responses.jsonl + responses_meta.json
5. result-analysis     结果分析        → runs/<ts>/stats.json + report.md
```

每步产出物落 `runs/<时间戳>/`。步间默认暂停确认（见 Commands）。

## Related workflows（路由）

5 个子文件按需加载，不全局暴露。按触发条件 load：

| 触发 | 加载 | 产出 |
|---|---|---|
| 用户给研究问题 / 目标人群，需设计问卷；或 `survey.json` 不存在 | `workflows/01-survey-design.md` | `survey.json` |
| `survey.json` 就绪，需反推人群原型 | `workflows/02-audience-inference.md` | `archetypes.json` |
| `archetypes.json` 就绪，需展开成具体受访者 | `workflows/03-persona-generation.md` | `respondents.jsonl` + meta |
| `respondents.jsonl` 就绪，需模拟作答 | `workflows/04-response-simulation.md` | `responses.jsonl` + meta |
| `responses.jsonl` 就绪，需分析 | `workflows/05-result-analysis.md` | `stats.json` + `report.md` |

**单步用法**：用户只要某一步（如只设计问卷），直接 load 对应 workflow，不必跑全链。
**串联用法**：用 `/design-flow:run-pipeline` 串 1→5（步间暂停）。

每步须满足该 workflow 的验收标准（可机械检查）再进下一步；触发 Stop 条件则停下追问，不臆造。

## 跨 workflow 红线

任何输出（人群画像 / 模拟数据集 / 分析报告）都必须标注：**合成样本 / 样本量 / 置信度 / 仅供预调研**。结果变量（满意度 / 使用意愿 / 推荐意愿 / 付费意愿）不能作为 persona 背景设定，只设定影响它们的原因。

## Prerequisites

- 无外部依赖（skill 主体纯 Markdown，LLM 驱动）。
- Workflow 5 的统计需 `python3`（标准库，无第三方包）跑 `scripts/analyze.py`。
- 运行时产出写 `runs/`（gitignore，不入库）。

## Quality Gate

整套 skill 完成一次运行的验收：

- 根 skill 是唯一入口，workflows 按需加载（不全局暴露）。
- 每步产出文件含合成样本标注（meta.note 或报告头部）。
- `respondents.jsonl` / `responses.jsonl` 每行含可追溯 id（`respondent_id` → `archetype_id` → `question_id` 链完整）。
- 分析报告区分"模拟数据显示的模式" vs "需真实用户验证的假设"。
- 统计来自 `scripts/analyze.py`（确定性），非 LLM 自算。

## Commands

- `/design-flow:run-pipeline [研究问题]` — 串联 1→5，步间暂停确认（见 `commands/run-pipeline.md`）。

## Known Pitfalls

- **结果变量硬塞背景**：把满意度 / 使用意愿当 persona 背景设定 → 自证预言、数据失真。只设定影响它们的原因（经验 / 情境 / 心理 / 资源 / 能力）。
- **前几个 persona 主导结论**：LLM 分析时易用前几类人下结论。强制 Cross-Interview Sampling——每条观察贴 source id、验证每人至少出现一次、单源标记。
- **LLM 自算统计**：60 行算术易错。统计必须走 `scripts/analyze.py`，LLM 只做主题编码与判断。
- **照抄预期倾向**：WF2 的 `预期影响construct` 是方向提示非剧本；WF4 若 100% 决定论作答 → 退化为剧本，质量降级。
- **合成样本当真人证据**：合成样本对真实人群代表性固有局限。报告必须声明仅供预调研、不替代真实研究。

## References

方法论沉淀见 `references/`（按需引用，各阶段填充）。维护仓库见 `AGENTS.md`。
