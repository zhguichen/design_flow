# Working — design-flow

变更日志 + 经验教训。每次有意义的改动后追加一条。

## Changelog

### 2026-07-01 — 初始化仓库骨架（TODO-0）

- 落地目录结构：README / AGENTS / SKILL 根 + 5 个 workflow 占位 + commands / references（.gitkeep）+ docs 四件套。
- `AGENTS.md` 写项目定位 + 目录结构 + 3 红线（公开仓库只用假值 / 根 skill 是主产出 / working.md 追加纪律）。
- `SKILL.md` 写 YAML frontmatter（`name: design-flow`，不设 `disable-model-invocation`——本 skill 是 LLM 驱动非 CLI 驱动）+ 章节骨架，路由逻辑留 TODO-6。
- 决策：构建期素材（`reference-docs/`、`构建路线图.md`）gitignore + `git rm --cached` 取消追踪，仓库只交付 skill 本身。
- 决策：运行时产出（问卷 / persona / 答案 / 报告）统一写 `runs/<时间戳>/`，gitignore。
- 待办：workflows 1-5 内容（TODO-1~5）、SKILL 路由 + 编排命令（TODO-6）、docs 填充 + 隐私检查（TODO-7）。

### 2026-07-01 — Workflow 1 问卷设计（TODO-1）

- 写 `workflows/01-survey-design.md`：输入（研究问题 / 目标人群 / 用途）→ 输出 `survey.json`（文件级 `research_question` / `purpose` / `recommended_n` + 每题 `question_id` / `text` / `type` / `options` / `scale` / `construct_measured`）。
- 方法搬 survey-design ref：题序（筛选→行为→态度→开放）/ 题型表 / 量表（Likert 5 点标端点、NPS、SUS 逐字）/ 避免偏差 / 样本量（±5%@95%≈385，合成场景缩放 30-60）。
- 决策：输出格式用 **JSON**（用户拍板，pipeline 契约最干净）；`construct_measured` 用受控词表 + 补充；`recommended_n` 写进文件、实际 N 在 WF3 可覆盖；文件内附精简示例。
- 验收标准全部可机械检查；Stop 条件（无研究问题 / 人群 → 追问）；红线（`purpose` 标预调研）。
- 待办：workflows 2-5（TODO-2~5）。

### 2026-07-01 — Workflow 2 人群反推（TODO-2）

- 写 `workflows/02-audience-inference.md`：读 `survey.json` 的 `construct_measured` → 反推关键影响变量（五类：经验/情境/心理/资源/能力）→ 5-8 类原型 + 比例（合计 1.0）。
- 输出 `archetypes.json`：`archetype_id` / `name` / `核心特征` / `proportion` / `变量设定`（类型+变量+取值+来源 question_id）/ `预期回答倾向` / `预期影响construct`。
- 决策：`预期回答倾向` 用**整体定性 + construct 方向**（用户拍板），不逐题给答案——保留 WF4 有限理性空间，避免剧本式作答。
- 红线落地：结果变量（满意度/使用意愿/推荐意愿/付费意愿）不作 persona 背景设定，只设定影响它们的原因；`预期影响construct` 是预测后果方向、非背景设定。
- 验收可机械检查（含 proportion 合计=1.0、来源 question_id 可追溯、变量类型不含结果构念）；Stop 条件（无 construct_measured → 回 WF1）。
- 待办：workflows 3-5（TODO-3~5）。

### 2026-07-01 — Workflow 3 Persona 生成（TODO-3）

- 写 `workflows/03-persona-generation.md`：按 `proportion × N` 把原型展开成具体受访者，每个五层结构（基础身份/社会处境/心理倾向/行为习惯/作答风格）。
- 输出 `respondents.jsonl`（每行 respondent_id/archetype_id/五层）+ sidecar `respondents_meta.json`（count/by_archetype/confidence/anti_pattern_checks/note）。
- 决策：置信度/meta 用 **sidecar meta 文件**（用户拍板）——数据与元数据分离，WF5 直接取用。
- 借 persona-methodology 的 5 anti-patterns（弹性/纯人口统计/理想用户/委员会/过期）做自检；借 persona_generator.py 的 3-part 置信度结构（样本量+数据质量+一致性），**显式不照搬**其 usage_frequency→archetype 固定规则分类。
- 置信度显式标注"反映模拟质量不等于研究效度"；数据质量分因单源 LLM 封顶 medium。
- 同类下个体强制差异（≥3 维不同）；红线：结果变量不作背景设定。
- 验收可机械检查（含同类不复制、五层不含结果构念、note 含合成样本字样）；Stop 条件（无 archetypes → 回 WF2）。
- 待办：workflows 4-5（TODO-4~5）。

### 2026-07-01 — Workflow 4 模拟作答（TODO-4）

