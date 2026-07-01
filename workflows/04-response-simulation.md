# Workflow 4：模拟作答与收集 (response-simulation)

LLM 以每个 persona 的身份**认真**作答问卷，产出答案 + 简短理由，汇总成数据集。默认"认真目标用户模式"：模拟有限理性/人格差异/不确定性；**不**模拟无效作答/随机/恶意反填；社会赞许偏差默认降低；没经历过就说"不确定"。输出 `responses.jsonl`，每行含 `respondent_id`、逐题 `answer` + `reasoning`。输出须标注合成样本。

> 占位文件，待填充（完整内容见后续 TODO-4）。
