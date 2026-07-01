# grapeot 独立 Skill 仓库 — 构建经验

> 来源：分析了 grapeot 的 semantic-search-skill、presentation_skill、outlook_skill、chinese-visa-photo-skill、playwright-test-skill 等独立 skill 仓库
> 学习日期：2026-07-01

---

## 一、仓库标准结构

grapeot 的每个独立 skill 仓库严格遵循同一套布局：

```
<skill-repo>/
├── README.md              # 给人看的：安装和使用指南
├── AGENTS.md              # 给维护者/Agent 看的：项目角色、结构、规则
├── pyproject.toml         # Python 打包配置
├── .env.example           # 密钥模板（全是假值）
├── .gitignore             # 屏蔽 .env, __pycache__, .venv, data/
│
├── skills/                # ★ 核心：Agent 面向的 skill 文件
│   └── skill_<name>.md    # 唯一的根 skill（Agent 读这个）
│
├── src/<package_name>/    # Python 库 + CLI 实现
│   └── cli.py             # argparse CLI 入口
│
├── docs/                  # 四份标准文档
│   ├── prd.md             # 产品需求文档
│   ├── rfc.md             # 架构设计文档
│   ├── working.md         # 变更日志 + 经验教训
│   └── test.md            # 测试策略
│
├── tests/                 # pytest（默认离线）
└── scripts/               # CLI 的 shell 包装脚本
```

### 三个面向，三个文件

这是最核心的设计决策——**同一个仓库，给三种读者看，用三个不同的文件：**

| 文件 | 读者 | 内容 |
|------|------|------|
| `README.md` | **安装 skill 的人** | 这个 skill 做什么、怎么装、怎么用 |
| `AGENTS.md` | **维护仓库的 Agent** | 项目角色、目录结构、环境规则、隐私红线、维护纪律 |
| `skills/skill_<name>.md` | **使用 skill 的 Agent** | 触发条件、操作步骤、CLI 命令、验收标准、已知坑位 |

**AGENTS.md 的典型内容：**
- 项目角色（一句话说清这个仓库是什么、不是什么）
- 目录结构（每个文件/文件夹的用途）
- 环境规则（用 uv 不用 pip、.venv 路径、不提交真实密钥）
- 隐私红线（运行什么正则扫描、示例数据必须是假的）
- 维护纪律（改了代码就更新 docs/working.md）

**关键：** 这不是可有可无的文档。grapeot 的每个仓库都有这三份文件，缺一不可。

---

## 二、SKILL.md —— 整个仓库的产品

SKILL.md 不是给人读的散文，是给 Agent 读的**操作合同**。Python CLI 只是支撑。

### 完整模板

```markdown
---
name: skill-name
description: 一句话描述这个 skill 做什么
disable-model-invocation: true  # 可选：true = 强制 Agent 用 CLI，别自己推理
---

# Skill 名称

## When To Use / Goal
什么场景触发、目标是什么。写清楚"当用户说 X 时，用这个 skill"。

## Boundaries
**In scope:** 这个 skill 负责什么
**Out of scope:** 明确不做什么，交给谁做

## Prerequisites
需要安装什么、配置什么环境变量

## Acceptance Criteria
列出可逐条检查的完成条件。**不满足 = 任务未完成。**
不是"做得好"，而是：
- `deck_plan.md` 存在且包含 mode/audience/thesis
- 每个 slide 的 `data-background` 路径都能解析到 `generated_slides/` 下的文件
- speaker_notes.md 存在，内容不重复 slide 正文

## Commands
具体的 CLI 命令，Agent 可以直接复制粘贴执行：
```bash
semantic-search rebuild --file-list tmp/files.txt --cache-dir .knowledge_cache
semantic-search query --file-list tmp/files.txt --cache-dir .knowledge_cache --query "问题" --top-k 10
```

## Known Caveats / Pitfalls
已知的坑和边界情况。比如：
- 图片模式是默认，HTML 模式只在用户明确要求时使用
- 不要在渲染失败时悄悄从 image 降级到 html

## Workspace Overlays
哪些配置应该留在用户的本地覆盖层，不写进公共仓库：
- 源文件目录路径
- API endpoint URL
- 联系人别名
```

