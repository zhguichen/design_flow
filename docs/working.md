# Working — design-flow

变更日志 + 经验教训。每次有意义的改动后追加一条。

## Changelog

### 2026-07-03 — 明确三种开头入口

- 根 Skill 增加开始方式路由：用户已有问卷、需要 Agent 生成问卷、已有 `survey.json` / run 继续。
- WF1 增加三种输入模式：已有问卷时只做规范化并保留原题意；Agent 生成问卷前先追问设计对象、目标人群、使用场景、已有方案和验证重点；已有标准文件时校验后继续。
- pipeline 命令在开头增加入口判定，门 1 展示入口类型、保留/修改说明和验收结果。
- README 与新手指南同步说明三种开始方式，避免误解为只能让 Agent 直接生成问卷。
- plugin 版本递增为 `0.1.5`。
- 经验教训：问卷生成只是附属能力。入口必须尊重用户已有问卷，并在 Agent 生成问卷时先追问设计目的，否则容易退化成泛泛的“是否愿意 xxx”题库。

### 2026-07-03 — 删除 hypotheses.json 数据流

- WF2 Phase C 不再生成 `hypotheses.json`；只输出任务情境、可观察 drivers 和题目覆盖，不生成逐题预测、结果方向、答案阈值或排序规则。
- WF3/WF4 删除封存文件隔离逻辑；subagent 隔离改为防止跨 persona 相互影响和任务摩擦规则泄漏。
- WF5 删除假设对照章节，报告改为区分模拟模式、可能解释和需真人确认的问题；统计脚本不受影响。
- `validate_run.py` 删除假设文件合同、`hypotheses_loaded` 元数据和报告章节要求，同时继续拒绝 persona / response 中的预测方向字段。
- 根 Skill、pipeline、references、README、AGENTS、PRD、RFC、测试、修改说明和两份指南同步收敛；plugin 版本递增为 `0.1.4`。
- 经验教训：没有参与统计计算、只能由同一模型在报告中手工对照的中间产物，不应成为强制主链合同。预调研应聚焦问卷压力测试与场景诊断。

### 2026-07-03 — WF1 只保留 pre-research

- 删除 `hypothesis-validation` 用途选项，`survey.purpose` 固定为 `pre-research`；合成场景只能做方向判断、问卷预检和预测预演。
- `validate_run.py` 增加强约束，任何其他 `purpose` 值均校验失败；发布 QA 增加对应反例。
- plugin 版本递增为 `0.1.3`。
- 经验教训：没有独立执行分支、又超出产品证据边界的枚举值只会制造虚假的能力暗示，应从合同与校验器中一起删除。

### 2026-07-03 — 显示 WF4 subagent 隔离说明

- 门 3 和 WF4 启动前明确向用户显示为什么需要隔离 subagent、允许传入哪些信息，以及该说明不会新增确认门。
- 环境支持 subagent 时改为必须使用隔离 context；无法创建时必须显示具体原因并降级为 `procedural`，禁止静默降级或误标 `isolated`。
- 根 Skill、pipeline、WF3、WF4、设计指南和发布 QA 同步更新；plugin 版本递增为 `0.1.2`。
- 经验教训：隔离不能只记录在事后 meta 中。用户需要在执行前知道模型是否真正与预测方向隔离，才能正确解释模拟质量。

### 2026-07-03 — 统一 JSON 内部引用符号

- JSON / JSONL 的自然语言字符串如需引用短语，统一使用 `「」`，避免模型生成未转义的 ASCII 双引号导致解析失败。
- 根 Skill 增加全流程规则，格式示例和发布 QA 增加对应正例；plugin 版本递增为 `0.1.1`。
- 经验教训：即使下游校验器能发现无效 JSON，也应在生成约定上消除高频转义风险；自然语言引用不需要占用 JSON 的结构引号。

### 2026-07-03 — 包装 Claude Code plugin 与 marketplace

