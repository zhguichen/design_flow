# RFC: design-flow Architecture

## Overview

`design-flow` 是 filesystem-native 的 Claude Code Skill：一个根 `SKILL.md` 入口 + 5 个按需加载的 workflow 子文件 + 1 个编排命令 + 1 个确定性统计脚本。无插件运行时、无第三方依赖（仅 python3 标准库）、无 vendor lock-in。

## Design Principles

### 1. 预调研定位优先

skill 全程标注 合成样本 / 仅供预调研 / 反映模拟质量不等于研究效度。这不是 polish 步骤，是入口条件——任何输出缺失标注即未完成。

### 2. 结构化契约驱动

每步产出是 JSON（survey / archetypes / respondents / responses）+ sidecar meta，而非散文。下游步骤机械消费上游字段（WF2 靠 WF1 的 `construct_measured`、WF3 靠 WF2 的 `proportion`）。验收标准全部可机械检查。

### 3. Progressive disclosure

根 `SKILL.md` ~95 行只放 pipeline 全貌 + 路由 + 红线 + Quality Gate + Pitfalls。方法论细节（题序 / 五类变量 / 五层结构 / 作答原则 / 统计方法）下沉到 5 个 workflow 子文件，按触发条件加载。

### 4. 确定性工具出事实，模型出判断

WF5 统计走 `scripts/analyze.py`（count / mean / median / 分布 / 交叉表），LLM 只做主题编码与洞察。LLM 不算算术（60 行易错）。工具测量、模型判断。

### 5. 防自证预言

结果变量（满意度 / 使用意愿 / 推荐意愿 / 付费意愿）不能作 persona 背景设定，只设定影响它们的原因。否则 persona 自带结果，作答变成自证预言、数据失真。

### 6. 防前几个 persona 主导

WF5 强制 Cross-Interview Sampling：每条观察贴 source id、验证每个受访者至少出现一次、单源标记。防 LLM 用前几类人下结论。

## Architecture

### File Layout

```
design-flow/
├── SKILL.md                 ← 根 skill（~95 行，唯一入口，路由到 workflows）
├── workflows/01..05-*.md    ← 5 个按需加载子文件
├── commands/run-pipeline.md ← 编排命令（串联 1→5，步间暂停）
├── scripts/analyze.py       ← WF5 确定性统计（python3 标准库）
├── references/              ← 方法论沉淀（按需引用，待填）
├── docs/{prd,rfc,working,test}.md
└── runs/                    ← 运行时产出（gitignore）
```

### Pipeline

```
1. survey-design       survey.json
2. audience-inference  archetypes.json
3. persona-generation  respondents.jsonl + respondents_meta.json
4. response-simulation responses.jsonl + responses_meta.json
5. result-analysis     stats.json（脚本）+ report.md（LLM）
```

步间暂停确认：每步验收通过后问"继续下一步?"再进。早期错误（烂问卷 / 烂原型）在当步拦下，不污染下游。

### 关键契约

- WF1 `construct_measured`（受控词表）→ WF2 反推变量的入口
- WF2 `proportion` + `变量设定`（五类，不含结果变量）→ WF3 按比例展开
- WF2 `预期影响construct`（整体定性方向）→ WF4 作答参考（非剧本，零变异则降级）
- WF3 `respondent_id` → WF4 作答 → WF5 source id 追溯

## Trade-Offs

### 单 root skill vs 多独立 skill

**选：单 root + 按需 workflow。** 5 个 workflow 是一条 pipeline 的阶段，不是独立可复用能力；多独立 skill 会重复注册、丢失上下游契约。根 skill 路由，workflow 子文件不全局暴露。

### 5 个 workflow vs 更多 / 更少

**选：5 个。** 对应 simulator 的核心流程（问卷→人群→persona→作答→分析）。更少则单文件膨胀、契约混杂；更多则过度拆分（simulator 本就 8 节，已收敛到 5 步）。

### JSON 输出 vs Markdown

**选：JSON（数据）+ report.md（终端报告）。** pipeline 步骤间机器消费需强类型 JSON（WF5 直接统计）；终端交付物给人读用 Markdown。问卷 / 人群 / 受访者 / 作答全 JSON，仅分析报告 Markdown。

### 何时引入 scripts/

**选：WF5 引入 `scripts/analyze.py`，不引入完整 CLI 包。** 遵循"使用 3 次以上才提取"原则的逃生条款——统计是确定性计算，LLM 算术不可靠，故 WF5 触发首次引入。只一个脚本（argparse + 标准库），无 pyproject / tests（待第三个确定性需求出现再升级为完整 CLI 包）。

### 步间暂停 vs 自动串联

**选：步间暂停确认。** 每步贵（生成 60 persona + 60 作答）、早期错误会传播。暂停让用户控节奏、当步拦错。牺牲速度换可靠。

### 受控构念词表 vs 自由文本

**选：受控词表 + 允许补充。** WF1→WF2 契约需清晰；纯自由文本则 WF2 反推一致性弱。词表覆盖态度 / 行为 / 需求 / 满意度 / 使用意愿 / 付费意愿 / 信任 / 体验 + 自定义。

## Future Expansion

### 何时提取新 script / reference

- 某确定性计算出现 3 次以上 → 提取到 `scripts/`
- 某方法论说明被 3 个 workflow 引用 → 提取到 `references/`
- 目前 `references/` 待填，候选：避免偏差检查表、Likert 量表选用指南、persona anti-patterns 速查

### 暂不做

- `.claude-plugin/plugin.json`（先当轻量 skill；要发布成插件再加）
- 完整 Python CLI 包（pyproject / tests，待第三个确定性需求）
- 真实问卷分发 / 收集