### 写法要点

1. **YAML frontmatter 必填**：`name`、`description`。`disable-model-invocation: true` 用于那些"Agent 自己干不了，必须调 CLI"的 skill（如 semantic-search 的 embedding 计算）。

2. **验收标准必须可机械检查**。不是"界面好看"，而是"`index.html` 中每个 `data-background` 路径对应一个实际存在的文件"。不是"回答合理"，而是"每条记录都有 respondent_id，且能追溯到 respondents.jsonl"。

3. **命令是可复制执行的**。Agent 读完 SKILL.md 后，应该能直接复制代码块里的命令跑起来。不要写"运行搜索命令"这种描述性语言。

4. **边界写得越清楚，Agent 越不会越权**。明确说"out of scope: PPTX 编辑"比期待 Agent 自己判断可靠得多。

5. **已知坑位要诚实**。presentation_skill 的 SKILL.md 里有 13 条 known traps 表格，每一条都是在真实使用中踩过的坑。

---

## 三、docs/ 四件套

每个仓库的 `docs/` 下都有四份文件，格式一致：

| 文件 | 回答的问题 | 典型长度 |
|------|-----------|---------|
| `prd.md` | 为什么要做？给谁用？成功标准是什么？不做什么？ | 1-2 页 |
| `rfc.md` | 架构怎么设计？关键权衡是什么？数据怎么存？ | 1-2 页 |
| `working.md` | 改了什么？学到了什么？ | 持续追加 |
| `test.md` | 测什么？怎么测？手动验证清单？ | 1 页 |

**关键纪律：** `working.md` 不是可选的。grapeot 的 AGENTS.md 里明确写了：每次有意义的改动后，必须在 `docs/working.md` 的 `# Changelog` 下追加一条。这不是为了别人看——是为了未来的自己（或 Agent）能理解当初为什么这么做。

---

## 四、Python CLI 实现规范

所有 skill 仓库的 CLI 遵循统一模式，Agent 可以跨 skill 无缝使用：

### 入口模式

```python
# src/<package>/cli.py

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="skill description")
    subparsers = parser.add_subparsers(dest="command")
    # ... 子命令
    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    # 分发到库函数
    ...

if __name__ == "__main__":
    main()
```

### 统一约定

- **argparse** + `build_parser()` 返回 `ArgumentParser`——不是 Click、不是 Typer
- **子命令** 用 `subparsers`，每个子命令一个功能
- **JSON 输出**：`json.dumps(..., ensure_ascii=False, indent=2)`
- **自定义异常**：如 `CacheError`、`OutlookSkillError`，不用裸 `Exception`
- **`--dry-run`**：所有写操作（发邮件、删记录）必须先支持 dry-run
- **`uv` 管理依赖**：`uv venv .venv && uv pip install -e '.[dev]'`
- **入口注册**：在 `pyproject.toml` 的 `[project.scripts]` 定义 CLI 命令名

### 敏感操作保护

```python
# outlook_skill 的发信命令
parser.add_argument("--dry-run", action="store_true",
    help="Preview the email without sending")
```

这是一个硬约定——任何有副作用的操作（发送、删除、发布）都必须先支持 dry-run。

---

## 五、测试策略

### 三层测试

| 层级 | 默认运行？ | 需要什么？ | 标记 |
|------|----------|-----------|------|
| **单元测试** | ✅ 是 | 无 | 普通 pytest |
| **离线集成** | ✅ 是 | 测试 fixture | 普通 pytest |
| **在线集成** | ❌ 否 | API key + 网络 | `@pytest.mark.live_integration` |

### 测试重点

grapeot 的测试**不追求覆盖率数字**，而是保护公共契约：

1. **CLI 参数解析**——改了参数名测试会挂
2. **核心算法逻辑**——排序、验证、概率采样
3. **文件 I/O 正确性**——缓存原子写入、schema 版本检查
4. **公共契约不变性**——"有且仅有一个根 skill"、"四份 docs 都存在"

### 不测什么

- 不测实时 API 调用（除非显式 `--run-live` 标记）
- 不 mock 外部服务（直接跳过）
- 不追求高覆盖率

