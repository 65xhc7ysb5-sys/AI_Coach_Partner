

**PRODUCT REQUIREMENTS DOCUMENT**

**Linchpin Manager**

AI Coaching Navigator

Version 1.3  |  March 2026

Author: Jason Suk

Classification: Internal — Field Pilot

# **Version History**

Each version is documented across six categories to preserve decision context and evolution rationale.

| Version 1.1  —  Initial Release     March 2026     Status: Superseded |  |
| :---- | :---- |
| **Category** | **Detail** |
| **Target Audience** | Primary: Retail managers (Sales, Tech, Ops, People Experience) experiencing friction in coaching quality and cadence. |
| **Pain Point** | Passive team member attitudes toward coaching; lack of sharp, contextual questions for managers to break through defensiveness or stagnation. |
| **Business Goal** | Facilitate prep for intentional and quality coaching, addressing behaviours, rather than metrics in number; increase team-member-initiated coaching requests by 20% per quarter; accelerate coaching cadence from 31 days to 14 days; reduce logging time from 15-30 minutes to \<10min; increase quantity and quality of coaching therefore |
| **Core Features** | F1: Role-based dynamic input form. F2: Manager intuition data capture. F3: Unified GROW output engine (FUEL / OSKAR / Radical Candor / CLEAR). |
| **Technical Milestone** | Coaching Report prototype (ai\_engine.py \+ prompts.py); Gemini API integration; Streamlit UI; GitHub repository created (AI\_Coach\_Partner). |
| **Limitations & Next Version** | No field-validated data; KPIs based on hypothesis only; single-tab architecture with limited modularity. |

| Version 1.2  —  Field Research Addendum     March 2026     Status: Superseded |  |
| :---- | :---- |
| **Category** | **Detail** |
| **Target Audience** | No change. Primary: Retail managers (Sales, Tech, Ops, People Experience) experiencing friction in coaching quality and cadence. |
| **Pain Point** | 6 structured pain points validated through a manager interview. App intervention scope defined for 3 of 6 pain points. |
| **Business Goal** | Baseline established: coaching log time \= 15-20 min. Target: under 10 min. Manager self-efficacy score added as new KPI. |
| **Core Features** | F4: Coaching Log (STAR-based, FYI-aligned, manager-tone preserving). F5: DB storage for coaching reports and logs (SQLite). Prompt improvement direction. |
| **Technical Milestone** | database.py (SQLite schema, two tables); ai\_engine\_log.py merged into ai\_engine.py; app\_tabs/ refactor; E2E test automation (tests/test\_e2e.py); .gitignore and git history cleaned. |
| **Limitations & Next Version** | Document structure split between PRD v1.1 and Addendum; no integrated version history; single user research data point. |

| Version 1.3  —  Full Rewrite (Current)     March 2026     Status: Active |  |
| :---- | :---- |
| **Category** | **Detail** |
| **Target Audience** | Primary: Jason (product owner & pilot user) and Seul (first external pilot user) for the development of targeted functionality on demand. Secondary: Retail managers (V2 onward) experiencing friction in coaching quality and cadence. |
| **Pain Point** | Pain point framework refined: app scope vs. structural issues separated. Positioning: coaching-in-the-moment support tool, not a daily task manager. |
| **Business Goal** | 5 KPIs defined with measurement method. Coaching log time reduction as primary near-term metric. Manager self-efficacy as leading indicator. |
| **Core Features** | F1-F5 confirmed with implementation status. |
| **Technical Milestone** | Full PRD rewrite into a 9-section integrated document. docs/PRD.md added to Git repository. Version history introduced with structured 6-category format. |
| **Limitations & Next Version** | Single user research participant (n=1). No comparative data yet. Native app development gap unresolved. Auth logic placeholder only. |

# **1\. Executive Summary**

Linchpin Manager is an AI-powered coaching navigator built for retail people managers. It transforms fragmented performance data and manager intuition into structured, framework-driven coaching guidance — reducing preparation time, improving conversation quality, and creating a traceable record of team member development.

The product is currently in a two-person field pilot phase. The primary user serves as both product owner and pilot participant. A second manager joined as the first external pilot user following a structured interview that produced the first field-validated data points for this document.

