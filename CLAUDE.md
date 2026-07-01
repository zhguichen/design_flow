# design-flow

本目录是一个 Claude Code Skill 项目。Skill 定义见 `SKILL.md`——把它作为首要操作合同加载。

当用户触发设计调研相关任务时，按 `SKILL.md` 的 Pipeline 路由表加载对应 workflow；串联场景使用 `/design-flow:run-pipeline` 命令（见 `commands/run-pipeline.md`）。

维护规约见 `AGENTS.md`。