- 新增仓库级 `.claude-plugin/marketplace.json`、plugin 级 `design_flow/.claude-plugin/plugin.json` 和 MIT `LICENSE`，首个发布版本定为 `0.1.0`。
- README 改为官方 marketplace 安装方式，并区分 plugin 源码目录与用户项目工作目录：安装后无需每次指定 plugin 路径，`runs/` 写到启动 Claude 的当前项目。
- plugin 内所有确定性脚本改用 `${CLAUDE_PLUGIN_ROOT}` 解析，避免安装到版本化缓存后误从用户项目查找 `scripts/`。
- 发布前检查加入 marketplace/plugin 严格校验、版本同步、Git tag 和本地 `--plugin-dir` 冒烟测试；隐私扫描增加 `--hidden` 以覆盖新建的 `.claude-plugin/`。
- 经验教训：filesystem skill 在源码仓库里能运行，不代表缓存安装后仍能运行。发布前必须显式区分只读 plugin 根与可写项目工作目录。

### 2026-07-03 — 门 3 支持确定性分层预演

- 新增 `scripts/select_respondents.py`：支持 `full` 和 `stratified-pilot`；pilot 由用户指定 n，脚本按 archetype 分层选择具体 respondent id 并记录 seed。
- 新增 `selection.json` 契约；WF4 只为入选 persona 作答，`responses_meta.selection` 记录 pool/selected/excluded、seed 与分层计数。
- `analyze.py` 改为按实际 responses 计算 archetype 数，并把 selection 元数据写入 `stats.json`；validator 检查 selection、responses、stats 三者一致。
- pilot 必须覆盖所有 archetype，n 不得小于 archetype 数；用户不得手工挑 id。pilot 报告标注“分层预演 / 不代表完整场景覆盖”，需要正式结果时对同一 persona pool 重跑 `full`。
- 同步更新根 Skill、pipeline、WF3–WF5、README、PRD、RFC、测试和两份指南。
- 经验教训：让用户决定计算预算是合理的，让用户在看到 persona 后挑具体对象会引入选择偏差。数量决策与个体选择必须分开，后者交给可复现的分层算法。

### 2026-07-03 — 新增新手指南与 workflow 设计理念

- 新增 `guides/getting-started.md`：用非技术语言说明适用边界、使用前准备、启动方式、三道确认门、产出文件、报告阅读方式和常见问题。
- 新增 `guides/workflow-design.md`：解释 5 个文件 / 7 个阶段的职责、阶段拆分原因、假设隔离、任务情境事实化、故事驱动模拟、确定性统计和单一校验来源。
- README 增加“新手入口”，AGENTS 目录树同步登记 `guides/`。
- 经验教训：安装说明、维护文档和 workflow 合同都默认读者已经理解用户研究术语。面向新手的文档应先回答“我需要准备什么、什么时候要做决定、最后该看哪个文件”，再解释机制和字段。

### 2026-07-03 — 下沉长示例并精简 WF2

- 将 482 行的 `02-audience-analysis.md` 重写为约 200 行的三阶段操作合同，保留方法、输入输出职责、机械校验、Stop 条件和红线，删除三个重复展开的完整 JSON 样例。
- WF1 删除两个完整领域案例；新增按需加载的 `references/output-examples.md`，集中提供 survey、audience package、respondent 和 response 的虚构合成片段。
- 根 Skill 明确只有在需要格式澄清时才加载示例 reference，正常执行不预加载。
- 经验教训：workflow 应说明如何决策，完整样例应按需加载。把字段合同、验收清单和同一案例同时放在主流程里，会让真正的操作规则被样例淹没。

### 2026-07-03 — 规范化 persona 与 response 的机制字段

- `behavior_mechanisms.json` 成为表层需求、假设性潜在动机、需求标签和证据等级的唯一来源。
- respondent 的 `mechanism_trace` 只保留 `mechanism_ids` 与个体化的 `individual_expression`；WF4 运行时联结完整机制。
- answer 只保留 `reasoning`、可选 `mechanism_id` 和 `uncertain`，不再逐题复制表层需求与潜在动机；WF5 按 id 联结解释。
- 经验教训：为隔离 context 方便而把上游定义复制到每一行，会放大 token 成本并制造版本漂移。应存引用和个体差异，在执行边界动态物化所需上下文。

### 2026-07-03 — 统一机械验收来源

