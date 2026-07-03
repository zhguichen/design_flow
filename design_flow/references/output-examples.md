# Output Examples

仅在需要澄清字段含义或向用户展示格式时加载。以下都是虚构合成片段，不是完整运行数据；正式产出以 workflow 合同与 `scripts/validate_run.py` 为准。

JSON / JSONL 的自然语言字符串需要引用短语时使用 `「」`，避免在字符串内部生成未转义的 ASCII 双引号：

```json
{"input_type":"能力","描述":"对设计风格关注较少，主要考虑「好不好打理」","相关题目":["Q6","Q7"]}
```

## WF1 survey.json

```json
{
  "research_question": "城市租房者在家具选购中遇到哪些任务摩擦",
  "target_population": "近半年购买过家具的城市租房者",
  "purpose": "pre-research",
  "simulation_n": null,
  "simulation_n_rationale": "待 WF2 根据最终 archetype 数统一建议并确认",
  "estimated_minutes": 4,
  "questions": [
    {
      "question_id": "Q1",
      "text": "选购过程中哪些环节最麻烦？",
      "type": "multi-select",
      "options": ["尺寸规划", "质量判断", "配送安装", "退换货"],
      "scale": null,
      "construct_measured": "痛点 / 阻力",
      "required": true
    }
  ]
}
```

## WF2 audience package

`archetypes.json` 中的单个原型：

```json
{
  "archetype_id": "A1",
  "name": "预算受限的短租者",
  "核心特征": "预算低、居住稳定性低、曾遇到退换货麻烦",
  "scenario_weight": 0.5,
  "weight_source": {"type": "coverage-default", "detail": "无真实分布依据，等权覆盖"},
  "变量设定": [
    {"类型": "资源", "变量": "家具预算", "取值": "低", "来源": ["Q1"]}
  ],
  "候选机制线索": ["损失规避", "风险感知"]
}
```

`behavior_mechanisms.json` 中的单个机制：

```json
{
  "mechanism_id": "M1",
  "name": "有限预算下的损失规避",
  "domain": "product_purchase",
  "applicable_archetypes": ["A1"],
  "affects_questions": ["Q1"],
  "logic": {"theory_basis": ["M-LOSS-AVERSION"], "mechanism_logic": "退换成本与预算限制放大失败后果"},
  "need_reading": {
    "surface_need": "避免买错",
    "hypothesized_latent_motive": "保护稀缺预算",
    "demand_authenticity": ["surface_need", "contextual_need"]
  },
  "evidence": {"level": "model-inference", "note": "无一手材料", "plausibility": "plausible"},
  "scrutiny": {
    "scope": "预算低且有退换经历者",
    "alternative_explanation": "也可能只是缺少品牌知识",
    "falsification_probe": "若预算差异与风险顾虑无关，则不支持"
  }
}
```

`task_frictions.json` 中的单个情境映射：

```json
{
  "F1": {
    "drivers": ["预算有限", "曾承担高额退货运费", "无法在线验证材质"],
    "mechanism_ids": ["M1"],
    "affects_questions": ["Q1"],
    "confidence": "high"
  }
}
```

## WF3 respondent

```json
{"respondent_id":"R001","archetype_id":"A1","基础身份":{"居住":"合租"},"社会处境":{"预算":"低","租期":"半年"},"心理倾向":{"风险偏好":"低"},"行为习惯":{"购买渠道":"线上","退换经历":"有"},"作答风格":{"是否承认不确定":"是"},"mechanism_trace":{"mechanism_ids":["M1"],"individual_expression":"预算紧张且经历过高额退货运费"}}
```

## WF4 response

门 3 生成的 `selection.json`：

```json
{
  "mode": "stratified-pilot",
  "pool_n": 30,
  "selected_n": 10,
  "seed": 42,
  "selected_respondent_ids": ["R001", "R004", "R008"],
  "by_archetype": {"A1": 2, "A2": 2, "A3": 2, "A4": 2, "A5": 2},
  "excluded_count": 20,
  "coverage": {"all_archetypes_included": true, "variants_target_met": false}
}
```

上面为字段片段，`selected_respondent_ids` 在正式文件中必须包含全部 10 个 id。

```json
{"respondent_id":"R001","answers":[{"question_id":"Q1","answer":["质量判断","退换货"],"reasoning":"上次材质与页面描述不符，退货运费又高。","mechanism_id":"M1","uncertain":false}]}
```
