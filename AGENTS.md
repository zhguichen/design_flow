# AGENTS.md — design-flow

维护仓库的 Agent 首读文件。任何 Agent 进入此仓库先读这里。

## 项目定位

`design-flow` 是面向设计类学生 / 从业者的 Claude Code Skill，解决"找不到可信、足量、结构合理的目标受访者样本"这个痛点。它覆盖完整链路：设计问卷 → 反推人群 → 生成 persona → LLM 模拟填写 → 收集结果 → 分析。

**边界：预调研工具，不替代真实用户研究。** 它替代的是低质量、随便发、没人认真填的学生式问卷调研，而不是专业研究中的真实样本采集。

形态：单一根 Skill（`SKILL.md`，harness 只发现这一个入口）+ 按需加载的 5 个 workflow 子文件 + 编排命令 + 参考资料夹。这是"root + sub-skills"模式，不是多个独立注册 skill。

## 目录结构

```
design-flow/
├── README.md              ← 给安装者看
├── AGENTS.md              ← 本文件：给维护 Agent 看
├── SKILL.md               ← 根 skill：给使用 Agent 看的操作合同（主产出）
├── workflows/             ← 按需加载的 5 个子文件
│   ├── 01-survey-design.md
│   ├── 02-audience-inference.md
│   ├── 03-persona-generation.md
│   ├── 04-response-simulation.md
│   └── 05-result-analysis.md
├── commands/
│   └── run-pipeline.md    ← 串联 1→5 的编排命令
├── references/            ← 方法论沉淀，按需引用
├── scripts/               ← 仅放必须确定性执行的部分（机会性，按需创建）
├── docs/
│   ├── prd.md             ← 产品需求
│   ├── rfc.md             ← 架构决策与权衡
│   ├── working.md         ← 变更日志 + 经验教训（持续追加）
│   └── test.md            ← 验收标准清单
└── runs/                  ← 运行时产出（问卷/persona/答案/报告），gitignore
```

## 关键约束（红线）

1. **公开仓库只用假值。** 不含真实邮箱、API key、内部路径、1Password 引用、真实联系人。示例 persona / 数据集必须是虚构合成样本。
2. **根 skill 是主产出。** 其余文件都为解释、论证、维护 skill 而存在。`SKILL.md` 保持精简（~200 行），专项内容下沉到 workflows / references。
3. **`docs/working.md` 追加纪律。** 每次有意义的改动后，在 `# Changelog` 下追加一条带日期的记录 + 经验教训。这是为了让未来的自己 / Agent 能回溯决策上下文。

## 跨阶段红线（所有 workflow 继承）

任何输出（人群画像 / 模拟数据集 / 分析报告）都必须标注：**合成样本 / 样本量 / 置信度 / 仅供预调研**。

## 语言

- 内容中文优先（目标用户是中文设计学生）。
- 文件名、字段名、代码标识符用英文。

## 环境

- Skill 主体是纯 Markdown，LLM 驱动。`scripts/analyze.py` 为 Workflow 5 提供确定性统计（python3 标准库，无外部依赖），是路线图"workflow 真需要确定性计算时引入 scripts"逃生条款的首次落地。
- 确定性计算（如统计）若需引入，遵循"使用 3 次以上才提取为 `scripts/`"原则。

## Git 协作流程

### 分支策略

- **`main`** — 主分支，始终保持可发布状态。禁止直接向 `main` 推送，所有改动通过 PR 合入。
- **功能分支** — `feat/<简短描述>`，例：`feat/add-export-csv`。从 `main` 拉出，合回 `main`。
- **修复分支** — `fix/<简短描述>`，例：`fix/survey-routing`。从 `main` 拉出，合回 `main`。
- **文档分支** — `docs/<简短描述>`，例：`docs/update-readme`。纯文档改动，从 `main` 拉出，合回 `main`。

### 开发流程

```bash
# 1. 从最新的 main 开始
git checkout main
git pull origin main

# 2. 创建功能分支
git checkout -b feat/my-feature

# 3. 开发 + 频繁提交（小步提交，便于回退）
git add <files>
git commit -m "<verb>: <description>"

# 4. 推送分支到远端
git push -u origin feat/my-feature

# 5. 在 GitHub 发起 PR，描述做了什么、为什么、怎么测

# 6. 合并后清理本地分支
git checkout main
git pull origin main
git branch -d feat/my-feature
```

### 提交信息规范

格式：`<verb>: <description>`

| 动词 | 用途 |
|------|------|
| `add` | 新增文件或功能 |
| `fix` | 修复 bug |
| `docs` | 纯文档改动 |
| `refine` | 改进现有实现（非 bug 修复） |
| `chore` | 维护性杂务（依赖更新、格式调整等） |
| `remove` | 删除文件或功能 |

例：`add: 仓库骨架`、`fix: survey workflow 路由`、`docs: prd 和 rfc`、`refine: 优化 audience inference prompt`

### PR 规范

- **标题**：使用与提交信息相同的 verb 格式
- **描述**：包含三要素——做了什么 / 为什么 / 怎么测
- **至少一个 Review**：合并前需另一人（或 Agent）过目
- **CI 通过后合并**：若项目配置了 lint / test，须全部通过

### 禁止提交

- `.env`、`runs/`、`reference-docs/`、`构建路线图.md` 或任何含真实凭据的文件
- `node_modules/`、`__pycache__/`、`.DS_Store`（后两者已在 `.gitignore`）

## 发布前隐私扫描

```bash
rg -n "op://|sk-[a-zA-Z0-9]{10,}|/Users/" .
```

扫描 1Password 引用（`op://`）、API key 风格串（`sk-` + 10+ 字符）、绝对用户路径（`/Users/`）。任何匹配都是红线。本命令会在 `AGENTS.md` 与 `docs/test.md` 自匹配（命令本身含 `op://` 与 `/Users/`），忽略这两处。`rg` 默认跳过 gitignore 文件，故 `reference-docs/`、`构建路线图.md`、`runs/` 不扫。本 skill 无 env 变量，故无 `.env.example`；示例 persona / 数据集必须虚构合成。
