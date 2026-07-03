# RFC: design-flow Architecture

## Overview

`design-flow` 是 filesystem-native 的 Claude Code Skill：一个根 `SKILL.md` 入口 + 5 个按需加载的 workflow 文件（WF2 内含 A/B/C 三个 Phase，共 7 个执行阶段）+ 1 个编排命令 + 3 个确定性脚本。无插件运行时、无第三方依赖（仅 python3 标准库）、无 vendor lock-in。

## Design Principles

### 1. 预调研定位优先

skill 全程标注 合成样本 / 仅供预调研 / 反映模拟质量不等于研究效度。这不是 polish 步骤，是入口条件——任何输出缺失标注即未完成。

### 2. 结构化契约驱动

每步产出是 JSON（survey / archetypes / behavior_mechanisms / task_frictions / hypotheses / respondents / responses）+ sidecar meta，而非散文。下游步骤机械消费上游字段（WF2 Phase A 靠 WF1 的 `construct_measured`，Phase C 靠 Phase B 的机制链，WF3 靠 Phase A 的 `simulation_plan` / `scenario_weight`，并把 Phase C 的可观察 drivers 事实化进 persona）。预测与模拟输入分离：`hypotheses.json` 在模拟前封存，WF3 / WF4 不消费；任务摩擦的分数、排序和答案规则也不进入 persona 或 WF4，WF5 才读取封存预测。结构、id、禁止字段和跨文件引用由 `scripts/validate_run.py` 统一检查；方法合理性留在各 workflow 判断。

### 3. Progressive disclosure

根 `SKILL.md` 保持精简，只放 pipeline 全貌 + 路由 + 红线 + Quality Gate + Pitfalls。方法论细节（题序 / 五类变量 / 行为机制 / 任务摩擦 / 五层结构 / 作答原则 / 统计方法）下沉到 5 个 workflow 文件，按触发条件加载。

### 4. 确定性工具出事实，模型出判断

WF5 统计走 `scripts/analyze.py`（count / mean / median / 分布 / 交叉表），LLM 只做主题编码与洞察。LLM 不算算术（60 行易错）。工具测量、模型判断。

### 5. 防自证预言

结果变量（满意度 / 使用意愿 / 推荐意愿 / 付费意愿）不能作 persona 背景设定，也不能作为 `预期影响construct`、`answer_implications` 等预测方向传入模拟阶段。只把经历、情境、资源、能力、机制与任务摩擦交给 WF3 / WF4。预测另存为封存的 `hypotheses.json`，WF5 才能对照；不支持假设时不得重生成。

### 6. 防前几个 persona 主导

WF5 强制 Cross-Interview Sampling：每条观察贴 source id、验证每个受访者至少出现一次、单源标记。防 LLM 用前几类人下结论。

### 7. 机制推导优先，不做属性穷举

WF2 Phase A 只生成待校验原型；Phase B 用人文社科 / 心理学机制把“环境/事件 → 处境/限制 → 行为机制 → 表层需求/假设性潜在动机”链路写清楚，并记录证据等级、合理性、替代解释和证伪条件。理论卡片只提供推理模板，不证明人群存在；没有连贯机制、不会影响回答、场景不自洽的可能性不进入模拟。

### 8. 任务摩擦优先，不从性格猜痛点

问卷里“哪个环节更麻烦 / 哪个功能更优先 / 最不愿意什么”这类题，需要任务场景、行为经验、环境限制、资源能力和机制链作为背景。WF2 Phase C 输出 `task_frictions.json` 的情境覆盖和可观察 drivers，WF3 把这些事实写进 persona；WF4 只根据人物故事独立作答，不从“谨慎型/开放型”等性格标签直接生成，也不执行分数查表。

## Architecture

### File Layout

```
design-flow/
├── SKILL.md                 ← 根 skill（精简入口，路由到 workflows）
├── workflows/*.md           ← 5 个按需加载文件；WF2 内含 A/B/C 三个 Phase
├── commands/run-pipeline.md ← 编排命令（串联 1→2A→2B→2C→3→4→5，三道确认门）
├── scripts/analyze.py       ← WF5 确定性统计（python3 标准库）
├── scripts/select_respondents.py ← full / stratified-pilot 分层选择
├── scripts/validate_run.py  ← 各阶段统一结构与跨文件契约校验
├── references/              ← 方法论沉淀（含行为机制库）
├── docs/{prd,rfc,working,test}.md
└── runs/                    ← 运行时产出（gitignore）
```

### Pipeline

```
1. survey-design       survey.json
2A. audience-analysis / archetype inference  archetypes.json
2B. audience-analysis / behavior mechanism behavior_mechanisms.json
2C. audience-analysis / task context task_frictions.json + hypotheses.json（封存）
3. persona-generation  respondents.jsonl + respondents_meta.json
4. response-simulation responses.jsonl + responses_meta.json
5. result-analysis     stats.json（脚本）+ report.md（LLM）
```

三道确认门：问卷确认；完整 audience package 与最终 `simulation_n` 确认；persona 抽查与 `full` / `stratified-pilot` 模式确认。内部 Phase 验收通过时自动推进，Stop 条件仍在当步拦截。WF4 与 WF5 在第三道门后连续运行。

### 关键契约