This PRD supersedes the hypothesis-driven v1.1 and the addendum-based v1.2. All KPIs, feature priorities, and milestone targets in this document are anchored to observed field data unless explicitly noted as projections.

| Attribute | Detail |
| :---- | :---- |
| Project Name | Linchpin Manager (AI Coaching Navigator) |
| Current Version | 1.3 — Field Pilot |
| GitHub Repository | github.com/jasonsuk / AI\_Coach\_Partner |
| Primary Stack | Python, Streamlit, SQLite, Gemini API (google-genai) |
| Pilot Users | Jason (product owner), Seul (external pilot, n=1) |
| Pilot Phase Target | Two users reach consistent usage before wider recommendation |
| Post-Pilot Target | Expand to additional managers upon return from parental leave (October 2026\) |

# **2\. Problem Statement**

## **2.1  Observed Pain Points**

Six structural pain points were identified through direct observation and validated through a manager interview (Seul, March 2026). Each is assessed for whether the application can directly intervene.

| \# | Pain Point | App Intervention | Evidence Source |
| :---- | :---- | :---- | :---- |
| 1 | Managers prioritize operational floor coverage over scheduled coaching; prioritization of back-office administrative tasks reinforce reduced coaching hours | Partial — reduces prep friction, which lowers the activation threshold for coaching. | Field observation |
| 2 | Unplanned operational demands displace coaching time structurally; coverage roles are insufficient in volume. | Out of scope — structural and resourcing issue. | Field observation |
| 3 | Scheduled coaching utilization sits at 75% of target; compliance is inconsistent across the manager population. | Indirect — coaching quality improvement raises manager self-efficacy, which increases intrinsic motivation to coach. | Company data |
| 4 | Over 90% of team members have been in the same role for 3+ years; short-term goal activation only occurs when promotion opportunities are announced. | Indirect — exploratory questions can surface latent development motivation regardless of promotion pipeline. | Field observation |
| 5 | Team members lack development ownership or do not know how to exercise it; they defer to manager direction. | Direct — Co-Active based question design is built to transfer ownership to the team member. | Field observation \+ interview |
| 6 | Team-member-initiated coaching requests represent approximately 20% of total coaching volume; the remaining 80% is manager-initiated. | Direct — improved session quality creates positive reinforcement that increases voluntary request rate over time. | Company system data |

## **2.2  Field-Validated Baseline Metrics**

The following figures were established through the Seul interview (March 19, 2026\) and serve as the pre-intervention baseline for KPI measurement.

| Metric | Baseline (Pre-App) | Target | Source |
| :---- | :---- | :---- | :---- |
| Coaching log authoring time | 15–20 minutes per session | Under 10 minutes | Seul interview — self-reported |
| Coaching preparation time | 3–4 minutes (minimal prep) | Structured prep in under 5 minutes | Seul interview — self-reported |
| Coach Connection frequency | Approx. 40 sessions/month (target) | Maintain with improved quality | Seul interview |
| Team-member-initiated coaching | Approx. 20% of total sessions | 35% within 2 pilot quarters | Company system data |

# **3\. Target Users**

## **3.1  Primary Users — Field Pilot**

| Attribute | Jason (Product Owner) | Seul (Pilot User) |
| :---- | :---- | :---- |
| Role | Retail Manager — People Domain | Senior Retail Manager |
| Current Status | Parental leave; developing product | Active in store; first external tester |
| Coaching Cadence | — | Approx. 40 Coach Connections / month |
| Prep Behavior | — | Minimal (3–4 min); uses Internal App for context |
| Log Authoring | — | 15–20 min per session (current) |
| App Adoption Signal | Product owner; full usage expected | Will use selectively — primarily when stuck on approach or question design |
| Key Concern | — | Questions must be contextually relevant; generic outputs will cause abandonment |

## **3.2  Secondary Users — V2 Roadmap**

Managers without established coaching frameworks represent the secondary user segment. This group will be introduced after the primary pilot demonstrates consistent value. Their key need is guided structure rather than question augmentation — a distinction that may require a separate onboarding flow in V2.

# **4\. Business Goals**

All KPIs below are tied to measurable outcomes. Baseline values are sourced from field observation or the Seul pilot interview. Projections are marked accordingly.

