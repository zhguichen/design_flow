# Behavior Mechanism Library

Use this reference in WF2 Phase B to route from questionnaire topic to human/social behavior mechanisms. Do not treat mechanism cards as evidence that a population type exists or as proof of prevalence. They are reasoning templates that make synthetic scenarios explicit, falsifiable, and easier to calibrate with real data.

## Core Rule

Include a group only when this chain is coherent:

`target context -> actor condition -> constraint/resource -> mechanism -> surface need -> hypothesized latent motive`

Exclude combinations that are merely possible but lack a mechanism, contradict the target population, duplicate another group, or do not affect the questionnaire scope. Selecting a card is `model-inference`, not target-context evidence. Do not write predicted answer directions into `behavior_mechanisms.json`; preregister them separately in sealed `hypotheses.json`.

## Evidence Rule

- A mechanism card is a reasoning template, not a citation.
- Use `user-evidence` only when a concrete user-provided artifact or source id supports the target context.
- Use `cited-research` only when a verifiable reference directly supports the relevant population, context, or mechanism link.
- Otherwise use `model-inference`; its plausibility cannot exceed `plausible`.
- Always record an alternative explanation and a falsification probe.

## Domain Router

| Questionnaire focus | Mechanisms to consider | Answer differences usually appear in |
|---|---|---|
| Technology/tool adoption | TAM, UTAUT, TPB, risk perception, self-efficacy | Use intention, trust, ease, effort, price, support |
| Product purchase/ownership | Loss aversion, price sensitivity, identity signaling, habit, social comparison | Purchase intent, willingness to pay, brand/style preference |
| Space/environment experience | Environmental control, crowding, perceived safety, privacy, place attachment, wayfinding load | Satisfaction, usage frequency, avoidance, desired features |
| Visual/aesthetic preference | Familiarity preference, cultural capital, identity fit, affective association, category recognition | Preference ratings, perceived quality, emotional response |
| Service participation | Trust, perceived cost-benefit, procedural fairness, social norm, service recovery | Adoption, complaint, loyalty, drop-off, recommendation |
| Public/social design | Institutional trust, fairness perception, group interest, risk perception, perceived efficacy | Support/opposition, participation, compliance |
| Habit/lifestyle change | Habit loop, self-efficacy, friction, social support, implementation intention | Intention-behavior gap, persistence, relapse, barriers |
| Need discovery/hypothesized motive | Stress appraisal, scarcity, compensation, defensive need, social desirability | Surface answers vs hypothesized underlying motive, priority, willingness |
| Survey answering itself | Comprehension-retrieval-judgment-response, satisficing, impression management | Middle choices, uncertainty, socially desirable answers |

## Mechanism Cards

### M-TPB: Attitude, Norm, Control

- Basis: Theory of Planned Behavior.
- Logic: Intention is shaped by attitude toward the behavior, perceived social pressure, and perceived behavioral control.
- Use when: the questionnaire asks whether someone will do, adopt, participate in, or change something.
- Surface answer: "I want/don't want to do it."
- Hypothesized latent motive: "Important others approve/disapprove" or "I can/cannot realistically do it."
- Watch for: high attitude but low control; public approval but private resistance.

### M-TAM-UTAUT: Technology/Tool Acceptance

- Basis: Technology Acceptance Model and Unified Theory of Acceptance and Use of Technology.
- Logic: Perceived usefulness/performance, ease/effort, social influence, and facilitating conditions shape technology use.
- Use when: the object is a tool, platform, AI system, app, software, or digital service.
- Surface answer: "It is efficient/useful/easy."
- Hypothesized latent motive: "It reduces effort, helps performance, or is accepted by the relevant group."
- Watch for: not relevant to non-technology topics unless the design object is a tool.

### M-STRESS-COPING: Threat Appraisal and Coping

- Basis: Stress appraisal and coping.
- Logic: People evaluate whether a situation is a threat/challenge, then evaluate whether their resources are enough; if not, they seek coping strategies.
- Use when: deadline, evaluation, uncertainty, risk, or shortage is central.
- Surface answer: "I need efficiency/help."
- Hypothesized latent motive: "I need to reduce threat, uncertainty, or failure risk."
- Watch for: coping can be problem-focused (solve it) or emotion-focused (feel safer).

### M-SCARCITY: Resource Scarcity and Cognitive Bandwidth

- Basis: scarcity and cognitive bandwidth research.
- Logic: shortage of time, money, social access, or attention narrows focus toward immediate relief and reduces capacity for complex evaluation.
- Use when: users lack time, budget, channels, support, or reliable resources.
- Surface answer: "I want something fast/cheap."
- Hypothesized latent motive: "I need a viable path under constraint."
- Watch for: short-term acceptance with low willingness to pay or high later regret.

