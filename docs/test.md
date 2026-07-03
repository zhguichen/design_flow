# Test Strategy

## What we test

`design-flow` 是 Markdown skill + 三个 python3 标准库脚本。测试分两层：脚本验证 + skill 方法验收。

### scripts/analyze.py（确定性脚本）

已用合成 fixture 测过（3 受访者 / 2 archetype / 全题型含 uncertain）：count / mean / median / 分布 / 交叉表 / ranking 平均排名 / uncertain 排除 均正确。回归检查：改脚本后重跑该 fixture 对比 `stats.json`。

fixture 放 `runs/test/`（gitignore，不入库），重跑：

```bash
# 重建 fixture 后
python3 scripts/analyze.py runs/test/
python3 -m json.tool runs/test/stats.json
```

### scripts/validate_run.py（统一契约校验）

对现有运行目录验证正反路径：符合当前契约的 WF1/WF2A/WF2B 通过；旧版含摩擦分数、重复机制字段的运行目录在 WF2C/WF3/WF4 被拒绝。发布前至少运行一次通过路径与一次预期失败路径，并检查错误信息指向具体文件或记录。

### scripts/select_respondents.py（确定性分层选择）

验证同一 persona pool、n 和 seed 重复运行得到相同 id；pilot 覆盖全部 archetype；n 小于 archetype 数、等于或大于 pool 时必须失败；`full` 必须选择全部 persona。

### Acceptance Criteria

字段结构、id 唯一性、禁止字段、跨文件引用和强类型只有一个机械事实来源：`scripts/validate_run.py`。各 workflow 的“完成前确认”只保留无法可靠自动判断的方法质量。

| 阶段 | 命令 | 仍需人工/模型判断 |
|---|---|---|
| WF1 | `python3 scripts/validate_run.py runs/<ts>/ --stage wf1` | 题序、偏差、措辞与研究适配 |
| WF2 Phase A | `... --stage wf2a` | 原型是否自洽、是否真的影响回答 |
| WF2 Phase B | `... --stage wf2b` | domain 路由、机制合理性与竞争解释 |
| WF2 Phase C | `... --stage wf2c` | drivers 是否可观察、假设是否有意义 |
| WF3 | `... --stage wf3` | persona 是否自然、同类差异是否可信 |
| WF4 | `... --stage wf4` | selection 是否符合用户模式、reasoning 是否像该 persona、是否存在无效模式 |
| WF5 | `python3 scripts/analyze.py runs/<ts>/` 后运行 `... --stage wf5` | 主题编码、机制解释与设计建议 |

### Pipeline 手动 QA 场景