- 写 `workflows/04-response-simulation.md`：LLM 以每个 persona 身份独立逐题作答，产出 `responses.jsonl`（每行 respondent_id + answers[]）+ sidecar `responses_meta.json`（模拟质量自评）。
- 作答原则搬 simulator §7：认真目标用户模式 / 有限理性 / 人格差异 / 不确定性 / 社会赞许偏差降低 / 没经历→"不确定"；**不**模拟无效作答/随机/恶意反填。
- 决策：answer 用**强类型**（用户拍板）——Likert/rating/nps 给 int、single-choice 给选项文本、open 给文本，WF5 可直接统计。
- 模拟质量三维度自评：内部一致性 / persona-答案匹配度 / 拒绝乱填；**不照抄** WF2 的 `预期影响construct`（方向提示非剧本，零变异→剧本化降级）。
- reasoning 关键题必给、其余可选；答案带可选 `uncertain` 标记；输出标注合成样本。
- 验收可机械检查（含 answer 在 options/量程内、无直线作答、 respondent_id 一一对应）；Stop 条件（无 respondents→回 WF3）。
- 待办：workflow 5（TODO-5）。

### 2026-07-01 — Workflow 5 结果分析（TODO-5）

- 写 `workflows/05-result-analysis.md` + `scripts/analyze.py`（首个确定性脚本）。
- 两阶段：phase1 `python3 scripts/analyze.py runs/<ts>/` → `stats.json`（每题 count/mean/median/分布 + 按 archetype 交叉表，标准库无依赖）；phase2 LLM 读 stats.json + responses.jsonl 做主题编码 + 洞察 + 写 `report.md`。
- 决策：统计用 **scripts/analyze.py**（用户拍板）——触发路线图"workflow 真需要确定性计算时引入 scripts"逃生条款；不引入完整 CLI 包（无 pyproject/tests），只一个脚本。统计由确定性代码算，避免 LLM 算术错误（确定性工具出事实、模型出判断）。
- 强制搬入 affinity-diagram 的 Cross-Interview Sampling Principle：每条观察贴 source respondent_id、聚类后验证每人至少出现一次、单源模式标记（防 LLM 用前几个 persona 下结论）。
- 描述统计搬 survey-design Analyzing Results（Likert 看全分布不只均值、每结论附样本量）；报告显式区分"模拟数据显示的模式" vs "需真实用户验证的假设"。
- 验收可机械检查（含 stats.json 字段、source id 覆盖、单源标记、假设段）。
- 5 个 workflow 全部就位。待办：根 SKILL 路由 + 编排命令（TODO-6）、docs 填充 + 隐私检查（TODO-7）。

### 2026-07-01 — 根 SKILL 路由 + 编排命令（TODO-6）

- 回填 `SKILL.md`：Related workflows 路由表（按触发条件 load 各 workflow + 单步/串联用法）、Prerequisites（WF5 需 python3）、Quality Gate、Known Pitfalls（结果变量硬塞背景/前几个 persona 主导/LLM 自算统计/照抄预期倾向/合成样本当真人证据）。控制在 ~95 行。
- 写 `commands/run-pipeline.md`：frontmatter(description + argument-hint[研究问题]) + 编号 1→5 步 + 结尾下一步提示。
- 决策：run-pipeline 节奏用**步间暂停确认**（用户拍板）——每步验收通过后问"继续下一步?"再进，早期错误可拦、用户控节奏。移除冗余的 `commands/.gitkeep`。
- 待办：docs 四件套填充 + README/AGENTS 完善 + 隐私检查（TODO-7）。

### 2026-07-01 — docs 四件套 + README/AGENTS + 隐私检查（TODO-7）

- 填 `docs/prd.md`（Summary / Problem / Target Users / Success Criteria / Non-Goals / Boundary）、`docs/rfc.md`（6 设计原则 + 架构 + 6 Trade-Offs + Future）、`docs/test.md`（analyze.py 验证 + 每步验收清单 + 6 QA 场景 + 回归 + 隐私扫描命令）。
- 重写 `README.md`（安装 / 使用 / 结构 / 隐私，人读）。
- `AGENTS.md` 补隐私扫描命令 `rg -n "op://|sk-[a-zA-Z0-9]{10,}|/Users/" .` + 自匹配说明。
- 跑隐私扫描：full scan 仅 4 处自匹配（`docs/test.md` + `AGENTS.md` 的命令行与描述），filtered（排除这两文件）为空 → 无真实红线。`.gitignore` 确认覆盖 `reference-docs/`、`构建路线图.md`、`runs/`、`.env`。
- 清理：untrack `.DS_Store`（macOS 垃圾）与 `commands/.gitkeep`（`run-pipeline.md` 已取代）；`references/.gitkeep` 保留（references/ 待填）。
- 无 env 变量，故无 `.env.example`。
- **8 个 TODO 全部完成。** skill 可用：`/design-flow:run-pipeline <研究问题>` 跑全链，步间暂停，产出落 `runs/<时间戳>/`。