### M-SELF-EFFICACY: Perceived Capability

- Basis: self-efficacy theory.
- Logic: People are more likely to initiate and persist when they believe they can perform the behavior successfully.
- Use when: method ability, tool skill, learning confidence, or execution ability matters.
- Surface answer: "This is too hard/easy."
- Hypothesized latent motive: "I do/don't believe I can handle the process."
- Watch for: low self-efficacy can look like low interest.

### M-SOCIAL-DESIRABILITY: Impression Management

- Basis: social desirability and response bias.
- Logic: People may answer in ways that present themselves as competent, ethical, diligent, or socially acceptable.
- Use when: topics involve morality, professionalism, academic norms, health, sustainability, taste, or status.
- Surface answer: "I care about the correct thing."
- Hypothesized latent motive: "I want to look legitimate or avoid judgment."
- Watch for: public answer differs from private action.

### M-SURVEY-RESPONSE: Answer Construction

- Basis: survey response psychology.
- Logic: A survey answer is constructed through comprehension, retrieval, judgment, and response selection.
- Use when: questions are abstract, recall-heavy, sensitive, technical, or unfamiliar.
- Surface answer: selected option.
- Hypothesized latent motive: may be uncertainty, limited recall, or difficulty mapping a feeling to options.
- Watch for: middle choices, "not sure", inconsistent details, short open answers.

### M-COGNITIVE-DISSONANCE: Consistency Repair

- Basis: cognitive dissonance theory.
- Logic: People reduce discomfort when attitudes, actions, or self-image conflict.
- Use when: users act against stated values, justify past choices, or defend a behavior.
- Surface answer: "This is reasonable because..."
- Hypothesized latent motive: "I need my behavior and self-image to feel consistent."
- Watch for: post-hoc rationalization.

### M-ENV-CONTROL: Environmental Control and Safety

- Basis: environmental psychology.
- Logic: Perceived control, privacy, safety, crowding, noise, and wayfinding affect space satisfaction and use.
- Use when: questionnaire concerns space, service environment, campus/public place, store, exhibition, home, transport, or workplace.
- Surface answer: "The space is comfortable/uncomfortable."
- Hypothesized latent motive: "I can/cannot control noise, privacy, movement, safety, or resources."
- Watch for: avoidance despite stated liking.

### M-IDENTITY-SIGNALING: Identity and Cultural Fit

- Basis: identity signaling, cultural capital, and social comparison.
- Logic: People choose objects/styles/brands that fit the identity they want to express or the group they want to belong to.
- Use when: aesthetic preference, brand, packaging, fashion, lifestyle, or visible consumption matters.
- Surface answer: "It looks good / has style."
- Hypothesized latent motive: "It fits who I am or who I want others to think I am."
- Watch for: "taste" masking status, belonging, or distinction.

### M-PRICE-LOSS: Price Sensitivity and Loss Aversion

- Basis: behavioral economics.
- Logic: People weigh possible losses more strongly than equivalent gains, especially under budget limits or uncertain benefits.
- Use when: price, payment, switching cost, risk, subscription, or trial is involved.
- Surface answer: "Too expensive."
- Hypothesized latent motive: "I am not sure the value will materialize, so payment feels risky."
- Watch for: free trial or refund changes acceptance.

### M-HABIT-FRICTION: Habit and Friction

- Basis: habit formation and behavior change.
- Logic: Existing routines, cues, effort, and immediate rewards shape whether people change behavior.
- Use when: questionnaire concerns repeated behavior, lifestyle, learning, commuting, exercise, recycling, app use, or routines.
- Surface answer: "I want to change."
- Hypothesized latent motive: "My environment and habits make change easy/hard."
- Watch for: high stated intention but low sustained behavior.

## Demand Authenticity Labels

- `real_need`: directly grounded in constraint, pain, or desired outcome.
- `surface_need`: stated reason is real but incomplete; deeper motive exists.
- `contextual_need`: strong only under certain events or pressure.
- `defensive_need`: framed to avoid blame, judgment, or ethical risk.
- `socially_desirable_need`: answer aligns with what sounds correct or professional.
- `compensatory_need`: tool/design compensates for missing ability, resource, confidence, or support.
- `pseudo_need`: attractive in abstract but weak scenario, weak effort willingness, or no stable trigger.

## Confidence

- `high`: mechanism is directly matched to topic and questionnaire includes multiple supporting questions.
- `medium`: mechanism is plausible and affects answers, but evidence is mainly inferred from context.
- `low`: mechanism is speculative; keep as weak signal or exclude if it does not change answers.