| KPI | Baseline | Target | Measurement Method | Status |
| :---- | :---- | :---- | :---- | :---- |
| Coaching log authoring time | 15–20 min / session | Under 10 min / session | Manager self-report; timestamp delta in app (V2) | Baseline established |
| Coaching preparation time | 3–4 min (minimal) | Structured prep in under 5 min | Manager self-report; pre/post interview | Baseline established |
| Team-member coaching self-initiation rate | \~20% of sessions | 35% within 2 pilot quarters | Company system data (Internal App) | Projection |
| Coach Connection cadence | 31-day avg (system target) | 14-day avg | App session log; Internal App data | Projection |
| Manager coaching self-efficacy score | Not yet measured | Statistically significant improvement after 8-week pilot | 5-point Likert scale; bi-weekly check-in | To be established at pilot start |

# **5\. Core Features**

## **5.1  Feature Status Overview**

| Feature | Name | Status | Target Version |
| :---- | :---- | :---- | :---- |
| F1 | Role-based Dynamic Input Form | Implemented | V1.1 |
| F2 | Manager Intuition Capture (Feedback / Wellbeing / Observation) | Implemented | V1.1 |
| F3 | Unified GROW Coaching Output Engine | Implemented | V1.1 |
| F4 | Coaching Log Generator (STAR-based, FYI-aligned) | Implemented | V1.2 |
| F5 | Persistent Database Storage (coaching\_reports \+ coaching\_logs) | Implemented | V1.2 |

## **5.2  Feature Detail**

### **F1 — Role-based Dynamic Input Form**

The input form adapts dynamically based on the selected department and role. KPI fields are rendered only for metrics relevant to the selected profile, minimizing irrelevant input and cognitive overhead. This directly addresses Pain Point 1 by reducing the time cost of session preparation.

### **F2 — Manager Intuition Capture**

Three free-text fields capture qualitative context: (1) customer or team feedback, (2) team member wellbeing indicators, and (3) the manager's own observation or gut reading. This unstructured input is incorporated into the AI prompt to ensure the coaching output reflects observed reality, not only quantitative metrics.

### **F3 — Unified GROW Coaching Output Engine**

The engine dynamically selects from multiple coaching frameworks — FUEL, OSKAR, Radical Candor, STEPPA, and CLEAR — based on the input profile, then standardizes the output into a Co-Active GROW structure. Output is segmented into five labeled sections: SUMMARY, GOAL, REALITY, OPTIONS, WAY FORWARD, and DEFENSE.

Design constraint: the engine produces navigational prompts for the manager, not a dialogue script. The final formulation of any question or statement remains the manager's responsibility. This constraint is enforced in the system prompt and validated through pilot feedback.

### **F4 — Coaching Log Generator**

Following a coaching session, the manager inputs structured fields — team member name, session date, session type, situation and goal, observed behaviors, coaching suggestions, agreed actions, and follow-up date. The engine produces a STAR-formatted log in the manager's voice, with FYI competency language and role-level keywords embedded naturally and bolded.

Agreed actions and follow-up date are output in a separate section to enable use as a shared behavioral commitment between manager and team member. The log is designed to be copied directly into internal coaching tools (Internal App).

