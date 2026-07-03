# AGENTS.md — design-flow

维护仓库的 Agent 首读文件。任何 Agent 进入此仓库先读这里。

## 项目定位

`design-flow` 是面向设计类学生 / 从业者的 Claude Code Skill，解决"找不到结构合理、场景覆盖充分的目标受访者样本用于预检"这个痛点。它覆盖完整链路：设计问卷 → 反推人群 → 行为机制映射 → 任务摩擦映射 → 生成 persona → LLM 模拟填写 → 收集结果 → 分析。

**边界：预调研工具，不替代真实用户研究。** 它替代的是低质量、随便发、没人认真填的学生式问卷调研，而不是专业研究中的真实样本采集。

形态：单一根 Skill（`SKILL.md`，harness 只发现这一个入口）+ 5 个按需加载的 workflow 文件（其中 WF2 含 A/B/C 三个 Phase，共 7 个执行阶段）+ 编排命令 + 参考资料夹。这是"root + sub-skills"模式，不是多个独立注册 skill。

## 目录结构

```
design-flow/                        ← Git 仓库根目录
├── .claude-plugin/
│   └── marketplace.json            ← Claude Code marketplace 目录
├── README.md                       ← 给安装者看
├── AGENTS.md                       ← 本文件：给维护 Agent 看
├── CLAUDE.md                       ← 项目指令：Agent 入口
├── LICENSE                         ← MIT 许可证正文
├── design_flow/                    ← 可独立缓存和安装的 plugin / Skill 包
│   ├── .claude-plugin/
│   │   └── plugin.json             ← plugin 元数据与版本
│   ├── SKILL.md                    ← 根 skill：给使用 Agent 看的操作合同（主产出）
│   ├── workflows/                  ← 5 个文件，共 7 个执行阶段
│   │   ├── 01-survey-design.md
│   │   ├── 02-audience-analysis.md ← Phase A 人群反推 / B 行为机制 / C 任务情境
│   │   ├── 03-persona-generation.md
│   │   ├── 04-response-simulation.md
│   │   └── 05-result-analysis.md
│   ├── commands/
│   │   └── run-pipeline.md         ← 串联 1→2A→2B→2C→3→4→5 的编排命令
│   ├── references/                 ← 方法论沉淀，按需引用
│   └── scripts/                    ← 仅放必须确定性执行的部分（机会性，按需创建）
├── docs/                           ← 项目文档
│   ├── prd.md                      ← 产品需求
│   ├── rfc.md                      ← 架构决策与权衡
│   ├── working.md                  ← 变更日志 + 经验教训（持续追加）
│   ├── test.md                     ← 验收标准清单
│   └── change-summary.md           ← 变更摘要
├── guides/                         ← 面向新手的使用与设计理念说明
│   ├── getting-started.md
│   └── workflow-design.md
├── reference-docs/                 ← 外部参考资料（gitignore）
└── runs/                           ← 运行时产出（问卷/机制/任务摩擦/persona/答案/报告），gitignore
```

## 关键约束（红线）

1. **公开仓库只用假值。** 不含真实邮箱、API key、内部路径、1Password 引用、真实联系人。示例 persona / 数据集必须是虚构合成样本。
2. **根 skill 是主产出。** 其余文件都为解释、论证、维护 skill 而存在。`SKILL.md` 保持精简（~200 行），专项内容下沉到 workflows / references。
3. **`docs/working.md` 追加纪律。** 每次有意义的改动后，在 `# Changelog` 下追加一条带日期的记录 + 经验教训。这是为了让未来的自己 / Agent 能回溯决策上下文。

## 跨阶段红线（所有 workflow 继承）

任何输出（人群画像 / 行为机制 / 任务摩擦 / 模拟数据集 / 分析报告）都必须标注：**合成样本 / 合成记录数 / 场景覆盖质量 / 仅供预调研**。`simulation_n` 与 `scenario_weight` 不得解释为真实样本量、抽样精度或现实比例。行为机制只提供可检验合理性，不证明人群存在；必须标证据等级、替代解释和证伪条件，模型推断不得标为 `supported`。没有连贯机制或任务摩擦支撑的人群原型不能进入 persona 生成；痛点题不能从性格直接作答。任何上游文件都不得携带逐题预测方向、答案阈值或查表规则，WF4 只根据事实化 persona 独立作答。

## 语言

- 内容中文优先（目标用户是中文设计学生）。
- 文件名、字段名、代码标识符用英文。

## 环境

- Skill 主体是 Markdown，LLM 驱动。`scripts/select_respondents.py` 负责确定性 persona 分层选择，`scripts/validate_run.py` 统一契约校验，`scripts/analyze.py` 提供 Workflow 5 统计；均只用 python3 标准库。
- 确定性计算（如统计）若需引入，遵循"使用 3 次以上才提取为 `scripts/`"原则。

## Git 约定

- 分支：`main`，直接推，两个人不需要 PR 流程
- 提交信息：`<verb>: <description>`。动词用 `add` / `fix` / `docs` / `refine` / `chore` / `remove`
- 推送前 `git pull --rebase` 避免冲突
- 永不提交 `.env`、`runs/`、`reference-docs/`、`构建路线图.md` 或任何含真实凭据的文件

## 发布前隐私扫描

```bash
rg --hidden -g '!.git/**' -n "op://|sk-[a-zA-Z0-9]{10,}|/Users/" .
```

扫描 1Password 引用（`op://`）、API key 风格串（`sk-` + 10+ 字符）、绝对用户路径（`/Users/`），并用 `--hidden` 覆盖 `.claude-plugin/`。任何匹配都是红线。本命令会在 `AGENTS.md` 与 `docs/test.md` 自匹配（命令本身含 `op://` 与 `/Users/`），忽略这两处。`rg` 仍跳过 gitignore 文件，故 `reference-docs/`、`构建路线图.md`、`runs/` 不扫。本 skill 无 env 变量，故无 `.env.example`；示例 persona / 数据集必须虚构合成。
