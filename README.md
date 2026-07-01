# design-flow

面向设计类学生 / 从业者的 Claude Code Skill：用 AI 合成样本帮助问卷预调研，覆盖"设计问卷 → 反推人群 → 生成 persona → LLM 模拟填写 → 收集结果 → 分析"全链路。

**边界：预调研工具，不替代真实用户研究。** 替代的是低质量、随便发、没人认真填的学生式问卷调研。

## 它解决什么

设计学生做问卷调研时：找不到足够目标用户、找到的不是目标用户、填写者敷衍乱填。本 skill 生成一批认真、符合目标人群、按自身处境作答的合成受访者，比随便找同学互填更有逻辑、更稳定、更接近目标人群。

## 它不做什么

- 不替代真实用户研究或专业样本采集
- 不做正式发表级统计
- 不分发问卷 / 收集真实填答
- 合成样本不当真人证据

## 安装

本 skill 是轻量 Markdown skill（暂不打包成插件）。把仓库 clone 或拷贝到稳定位置，把根 `SKILL.md` 加入你的 AI agent 工作区 skill 发现链（INDEX.md / AGENTS.md / CLAUDE.md）。保持 `workflows/`、`commands/`、`scripts/`、`references/` 与 `SKILL.md` 同级，使相对引用能解析。

需要 `python3`（标准库即可，无第三方包）跑 Workflow 5 的统计。

## 使用

给 AI agent 一句研究问题，用编排命令跑全链：

```
/design-flow:run-pipeline 年轻租房群体对模块化家具的需求与购买决策调研
```

步间会暂停确认。也可只跑某一步（如只设计问卷），agent 直接 load 对应 `workflows/0X-*.md`。

产出落在 `runs/<时间戳>/`：`survey.json` → `archetypes.json` → `respondents.jsonl` → `responses.jsonl` → `stats.json` + `report.md`。

## 结构

- `SKILL.md` — 根 skill（唯一入口，路由到 workflows）
- `workflows/01..05-*.md` — 问卷设计 / 人群反推 / persona 生成 / 模拟作答 / 结果分析
- `commands/run-pipeline.md` — 串联 1→5 的编排命令
- `scripts/analyze.py` — WF5 确定性统计
- `docs/{prd,rfc,working,test}.md` — 需求 / 架构 / 变更日志 / 测试
- `AGENTS.md` — 给维护 Agent 看

## 隐私

本仓库设计为公开安全：无真实凭据、内部路径、真实联系人。示例 persona / 数据集均虚构合成。发布前隐私检查见 `docs/test.md`。

## License

MIT