---

## 六、公共安全——从第一天就设计

grapeot 的仓库从创建的第一分钟就是按"随时可以公开"来设置的：

### .gitignore

```gitignore
.env
.env.*
!.env.example
__pycache__/
.venv/
data/
*.pyc
dist/
```

### .env.example

```bash
# 全是假值，从不包含真实密钥
OPENAI_API_KEY=replace-with-your-real-key
SEMANTIC_SEARCH_CACHE_DIR=/path/to/your/cache
# 如果用到 1Password：
# OP_SERVICE_ACCOUNT_TOKEN=op://your-vault/your-item/your-field
```

### 隐私扫描命令

AGENTS.md 中记录的发布前检查命令：
```bash
rg -n "op://|sk-[a-zA-Z0-9]{10,}|/Users/" .
```
任何匹配都是红线。

### 示例数据

- 用假名：`alice@example.com`
- 合成图片标注"此图为虚构"
- 不包含任何真实联系人、路径、token、客户名

---

## 七、安装协议——公共仓库 + 本地覆盖

grapeot 的 skill 仓库不分发配置，只分发**技术契约**。安装时：

```
公共仓库（GitHub）              私有工作区（用户本地）
─────────────────────────────────────────────────
SKILL.md 操作指南               实际使用的源文件目录
CLI 接口和参数                  联系人 alias
离线测试用例                    API 密钥
.env.example（假值）            端点 URL
                                业务上下文
                                .env（真值）
```

用户安装时把仓库 clone 到工作区，在 `rules/skills/` 创建符号链接暴露唯一的根 skill，私有配置留在本地 `.env` 或 overlay 文件里——**绝不进公共仓库**。

---

## 八、创建新 Skill 仓库的步骤

按 grapeot 的模式，建一个独立 skill 仓库的标准流程：

### 1. 写 SKILL.md（先写这个）

在写任何代码之前，先把 Agent 的操作合同写清楚：
- 什么场景触发？（When to use）
- 边界在哪？（In scope / Out of scope）
- 验收标准是什么？（可逐条检查）
- 需要什么命令？（可复制执行）

### 2. 搭骨架

```bash
mkdir -p skills src/<pkg> docs tests scripts
touch README.md AGENTS.md .env.example .gitignore pyproject.toml
```

### 3. 写 AGENTS.md

给维护仓库的 Agent 看：项目角色、目录结构、环境规则、隐私红线、维护纪律。

### 4. 写 README.md

给人看：这个 skill 是什么、怎么装、依赖什么、快速开始。

### 5. 写 docs/ 四件套

`prd.md` → `rfc.md` → `test.md` → `working.md`（先建空文件，边做边填）

### 6. 实现 CLI

`src/<pkg>/cli.py`，argparse + 子命令，JSON 输出，`--dry-run`。

### 7. 写测试

离线优先。保护 CLI 契约和核心逻辑。集成测试加 `live_integration` 标记。

### 8. 隐私检查

```bash
rg -n "op://|sk-[a-zA-Z0-9]{10,}|/Users/" .
```
确认 `.env.example` 全是假值，`.gitignore` 屏蔽了敏感文件。

---

## 九、关键设计决策速查

| 决策 | 为什么 |
|------|--------|
| 一个仓库 = 一个根 skill | 独立版本、独立测试、独立安装 |
| SKILL.md 用 YAML frontmatter | Agent 能解析 name/description/disable-model-invocation |
| `disable-model-invocation: true` | 告诉 Agent "别自己推理，调 CLI" |
| argparse 而不是 Click/Typer | 减少依赖，Agent 更熟悉 argparse 格式 |
| `--dry-run` 在所有写操作上 | 防止 Agent 误操作 |
| `src/` 布局而不是平铺 | 避免 Python import 路径污染 |
| `uv` 而不是 `pip` | 更快、更可靠、lock 文件支持 |
| 离线测试默认运行 | 不需要任何密钥就能验证 |
| `.env.example` 只有假值 | 从第一天就是公开安全的 |
| `docs/working.md` 持续追加 | 保留决策上下文，Agent 能回溯 |

