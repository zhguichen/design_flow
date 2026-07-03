# Working — design-flow

变更日志 + 经验教训。每次有意义的改动后追加一条。

## Changelog

### 2026-07-03 — 步间完整展示产出 + 主动问模拟规模

- `commands/run-pipeline.md`：步间暂停确认从"展示验收结果"改为"完整展示该步产出（先全量，再验收结果）"，量大时（persona/作答超 20 条）允许"前几条 + 每 archetype 至少 1 条 + 完整统计表 + 注明其余见文件"的降级展示，但必须显式声明，不能默默略过。
- WF1：`simulation_n` 从"用户没指定就填 null"改为"问卷定稿前主动问打算生成多少条合成记录"，只有用户明确表示无偏好才填 `null`；新增对应 Stop 条件。
- WF2 Phase A：原型数确定后，按"原型数 × variants_per_archetype"算出建议 `simulation_n`，主动报出并确认，不默默定稿；新增对应 Stop 条件。
- 经验教训：默默填默认值（`null` / 建议值）会让用户以为"没得选"，其实这两个数字直接决定下游生成成本和覆盖范围，理应主动确认而不是留白等用户自己发现。

### 2026-07-02 — 将行为机制从“存在证明”改为证据分级的可证伪假设

- WF2.5 将机制 `confidence` 改为 `plausibility`，新增 `evidence_level` / `evidence_detail` / `source_refs`；只有直接相关的用户材料或可核验研究才能标 `supported`。
- 明确机制库卡片只是推理模板。仅依赖机制库、问卷文本和模型推理时必须标 `model-inference`，合理性最高为 `plausible`。
- 将 `latent_motive` 全链改为 `hypothesized_latent_motive`，同步 WF3 persona、WF4 response 与 WF5 报告，禁止把推断写成受访者已承认的内心事实。
- 每个机制新增 `alternative_explanation` 与 `falsification_probe`，替代原先泛化的 `validation_probe`；报告必须展示竞争解释和什么观察会使机制不受支持。
- 根 Skill、README、AGENTS、pipeline、PRD、RFC、测试、参考库和队友说明统一改为“机制提供可检验合理性，不证明人群存在或现实比例”。
- 经验教训：理论名称会制造权威感，但“能套上理论”不等于目标场景有证据。可审计机制必须同时说明证据来自哪里、还可能怎么解释、怎样会被证伪。

### 2026-07-02 — 用场景覆盖取代虚假的样本量与人群比例

- WF1 将 `recommended_n` / `n_rationale` 改为可选的 `simulation_n` / `simulation_n_rationale`；删除“真实样本约 385、合成缩放到 30–60”的类比，明确生成数量只是计算预算。
- WF2 将 `proportion` 改为 `scenario_weight`，每个权重必须记录 `weight_source`；无真实依据时使用 `coverage-default` 等权，不再由模型猜现实分布。
- WF2 新增 `simulation_plan`：默认按“archetype 数 × 每类 3 个差异化变体”确定基础覆盖，额外预算才按权重分配。
- WF3 将“样本量置信度”改为“场景覆盖质量”，不再用 N<10 / 10–30 / 30+ 评价证据强弱；增加合成记录不会增加真实世界证据。
- WF5 将样本量/分群分布措辞改为合成记录数/场景分配，要求列出权重来源，禁止把模拟百分比解释为总体比例、市场规模或发生率。
- 同步更新根 Skill、README、AGENTS、PRD、RFC、测试和队友修改说明。
- 经验教训：合成数据的行数只影响压力测试覆盖，不产生独立受访者证据；没有校准数据时，等权场景比“看起来真实”的模型比例更诚实。

### 2026-07-02 — 隔离预注册假设，切断模拟自证循环

