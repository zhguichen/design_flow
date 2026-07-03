# design-flow

面向设计类学生 / 从业者的 Claude Code Skill：用 AI 合成场景帮助问卷预调研，覆盖"设计问卷 → 反推人群 → 行为机制映射 → 任务摩擦映射 → 生成 persona → LLM 模拟填写 → 收集结果 → 分析"全链路。

**边界：预调研工具，不替代真实用户研究。** 替代的是低质量、随便发、没人认真填的学生式问卷调研。

## 它解决什么

设计学生做问卷调研时：找不到足够目标用户、找到的不是目标用户、填写者敷衍乱填。本 skill 生成一组合成受访者场景，并用证据分级、可证伪的行为机制假设和任务摩擦解释场景，用于预检问卷和比较不同情景。机制使场景更明确，不证明这类人真实存在；合成记录也不证明现实人群比例，不因生成数量增加而更接近目标总体。

## 它不做什么

- 不替代真实用户研究或专业样本采集
- 不做正式发表级统计
- 不分发问卷 / 收集真实填答
- 合成样本不当真人证据

## 安装

本仓库按 Claude Code plugin + marketplace 发布。先安装最新版 Claude Code，然后执行：

```bash
claude plugin marketplace add zhguichen/design_flow
claude plugin install design-flow@design-flow
```

插件默认安装到 user scope，可在所有项目中使用。安装后不需要每次指定 Skill 工作目录；只需先进入希望保存调研产出的项目目录，再启动 Claude：

```bash
mkdir -p my-survey-project
cd my-survey-project
claude
```

此时当前项目目录是运行工作目录，生成内容会写入其中的 `runs/<时间戳>/`。

本地开发或尚未推送到 GitHub 时，在仓库根目录运行 `claude --plugin-dir ./design_flow`。`--plugin-dir` 指向插件目录，不是产出目录；如需在另一个项目里测试，可传绝对路径。

需要 `python3`（标准库即可，无第三方包）做 persona 分层选择、每阶段结构校验和 Workflow 5 统计。

## 新手入口

第一次使用、不熟悉 Skill 或用户研究流程，先读：

- [小白使用指南](guides/getting-started.md) — 从准备研究问题到阅读最终报告的操作指南
- [Workflow 设计理念](guides/workflow-design.md) — 7 个执行阶段为什么这样设计、各自防止什么错误

## 使用

给 AI agent 一句研究问题，用编排命令跑全链：

```
/design-flow:run-pipeline 年轻租房群体对模块化家具的需求与购买决策调研
```

全链只在问卷、audience package + 模拟规模、persona 抽查 + 模拟模式三处暂停确认。也可只跑某一步（如只设计问卷），agent 直接 load 对应 `workflows/0X-*.md`。

产出落在 `runs/<时间戳>/`：`survey.json` → `archetypes.json` → `behavior_mechanisms.json` → `task_frictions.json` + 封存的 `hypotheses.json` → `respondents.jsonl` → `selection.json` → `responses.jsonl` → `stats.json` + `report.md`。门 3 可选择全部模拟，或只指定 n 做确定性分层预演；用户不手工挑 persona。WF3 / WF4 不读取预测，WF5 才打开假设逐条对照。

如果是给队友看本轮修改，先读 `docs/change-summary.md`。

## 结构

- `.claude-plugin/marketplace.json` — 仓库 marketplace 目录
- `design_flow/.claude-plugin/plugin.json` — plugin 元数据与版本
- `design_flow/SKILL.md` — 根 skill（唯一入口，路由到 workflows）
- `design_flow/workflows/*.md` — 5 个 workflow 文件；WF2 内含人群反推 / 行为机制映射 / 任务摩擦映射三个 Phase，共 7 个执行阶段
- `design_flow/commands/run-pipeline.md` — 串联 1→2A→2B→2C→3→4→5 的编排命令
- `design_flow/scripts/*.py` — 分层选择、契约校验与确定性统计
- `guides/` — 面向新手的使用说明与 workflow 设计理念
- `docs/{prd,rfc,working,test}.md` — 需求 / 架构 / 变更日志 / 测试
- `AGENTS.md` — 给维护 Agent 看

## 隐私

本仓库设计为公开安全：无真实凭据、内部路径、真实联系人。示例 persona / 数据集均虚构合成。发布前隐私检查见 `docs/test.md`。

## License

[MIT](LICENSE)
