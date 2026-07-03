# Task Friction Framework

Use this reference in WF2.6 when the questionnaire asks about pain points, troublesome steps, barriers, priorities, or "which part is hardest." The goal is not to guess an individual's personality. The goal is to derive task-specific friction from context, behavior, constraints, capability, and mechanism traces.

## Core Rule

Do not answer pain-point questions from personality alone.

Use this chain:

`task context -> current behavior -> environment constraint -> capability/resource -> mechanism -> friction dimension -> likely pain answer`

If the chain cannot be built, mark the friction as low confidence or exclude it.

## Friction Dimensions

Use domain-specific wording, but keep the underlying dimensions stable:

| Dimension | Means | Usually raised by |
|---|---|---|
| `time_effort` | Takes too long, too many steps, interrupts schedule | time pressure, multitasking, deadline, fatigue |
| `physical_effort` | Body strain, manual labor, repetitive action | age, health, carrying, cleaning, cutting, standing |
| `cognitive_load` | Need to decide, remember, compare, plan, learn | low expertise, many choices, unfamiliar concepts |
| `risk_safety` | Fear of harm, failure, embarrassment, loss | children/elderly, public evaluation, fire/knife/privacy/data risk |
| `money_loss` | Price, waste, maintenance, regret, switching cost | budget limits, uncertain value, past idle purchases |
| `space_environment` | Space, layout, noise, storage, privacy, crowding | small homes, shared spaces, fixed equipment, commute |
| `identity_control` | Loss of autonomy, taste, craft, self-image | hobbies, expertise, cultural taste, professional identity |
| `social_coordination` | Needs agreement from family, peers, teacher, team | household roles, group work, authority approval |
| `maintenance_aftercare` | Cleaning, upkeep, repair, setup, learning overhead | complex products, hygiene, subscriptions, consumables |
| `habit_disruption` | Requires routine change or new behavior | low frequency, strong existing alternatives, frictionful onboarding |

## Scoring

Score each relevant task dimension from 1 to 5:

- `1`: rarely a problem for this archetype
- `2`: occasional minor friction
- `3`: noticeable but not decisive
- `4`: strong friction that affects answers
- `5`: dominant friction and likely top pain point

Every score must include:

- `drivers`: the concrete context variables that push the score up or down
- `mechanism_ids`: related WF2.5 mechanisms
- `affects_questions`: question ids likely affected
- `confidence`: `high`, `medium`, or `low`

## Domain Examples

### Kitchen Robot

- Small rental kitchen + limited counter space -> `space_environment=5`
- Children/elderly at home + hot oil/knife/fire risk -> `risk_safety=5`
- Enjoys cooking as craft -> `identity_control=5`, but `physical_effort` for cleaning/cutting may still be high
- Busy dual-income household -> `time_effort=5`, `maintenance_aftercare` must stay low
- Low cooking frequency + convenient delivery -> `habit_disruption=5`, purchase need low

### Design Student Survey Tool

- Deadline + no respondent channels -> `time_effort=5`, `social_coordination=4`
- Method-sensitive student -> `risk_safety=4` as method/ethics risk
- Low research literacy -> `cognitive_load=5`
- Low budget -> `money_loss=4`

### Public Service / Space Design

- Crowded space + poor wayfinding -> `space_environment=5`, `cognitive_load=4`
- Personal safety concerns -> `risk_safety=5`
- Shared resources -> `social_coordination=4`

## Output Principle

WF2.6 does not create final answers. It creates a `task_friction_profile` that WF3 embeds in respondents and WF4 uses when answering pain, ranking, priority, barrier, and open-ended questions.

When a survey question asks "which part is harder/more troublesome/more important," WF4 must answer from the highest-scoring relevant friction dimensions, with small variation only when persona-specific details justify it.