- WF1 `construct_measured`（受控词表）→ WF2 反推变量的入口
- WF2 Phase A `simulation_plan` + 带来源的 `scenario_weight` + `变量设定`（五类，不含结果变量）→ Phase B 机制校验与 WF3 场景覆盖
- WF2 Phase B `behavior_mechanisms.json` + `archetype_mechanism_map` → Phase C 做任务摩擦映射
- WF2 Phase C `task_frictions.json` 的 `question_context_coverage` + drivers → WF3 将具体经历、资源、能力和环境限制写入五层 persona
- WF2 Phase C 另写 `hypotheses.json` 并封存 → WF3 / WF4 禁止读取 → WF5 首次加载并逐条标记支持状态
- WF3 的可观察背景 + `mechanism_trace` → WF4 盲模拟作答，不接收任务摩擦文件或预期结果方向
- WF3 persona pool → `selection.json`：`full` 全选，或用户指定 n 后由脚本分层选择；不允许手工挑 id
- WF3 `respondent_id` + `mechanism_trace` → WF4 作答；WF5 再用 source id、机制与模拟前任务情境解释实际模式

## Trade-Offs

### 单 root skill vs 多独立 skill

**选：单 root + 按需 workflow。** 5 个 workflow 文件组成一条含 7 个执行阶段的 pipeline，不是独立可复用能力；多独立 skill 会重复注册、丢失上下游契约。根 skill 路由，workflow 文件不全局暴露。

### 5 个文件 / 7 个阶段 vs 更多 / 更少

**选：5 个文件、7 个阶段。** 原来的核心流程是问卷→人群→persona→作答→分析；人群分析内部增加 Phase B，是因为“像人的 persona”仍不足以回答用户最关心的问题：为什么这些模拟人可信；增加 Phase C，是因为“痛点/麻烦环节”不能从性格直接生成，必须由任务情境推导。三者共享输入并连续执行，所以合并在一个 `02-audience-analysis.md` 中。

### 为什么引入 WF2 Phase B

用户痛点不是问卷生成，而是“找不到可信样本”。如果直接从 WF2 Phase A 进入 WF3，persona 可能只是人口统计 + 情绪标签。Phase B 的取舍是：不证明人群存在或真实比例，只把环境触发、表层需求和假设性潜在动机整理成证据分级、可证伪的解释。牺牲一点流程长度，换来可审计性，但不把理论合理性冒充经验事实。

### 为什么引入 WF2 Phase C

用户指出“哪个环节更麻烦”高度个性化。直接让空洞 persona 回答会退化成性格猜测，但把摩擦分数和题目规则传给 WF4 又会退化成查表。WF2 Phase C 因此只整理任务维度、可观察 drivers 和情境覆盖；WF3 将其事实化进人物故事，具体预测单独封存在 `hypotheses.json`。WF4 在不读取任务摩擦文件的情况下独立作答，WF5 再检查模拟前推导是否得到支持。

### JSON 输出 vs Markdown

**选：JSON（数据）+ report.md（终端报告）。** pipeline 步骤间机器消费需强类型 JSON（WF5 直接统计）；终端交付物给人读用 Markdown。问卷 / 人群 / 受访者 / 作答全 JSON，仅分析报告 Markdown。

### 何时引入 scripts/

**选：保留三个标准库脚本，不引入完整 CLI 包。** `select_respondents.py` 负责可复现的分层选择，`analyze.py` 负责统计事实，`validate_run.py` 统一检查结构、id、禁止字段和跨文件引用。方法合理性仍由 LLM 判断。无 pyproject / 第三方依赖，待脚本继续复杂化再升级为完整包。

### 三道确认门 vs 每步暂停

**选：三道确认门。** 问卷、audience package 和 persona 分别对应研究结构、生成预算、模拟输入三个真正需要用户判断的决策点。Phase A/B/C 内部与 WF4→WF5 之间不再设置形式化暂停；结构错误由验收和 Stop 条件拦截，避免六次重复确认。

### 合成规模与场景权重

**选：覆盖计划，不做抽样精度映射。** `simulation_n` 只表示计算预算，默认由“archetype 数 × 每类 3 个变体”得出；`scenario_weight` 只分配额外合成变体。每个权重必须记录来源，无真实依据时采用 `coverage-default` 等权覆盖。生成更多记录不会增加真实世界证据，报告不得把模拟分布解释为总体比例。

### 受控构念词表 vs 自由文本

**选：受控词表 + 允许补充。** WF1→WF2 契约需清晰；纯自由文本则 WF2 反推一致性弱。词表覆盖态度 / 行为 / 需求 / 满意度 / 使用意愿 / 付费意愿 / 信任 / 体验 + 自定义。

## Future Expansion

### 何时提取新 script / reference

- 某确定性计算出现 3 次以上 → 提取到 `scripts/`
- 某方法论说明被 3 个 workflow 引用 → 提取到 `references/`
- 目前 `references/` 已含行为机制库与任务摩擦框架；候选：避免偏差检查表、Likert 量表选用指南、persona anti-patterns 速查

### 暂不做

- `.claude-plugin/plugin.json`（先当轻量 skill；要发布成插件再加）
- 完整 Python CLI 包（pyproject / tests，待第三个确定性需求）
- 真实问卷分发 / 收集