| # | 场景 | 期望 |
|---|---|---|
| 1 | 给研究问题跑 run-pipeline 全链 | 7 个执行阶段产出齐全；只在问卷、audience package + N、persona 抽查 + 模拟模式三处确认；report.md 区分模拟 / 机制与任务摩擦解释 / 假设 |
| 2 | WF1 给烂问卷（双重题） | 验收拦下、要求修订 |
| 3 | WF2 把"使用意愿"塞进变量设定 | 红线触发、拒绝 |
| 4 | WF3 同 archetype 个体复制 | anti-pattern elastic 拦下、重生成 |
| 5 | WF4 全 uncertain 作答 | `no_invalid_responding` 降级 |
| 6 | WF5 LLM 自算统计而非调脚本 | 拦下、要求走 `analyze.py` |
| 7 | 非技术问卷 WF2 Phase B 默认套 TAM/UTAUT | 拦下，要求按 domain 路由机制 |
| 8 | WF2 Phase A 原型没有机制支撑 | Phase B 要求删除、合并或重写，不能进 WF3 |
| 9 | WF2 把所有可能组合都纳入 | 拦下，要求只保留有机制链且影响回答的类型 |
| 10 | WF4 对“哪个环节更麻烦”只按性格作答，或按摩擦分数查表 | 拦下；WF2 Phase C drivers 必须先事实化进 persona，WF4 只根据人物故事独立作答 |
| 11 | 问卷只有“是否愿意”没有痛点/任务题 | 回 WF1 重写问卷，不能进入 WF2 Phase C |
| 12 | WF3 / WF4 读取 `hypotheses.json` 或复制预测方向 | 拦下；清除预测字段后重新生成，WF5 前保持封存 |
| 13 | 模拟结果不支持预注册假设 | 保留原结果，WF5 标记 `not_supported` 或 `inconclusive`，不得重生成 |
| 14 | WF2 没有真实分布依据却给出不等权“现实比例” | 拦下；改用 `coverage-default` 等权，或要求明确标注用户设定/模型假设 |
| 15 | WF5 把模拟百分比解释为目标总体发生率 | 拦下；改写为本次合成场景内模式并声明不可外推 |
| 16 | WF2 Phase B 只套理论卡片就标 `supported` | 拦下；改为 `model-inference` + `plausible/speculative`，补替代解释与证伪条件 |
| 17 | 报告把假设性潜在动机写成受访者事实 | 拦下；改用“可能解释/待验证”，并显示证据等级 |
| 18 | run-pipeline 在内部 Phase 重复询问“是否继续”，或确认门只给验收结果不展示产出 | 拦下；只保留三道门，并完整展示自上次门禁以来的产出 |
| 19 | WF1 未获得模拟规模就填 `null` 并继续 | 允许；WF1 只记录已有预算偏好，统一在 audience package 门禁确认 |
| 20 | WF2 Phase A 单独询问 `simulation_n`，或 Phase C 后未确认最终值就进入 WF3 | 拦下；只在完整 audience package 门禁确认一次 |
| 21 | 用户在门 3 手工挑选具体 persona | 拦下；用户只选择 `full` 或指定 pilot n，具体 id 由脚本按 archetype 分层选择 |
| 22 | pilot n 小于 archetype 数，或报告未标有限覆盖 | 拦下；重新选择 n，并在报告声明“分层预演 / 不代表完整场景覆盖” |
| 23 | JSON 字符串中的自然语言短语需要加引号 | 使用 `「」`，写入后通过 JSON 解析；不得直接嵌入未转义的 ASCII 双引号 |

### 回归检查（发布前）

1. 运行 `claude plugin validate . --strict` 和 `claude plugin validate ./design_flow --strict`
2. 确认 marketplace 与 plugin 的 `version` 一致；每次发布都递增语义版本并创建对应的 `v<version>` Git tag
3. 跑隐私扫描（见下）
4. 重跑 `analyze.py` 合成 fixture 对比 `stats.json`
5. 确认根 SKILL ≤ ~200 行
6. 确认 5 个 workflow 文件、7 个执行阶段的验收标准仍可机械检查
7. 用 `claude --plugin-dir ./design_flow` 启动一次干净会话，确认 `/design-flow:run-pipeline` 可发现，且脚本从 `${CLAUDE_PLUGIN_ROOT}` 解析、产出写到当前项目的 `runs/`

## 隐私扫描（发布前必跑）

```bash
rg --hidden -g '!.git/**' -n "op://|sk-[a-zA-Z0-9]{10,}|/Users/" .
```

扫描 1Password 引用（`op://`）、API key 风格串（`sk-` + 10+ 字符）、绝对用户路径（`/Users/`），并用 `--hidden` 覆盖 `.claude-plugin/`。任何匹配都是红线。本命令会在 `AGENTS.md` 与 `docs/test.md` 自匹配（命令本身含 `op://` 与 `/Users/`），忽略这两处。`rg` 仍跳过 gitignore 文件，故 `reference-docs/`、`构建路线图.md`、`runs/` 不扫。本 skill 无 env 变量，故无 `.env.example`；示例 persona / 数据集必须虚构合成。

## What we don't test (yet)

- CI 自动化（skill 主体是 Markdown，无 build）
- LLM 作答质量的客观回归（需真实对照样本，本工具定位预调研，不强求）
