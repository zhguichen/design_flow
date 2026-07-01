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
