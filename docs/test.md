# Test Strategy

## What we test

`design-flow` 是 Markdown skill + 一个 python3 脚本。测试分两层：脚本验证 + skill 验收清单（可机械检查）。

### scripts/analyze.py（确定性脚本）

已用合成 fixture 测过（3 受访者 / 2 archetype / 全题型含 uncertain）：count / mean / median / 分布 / 交叉表 / ranking 平均排名 / uncertain 排除 均正确。回归检查：改脚本后重跑该 fixture 对比 `stats.json`。

fixture 放 `runs/test/`（gitignore，不入库），重跑：

```bash
# 重建 fixture 后
python3 scripts/analyze.py runs/test/
python3 -m json.tool runs/test/stats.json
```

未来可加 `tests/test_analyze.py`（pytest，离线），当脚本复杂化或出现第二个脚本时引入。

### Acceptance Criteria（每步验收，可机械检查）

**WF1 survey.json**：合法 JSON；含 `research_question` / `target_population` / `purpose` / `recommended_n` / `questions`；每题 `question_id` 唯一 + `construct_measured` 非空；likert 题 `scale` 含 `low` / `high`；options 互斥穷尽；题序 筛选→行为→态度→开放；题数 ≤ 15、分钟 ≤ 5。

**WF2 archetypes.json**：原型 5-8；`archetype_id` 唯一；`proportion` 合计 = 1.0；每原型 `变量设定` 含类型（五类）/ 变量 / 取值 / 来源（`question_id` 可追溯）；变量类型不含结果构念；每原型有 `预期回答倾向`（整体定性）+ `预期影响construct`。

**WF3 respondents.jsonl + meta**：每行合法 JSON 含 `respondent_id` 唯一 + `archetype_id` 可追溯 + 五层；五层均非空；同 archetype 下任意两体 ≥ 3 维不同；行数 = N、`by_archetype` 合计 = 行数；五层不含结果构念键；meta 含 `count` / `by_archetype` / `confidence` / `anti_pattern_checks` / `note`；`note` 含"合成样本"+"预调研"。

**WF4 responses.jsonl + meta**：每行含 `respondent_id`（一一对应 respondents）+ `answers`；`answers` 覆盖 survey 所有题；answer 强类型（likert int 量程内 / single-choice 在 options 内）；关键题有 `reasoning`；无直线作答 / 全 uncertain；meta 含 `count` / `quality` / `invalid_patterns_detected` / `note`；`note` 含"合成样本"+"预调研"。

**WF5 stats.json + report.md**：`stats.json` 含 `total_n` / `per_question` / `cross_tabs_by_archetype`；`report.md` 含 6 章节；报告头部含"合成样本"+"预调研"+样本量+置信度；每条开放观察贴 source id 且覆盖全部 `respondent_id`；单源模式有标记；每统计结论附 n；报告含"需真实用户验证的假设"段。

### Pipeline 手动 QA 场景

| # | 场景 | 期望 |
|---|---|---|
| 1 | 给研究问题跑 run-pipeline 全链 | 5 步产出齐全、步间暂停、report.md 区分模拟 vs 假设 |
| 2 | WF1 给烂问卷（双重题） | 验收拦下、要求修订 |
| 3 | WF2 把"使用意愿"塞进变量设定 | 红线触发、拒绝 |
| 4 | WF3 同 archetype 个体复制 | anti-pattern elastic 拦下、重生成 |
| 5 | WF4 全 uncertain 作答 | `no_invalid_responding` 降级 |
| 6 | WF5 LLM 自算统计而非调脚本 | 拦下、要求走 `analyze.py` |

### 回归检查（发布前）

1. 跑隐私扫描（见下）
2. 重跑 `analyze.py` 合成 fixture 对比 `stats.json`
3. 确认根 SKILL ≤ ~200 行
4. 确认 5 个 workflow 验收标准仍可机械检查
5. 确认安装目录名为 `design-flow`（kebab），与 skill `name` 一致（带空格的目录名会触发 linter 警告；改名会改 cwd，在会话停顿点做）

## 隐私扫描（发布前必跑）

```bash
rg -n "op://|sk-[a-zA-Z0-9]{10,}|/Users/" .
```

扫描 1Password 引用（`op://`）、API key 风格串（`sk-` + 10+ 字符）、绝对用户路径（`/Users/`）。任何匹配都是红线。本命令会在 `AGENTS.md` 与 `docs/test.md` 自匹配（命令本身含 `op://` 与 `/Users/`），忽略这两处。`rg` 默认跳过 gitignore 文件，故 `reference-docs/`、`构建路线图.md`、`runs/` 不扫。本 skill 无 env 变量，故无 `.env.example`；示例 persona / 数据集必须虚构合成。

## What we don't test (yet)

- CI 自动化（skill 主体是 Markdown，无 build）
- LLM 作答质量的客观回归（需真实对照样本，本工具定位预调研，不强求）