- 新增 `scripts/validate_run.py`，用 `--stage wf1|wf2a|wf2b|wf2c|wf3|wf4|wf5|all` 检查 JSON/JSONL、id、强类型、禁止字段和跨文件引用。
- 各 workflow 的“完成前确认”改为先调用校验器，再保留题序、机制合理性、persona 自然度等无法可靠自动判断的质量判断。
- `docs/test.md` 删除逐字段复述，改为阶段命令与人工判断表；根 Skill 只保留跨阶段 Quality Gate。
- 经验教训：同一字段契约同时写在根 Skill、workflow 和测试文档里会必然漂移。机械规则应由脚本执行，说明文档只描述职责和不可机械化的判断。

### 2026-07-03 — 合并模拟规模询问并收敛为三道确认门

- WF1 不再因缺少 `simulation_n` 单独追问；只记录用户已主动提供的预算偏好，否则填 `null` 交给 WF2。
- WF2 Phase A 计算 proposed plan 但不打断；Phase C 完成后结合 archetype 数、基础覆盖量和预算偏好，只确认一次最终 `simulation_n`。
- run-pipeline 从每个阶段暂停改为三道确认门：问卷、完整 audience package + 模拟规模、persona 抽样。Phase A/B/C 内部自动推进，WF4 验收后自动进入 WF5。
- 经验教训：确认应该对应真正需要用户判断的决策，而不是对应文件数量。过密确认会把内部实现结构暴露给用户，也会重复询问在早期阶段尚无依据的问题。

### 2026-07-03 — 统一为 5 个 workflow 文件、7 个执行阶段

- 全仓统一使用 `1→2A→2B→2C→3→4→5`：WF2 Phase A 人群反推、Phase B 行为机制映射、Phase C 任务情境映射。
- `AGENTS.md` 目录树改为实际存在的 5 个 workflow 文件，删除已不存在的 `02-audience-inference.md`、`025-*`、`026-*` 路径。
- 根 Skill、README、pipeline、PRD、RFC、references、测试契约和队友说明统一使用“5 个文件、7 个执行阶段”，不再把执行阶段误写成 7 个文件。
- 经验教训：文件拓扑和执行阶段是两件事。把二者都叫 workflow 会让路由、文件路径和验收编号逐渐漂移；维护文档应同时明确物理文件数与逻辑阶段数。

### 2026-07-03 — 统一方案 A：任务情境事实化后盲作答

- WF2 Phase C 不再生成 1-5 摩擦分数、top friction 或分数到答案的 `question_friction_rules`；改为 `question_context_coverage`，只记录相关维度、可观察 drivers、机制追溯和 persona 所需情境输入。
- WF3 不再把 `task_friction_profile` 复制进 respondent；改为将 drivers 转写进五层人物故事中的具体经历、资源、能力和环境限制，同时禁止同义改写封存预测。
- WF4 保持方案 A，只接收五层 persona、`mechanism_trace`、所属机制和问卷，不读取 `task_frictions.json` 或 `hypotheses.json`，不执行查表。
- 同步更新根 Skill、pipeline、任务摩擦 reference、PRD、RFC、验收清单和队友说明。
- 经验教训：只在 WF4 里声明“不读摩擦分数”不够；如果 WF2/WF3 仍生产并复制分数、top friction 和答案规则，数据流仍然含有死字段和预测泄漏。盲模拟需要从产出契约上切断方向性字段，而不是只靠最后一步自律。

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
- `AGENTS.md` 补隐私扫描命令与自匹配说明。
- 跑隐私扫描：full scan 仅 4 处自匹配（`docs/test.md` + `AGENTS.md` 的命令行与描述），filtered（排除这两文件）为空 → 无真实红线。`.gitignore` 确认覆盖 `reference-docs/`、`构建路线图.md`、`runs/`、`.env`。
- 清理：untrack `.DS_Store`（macOS 垃圾）与 `commands/.gitkeep`（`run-pipeline.md` 已取代）；`references/.gitkeep` 保留（references/ 待填）。
- 无 env 变量，故无 `.env.example`。
- **8 个 TODO 全部完成。** skill 可用：`/design-flow:run-pipeline <研究问题>` 跑全链，步间暂停，产出落 `runs/<时间戳>/`。
