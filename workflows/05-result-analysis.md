# Workflow 5：结果分析 (result-analysis)

对合成数据集做描述统计 + 开放题主题编码 + 分群交叉分析 + 机制/任务摩擦解释，产出洞察与设计启示。报告显式区分"模拟数据显示的模式"、"机制与任务摩擦推导出的解释"、"需真实用户验证的假设"。

按需从根 `SKILL.md` 加载。依赖 WF4 的 `responses.jsonl` 等。pipeline 终端步骤。

## When to use

- `responses.jsonl` 已就绪，需要分析
- WF4 完成后由 pipeline 推进（pipeline 终点）

不适用：无 `responses.jsonl` → 回 WF4。

## 输入

- `runs/<时间戳>/responses.jsonl` + `responses_meta.json`
- `runs/<时间戳>/survey.json` + `archetypes.json` + `behavior_mechanisms.json` + `task_frictions.json` + `respondents.jsonl`

## 输出

- `runs/<时间戳>/stats.json` — 确定性统计（phase 1，脚本生成）
- `runs/<时间戳>/report.md` — 分析报告（phase 2，LLM 生成，终端交付物）

## 方法

### Phase 1：确定性统计（脚本）

```bash
python3 scripts/analyze.py runs/<时间戳>/
```

生成 `stats.json`，含：

- `total_n` / `by_archetype`：样本量与分群量
- `per_question`：每题统计
  - likert / rating / nps：count / mean / median / min / max / distribution / uncertain_count
  - single-choice / multi-select：count / distribution / uncertain_count
  - open：全部答案待 LLM 编码
  - ranking：每项平均排名
- `cross_tabs_by_archetype`：每题按 archetype 分群的统计

> 脚本只出事实，不出判断。统计由确定性代码算，避免 LLM 算术错误（"确定性工具出事实，模型出判断"）。

### Phase 2：主题编码 + 洞察 + 报告（LLM）

LLM 读 `stats.json` + `responses.jsonl`（开放题原文 + reasoning），做：

1. **描述统计呈现**：每题展示分布（Likert 看全分布不只均值）；**每条结论附样本量**。
2. **开放题主题编码**（搬 affinity-diagram）：
   - 提取每条开放答案与 reasoning 中的观察
   - 自下而上聚类 → 命名主题 → 写洞察陈述（"so what"）
   - **Cross-Interview Sampling Principle（强制）**：每条观察贴 source `respondent_id`；聚类后验证每个受访者至少出现一次；单源模式标记
3. **分群交叉分析**：用 `cross_tabs_by_archetype` 看 archetype 间差异（如"赶作业型 vs 方法认真型"的使用意愿差异）。
4. **机制/任务摩擦解释**：读 `behavior_mechanisms.json`、`task_frictions.json` 与 responses 的 `mechanism_id` / `friction_dimension_id` / `reasoning`，解释表层需求、潜在动机、需求真实性标签和任务摩擦如何影响答案。
5. **设计启示**：从统计模式 + 机制/任务摩擦解释推出对设计决策的启示。设计启示必须能回到具体机制或摩擦维度，不只回到均值。
6. **置信度与局限**：声明 合成样本 / 样本量 / 置信度 / 仅供预调研；**显式区分**：
   - "模拟数据显示的模式"（数据里看到的）
   - "机制与任务摩擦推导出的解释"（由 WF2.5 机制与 WF2.6 任务摩擦解释的原因链）
   - "需真实用户验证的假设"（推论出的、待真人验证）

### Cross-Interview Sampling Principle（强制，防 LLM 偏差）

LLM 易用前几个 persona 类型下结论。强制：

- 每条观察贴 source `respondent_id`
- 索引均匀覆盖所有受访者，不为前几个主导
- 聚类后验证每个受访者至少出现一次 → 缺则回补
- 单一来源的模式标记为"单源"，不作强结论

## report.md 结构

```markdown
# 分析报告：<研究问题>

> 合成样本 / N=<n> / 置信度=<overall> / 仅供预调研

## 1. 样本概况
- 总样本量、分群分布

## 2. 描述统计
### <construct>（Qx）
- 分布 / 均值 / 中位数（附 n）

## 3. 开放题主题
### 主题 A：<名称>
- 洞察：<so what>
- 证据：[R001] ... [R017] ...（每条贴 source id；标注单源）

## 4. 分群差异
| archetype | 使用意愿均值 | ... |
|---|---|---|

## 5. 机制与任务摩擦解释
- 表层需求：...
- 潜在动机：...
- 需求真实性：...
- 任务摩擦：...
- 对作答的影响：...

## 6. 设计启示
- ...

## 7. 置信度与局限
- 模拟数据显示的模式：...
- 机制推导出的解释：...
- 需真实用户验证的假设：...
- 局限：合成样本、单源 LLM、不替代真实研究
```

## 红线

- 报告头部标注 合成样本 / 样本量 / 置信度 / 仅供预调研。
- 显式区分"模拟数据显示的模式"、"机制与任务摩擦推导出的解释"、"需真实用户验证的假设"。
- 设计启示必须回到机制链或任务摩擦维度，不能只说统计高低。
- 全 pipeline 红线继承。

## 验收标准（可机械检查）

- [ ] `stats.json` 存在（phase 1 脚本产出），含 `total_n` / `per_question` / `cross_tabs_by_archetype`。
- [ ] `report.md` 存在，含 7 个章节。
- [ ] 报告头部含"合成样本"与"预调研"与样本量与置信度。
- [ ] 每条开放题观察贴了 source `respondent_id`（`grep -o '\[R[0-9]\+\]' report.md | sort -u` 数量 ≥ 受访者数）。
- [ ] 每个受访者至少出现一次（source id 覆盖 = 全部 `respondent_id`）。
- [ ] 单源模式有标记。
- [ ] 每条统计结论附样本量（n=...）。
- [ ] 报告含"机制与任务摩擦解释"与"需真实用户验证的假设"段。
- [ ] 至少一条设计启示能追溯到 `behavior_mechanisms.json` 的机制 id/名称，或 `task_frictions.json` 的摩擦维度 id/名称。

## Stop 条件

- 无 `responses.jsonl` → 回 WF4。
- `stats.json` 生成失败 → 检查 `responses.jsonl` 格式，不臆造统计。

## 示例

见上文 `report.md` 结构。完整报告见运行时产出。