- WF2 删除 `预期回答倾向` / `预期影响construct`，WF2.5 删除 `likely_behavior` / `answer_implications`；archetype 与机制文件只保留经历、情境、资源、能力和因果机制。
- WF2.6 在 `task_frictions.json` 之外新增独立 `hypotheses.json`，要求模拟前写入并标记 `status=sealed`，每条预测包含替代解释和证伪规则。
- WF3 / WF4 明确禁止读取 `hypotheses.json`；respondent 与 response 不得携带预测方向。模拟结果不支持假设时不得重生成或纠偏。
- WF4 优先在隔离 context / subagent 中只接收 allowlist 输入；无法隔离时必须标记 `blinding.level=procedural` 并降级置信度，避免把程序性“不读取文件”误称为真正盲法。
- WF5 才首次加载封存假设，逐条标记 `supported / not_supported / inconclusive` 并附实际统计或 source 证据。
- 同步更新根 `SKILL.md`、pipeline 命令、README、AGENTS、PRD、RFC 与测试契约。
- 经验教训：仅禁止把结果变量放进 persona 不足以防自证；只要“预期方向”仍传入作答模型，统计结果仍会回放上游设定。预测必须与生成输入物理分离，并允许假设失败。

### 2026-07-02 — 增加队友修改说明文档

- 新增 `docs/change-summary.md`：用非工程读者也能理解的方式说明本轮为什么加入 WF2.5 行为机制映射和 WF2.6 任务摩擦映射、改了哪些文件、解决了哪些可信度问题、队友应该按什么顺序 review。
- 更新 `README.md`：在使用说明后加入 `docs/change-summary.md` 入口，避免队友只看到一堆 workflow 文件，不知道先读哪里。

### 2026-07-02 — 新增 WF2.6 任务摩擦映射

- 新增 `references/task-friction-framework.md`：明确痛点/麻烦环节不能从性格直接推导，必须走“任务场景 → 当前行为 → 环境限制 → 资源/能力 → 行为机制 → 摩擦维度 → 可能痛点答案”链路。
- 新增 `workflows/026-task-friction-mapping.md`：在 WF2.5 和 WF3 之间输出 `task_frictions.json`，为痛点题、排序题、功能优先级题、使用边界题、开放题提供摩擦维度、分数、drivers 和作答规则。
- 更新 `SKILL.md` 与 `commands/run-pipeline.md`：全链从 1→2→2.5→3→4→5 改为 1→2→2.5→2.6→3→4→5。
- 更新 WF3：每个 respondent 必须带 `task_friction_profile`，不能只带 persona 五层和 `mechanism_trace`。
- 更新 WF4：痛点/排序/功能优先级/开放题必须追溯到 `task_friction_profile`，不能从“谨慎/开放”等性格标签直接作答。
- 更新 WF5、README、PRD、RFC、test、AGENTS：报告和验收标准加入“机制与任务摩擦解释”。

### 2026-07-02 — 接入 user-research + 新增行为机制映射层

- 安装 Anthropic `user-research` skill 到本机 Codex skills；定位为 WF1 的研究方法顾问，用于检查问卷是否适合该研究目的、目标人群与方法是否匹配，但不替代本 skill 的 `survey.json` 契约。
- 新增 `references/behavior-mechanism-library.md`：按问卷领域路由技术接受、产品购买、空间体验、视觉审美、服务参与、公共设计、生活方式、潜在需求、问卷作答心理等机制；核心链路为“环境/事件 → 处境/限制 → 行为机制 → 表层需求/潜在动机 → 作答影响”。
- 新增 `workflows/025-behavior-mechanism-mapping.md`：WF2 的原型先经过机制校验，输出 `behavior_mechanisms.json`；没有机制支撑、不会影响回答、现实不自洽的类型不能进入 WF3。
- 更新 WF1：可参考 Anthropic `user-research` 做方法适配，但最终仍必须输出带 `construct_measured` 的 `survey.json`。
- 更新 WF2：原型改为“待机制校验”，新增 `候选机制线索`，下一步改为 WF2.5。
- 更新 WF3/WF4/WF5：persona 必须带 `mechanism_trace`；关键作答要能追溯机制；报告新增“机制解释”，显式区分模拟数据模式、机制推导解释与需真人验证的假设。
- 更新 `SKILL.md`、`commands/run-pipeline.md`、README、PRD、RFC、test、AGENTS：全链从 5 步改为 1→2→2.5→3→4→5。

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