Tone learning is implemented via Option A (prompt injection of the manager's two most recent logs), enabling progressive stylistic calibration without additional infrastructure.

### **F5 — Persistent Database Storage**

SQLite stores both coaching reports (coaching\_reports table) and coaching logs (coaching\_logs table). Both tables are keyed on manager\_id and employee\_id, enabling historical retrieval and forming the basis for future follow-up reminders and tone learning. Auth is currently handled via a .env constant (MANAGER\_ID); a login layer using streamlit-authenticator is planned prior to any multi-user deployment.

# **6\. Milestones & Roadmap**

The roadmap is structured around Jason's parental leave and planned return to store in October 2026\. Each phase has defined exit criteria before the next begins.

| Phase | Period | Objective | Exit Criteria |
| :---- | :---- | :---- | :---- |
| Phase 1 — Two-Person Pilot | Now — September 2026 | Jason and Seul use the tool consistently; app quality reaches self-sustaining usability. | Both users report consistent usage; coaching log time under 10 min; at least 10 logs stored per user. |
| Phase 2 — Return & In-Store Integration | October 2026 (Return) | Jason uses the tool as active floor manager; cross-manager observation begins. | Jason completes 20+ coaching sessions logged via app; baseline vs. post-app KPI comparison available. |
| Phase 3 — Controlled Expansion | Q4 2026 — Q1 2027 | Recommend to 2–3 additional managers based on Phase 2 evidence. | At least 2 additional managers complete a 4-week trial; net positive self-efficacy score delta. |
| Phase 4 — Stakeholder Pitch | Q2 2027 | Secure internal sponsorship for native app conversion or engineering resource allocation. | PoC deck with quantified impact; at least one Director-level sponsor identified. |

# **7\. Feature Backlog**

Features below are defined but not yet implemented. Priority is relative to the two-person pilot phase. Complexity reflects estimated engineering effort given the current Streamlit \+ SQLite \+ Gemini stack.

| ID | Feature | Priority | Complexity | Target Version |
| :---- | :---- | :---- | :---- | :---- |
| F6 | Follow-up reminder banner (app launch shows due check-ins) | High | Low | V1.4 |
| F7 | Team member segmentation field (personality / resistance type) for question weighting | High | Medium | V1.4 |
| F8 | Manager self-efficacy check-in (5-point scale, bi-weekly) | Medium | Low | V1.4 |
| F9 | Tone profile auto-generation from accumulated logs (Option B) | Medium | Medium | V2.0 |
| F10 | In-session coaching checkpoint (real-time "is the team member engaging?" marker) | Medium | Medium | V2.0 |
| F11 | Post-session behavior change tracking (manager records observed delta) | High | Medium | V2.0 |
| F12 | Multi-user authentication layer (streamlit-authenticator) | High | Medium | Pre-Expansion |
| F13 | Vector DB-based semantic log search (ChromaDB or Pinecone) | Low | High | V3.0 |
| F14 | Internal App API integration for automated KPI population | Low | High | V3.0 |

# **8\. Technical Architecture**

## **8.1  Current Stack**

| Layer | Technology | Notes |
| :---- | :---- | :---- |
| UI Framework | Streamlit | Two-tab structure: coaching guide and coaching log |
| AI Engine | Google Gemini API (gemini-2.5-flash) | google-genai SDK; temperature configurable per function |
| Database | SQLite (via database.py) | coaching\_reports and coaching\_logs tables; keyed on manager\_id \+ employee\_id |
| Prompt Management | prompts.py | Version-controlled prompt dictionary; LATEST\_VERSION constant; GROW v1.0 and v1.1 |
| Package Management | uv \+ pyproject.toml | Environment reproducibility; dev dependencies include pytest |
| Version Control | Git / GitHub | Repository: github.com/jasonsuk/AI\_Coach\_Partner |
| Environment Config | .env (python-dotenv) | GEMINI\_API\_KEY and MANAGER\_ID; .gitignore enforced |

## **8.2  File Structure**

app.py                   — Orchestrator; sidebar config; tab routing

app\_tabs/                — Tab modules

  coaching\_guide\_tab.py  — F1, F2, F3 (coaching guide output)

  coaching\_log\_tab.py    — F4, F5 (coaching log input \+ history)

ai\_engine.py             — generate\_coaching\_report() \+ generate\_coaching\_log()

prompts.py               — COACHING\_PROMPTS dict \+ SYSTEM\_MESSAGES

database.py              — init\_db(), save\_log(), save\_report(), query functions

tests/test\_e2e.py        — E2E validation: import checks, DB CRUD, function signatures

docs/PRD.md              — Source of truth for this document (Markdown)

.env                     — API key \+ manager ID (not committed)

.gitignore               — Excludes \*.db, .env, \_\_pycache\_\_, backup files

## **8.3  Security Posture**

All API keys and personally identifiable information (manager ID) are stored in .env and excluded from version control. SQLite database files are gitignored. Prior to any multi-user deployment, a proper authentication layer (streamlit-authenticator) must be implemented and a PII masking review conducted for all Gemini API payloads.

# **9\. User Research**

## **9.1  Interview — Seul (March 19, 2026\)**

This was the first structured external user interview. Seul is a senior retail manager with a coaching cadence of approximately 40 Coach Connections per month. The interview followed a four-part guide covering: current coaching reality, friction points, team member passivity, and app concept response.

| Question Area | Response Summary | Implication |
| :---- | :---- | :---- |
| Coach Connection frequency | Targets 2 sessions/day across 20 working days (\~40/month) | Higher cadence than average; motivation is present but quality may be inconsistent |
| Preparation method | Reviews Internal App (team member system) \+ previous coaching notes; 3–4 minutes total | Prep is reactive and minimal; structured input would require almost no additional time cost |
| Biggest prep friction | Team member personality and mood; scheduling constraints (e.g., team member leaving within 15–20 minutes) | App output must be usable in compressed timeframes; conciseness of output is critical |
| Self-efficacy signal | Feels the session is going well mid-conversation — when the team member begins generating their own answers | Efficacy is experience-based, not preparation-based; app must support in-session awareness, not only prep |
| Most difficult team member type | Closed-off individuals; those who do not see the value of coaching; those with strong fixed beliefs | Defense bypass output (DEFENSE section) is critical feature; must be specific to personality type |
| Resistance response method | Previously: broaden perspective with organizational framing. Now: ask "why do you think you shouldn't do this?" — turning resistance into inquiry | Validates Co-Active inverse questioning approach embedded in the app design |
| App adoption intent | Would use selectively — specifically when uncertain about approach or question design. Not every session. | Validates positioning as a coaching support tool rather than a daily workflow dependency |
| Primary concern about the app | Generic or contextually irrelevant questions would cause abandonment. | Highest risk to adoption; team member segmentation input (F7) and prompt quality are the critical success factors |
| Unsolicited feedback | Post-session log summarization would be highly valuable; current log writing takes 15–20 min; expects app to reduce this to \~10 min with potential for further reduction through familiarity. | Confirms F4 (Coaching Log) as the highest-value feature for this user; log time is the primary KPI anchor |

## **9.2  Prompt Engineering Implications**

Three prompt improvement directions were identified from the Seul interview:

* P1 — Team member segmentation weighting: When the manager inputs a team member type (e.g., "resistant," "fixed-belief"), the DEFENSE section output should increase in specificity and the OPTIONS section should shift toward inverse inquiry patterns.

* P2 — Coaching session continuity: Integrate previous log data into the coaching guide prompt so that follow-up sessions reference prior agreed actions. This requires F4 and F3 to share session context.

* P3 — Output conciseness for time-compressed sessions: Add a "short session mode" flag (sub-15 minutes) that reduces GROW output to SUMMARY \+ top two OPTIONS \+ one WAY FORWARD commitment.

## **9.3  Research Limitations**

* Sample size: n=1. All qualitative findings are directional only. No statistical significance can be claimed.

* Self-report bias: Baseline metrics (prep time, log time) are self-reported and subject to recall error.

* Single domain: Seul operates in the same store context as the product owner. Generalizability to other store types, regions, or management cultures is unverified.

* Next step: A second interview with a Tech Support domain manager is planned for Phase 2 (post-return, October 2026\) to test cross-domain applicability.

# **10\. PRD Workflow & Version Control**

This document is maintained in two synchronized locations to serve different audiences.

| Location | Format | Purpose | Update Trigger |
| :---- | :---- | :---- | :---- |
| GitHub: docs/PRD.md | Markdown | Source of truth; co-located with code; tracked via git history | Any feature, KPI, or milestone change; committed alongside relevant code changes |
| Google Drive (shared) | DOCX (this file) | Stakeholder sharing; readable formatting; comment-friendly | Exported from Markdown after significant version increments (minor, major) |

## **10.1  Versioning Convention**

| Change Type | Version Increment | Example |
| :---- | :---- | :---- |
| Typo or minor correction | Patch: v1.3.x | v1.3.1 |
| Feature addition, KPI update, new research | Minor: v1.x | v1.4 |
| Full structural rewrite or product pivot | Major: vX.0 | v2.0 |

## **10.2  Recommended Commit Pattern**

When updating the PRD alongside code changes:

* Stage docs/PRD.md together with the relevant feature code files

* Use commit message format: docs: \[reason for change\] — e.g., docs: update KPI baseline from Seul interview

* Tag major version milestones: git tag v1.3