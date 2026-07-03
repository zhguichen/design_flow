# Task Friction Framework

Use this reference in WF2 Phase C when the questionnaire asks about pain points, troublesome steps, barriers, priorities, or "which part is hardest." The goal is not to guess an individual's personality. The goal is to derive task-specific friction from context, behavior, constraints, capability, and mechanism traces.

## Core Rule

Do not answer pain-point questions from personality alone.

Use this chain:

`task context -> current behavior -> environment constraint -> capability/resource -> mechanism -> friction dimension`

If the chain cannot be built, mark the context mapping as low confidence or exclude it. Do not append an answer direction; predicted differences belong only in sealed `hypotheses.json`.

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

## Context Mapping

For each relevant task dimension, record:

- `drivers`: concrete, observable context variables
- `mechanism_ids`: related WF2 Phase B mechanisms
- `affects_questions`: question ids for which the persona needs relevant context
- `confidence`: `high`, `medium`, or `low`

Do not assign 1-5 friction scores, top-friction rankings, answer thresholds, or question answer rules. Those fields encode predicted outcomes and must not enter WF3/WF4.

## Domain Examples

### Kitchen Robot

- Small rental kitchen + limited counter space -> `space_environment`
- Children/elderly at home + hot oil/knife/fire risk -> `risk_safety`
- Enjoys cooking as craft -> `identity_control`; cleaning/cutting experience also supplies `physical_effort` context
- Busy dual-income household -> `time_effort` and `maintenance_aftercare`
- Low cooking frequency + convenient delivery -> `habit_disruption`

### Design Student Survey Tool

- Deadline + no respondent channels -> `time_effort`, `social_coordination`
- Method-sensitive student -> `risk_safety` as method/ethics risk
- Low research literacy -> `cognitive_load`
- Low budget -> `money_loss`

### Public Service / Space Design

- Crowded space + poor wayfinding -> `space_environment`, `cognitive_load`
- Personal safety concerns -> `risk_safety`
- Shared resources -> `social_coordination`

## Output Principle

WF2 Phase C does not create final answers or a score lookup table. It creates task-context coverage that WF3 translates into observable persona facts. WF4 receives only the persona story and mechanism trace, then answers independently.
