# Candidate Competency and Engineering Fit Architecture

**Status:** Accepted architectural requirement  
**Assessment priority:** Balanced  
**Scope:** Candidate suitability for software-engineering opportunities  
**Boundary:** Separate from job legitimacy and opportunity qualification

## 1. Decision

The system will use a balanced candidate competency model. It will assess technical capability, practical engineering discipline, and professional engineering behaviours together. It will also show growth potential and evidence gaps separately rather than allowing a single score to hide them.

The model answers a different question from job qualification:

- **Opportunity qualification:** Is this posting legitimate and within the search policy?
- **Candidate suitability:** Does the applicant have evidence of the capabilities and working practices the role requires?

A job must pass opportunity qualification regardless of candidate fit. A candidate must not be marked unsuitable merely because the system has not yet collected evidence.

## 2. Placement in the existing milestone sequence

The seven milestones remain unchanged and in their approved order:

1. Policy and validation integrity.
2. Persistence integrity — PostgreSQL.
3. Workflow integrity — Temporal.
4. Discovery integrity — approved source adapters, discovery and normalization.
5. Application preparation.
6. Controlled browser execution — Playwright.
7. Operations and observability.

This document records the architecture now; it does **not** add candidate-fit work to the active Milestone 1 repair sequence.

Implementation boundaries:

- **Now / Milestone 1:** Finish the existing policy, contracts, deterministic validators, source enforcement, evidence, stop-condition and test repairs. Candidate fit must not alter or delay these repairs.
- **Milestone 2:** Include the future candidate profile, competency evidence and assessment records in the persistence design. Do not store sensitive applicant data that is not necessary.
- **After Milestone 1 is accepted:** Implement and test the competency taxonomy, profile and evidence contracts as a separate bounded subsystem. Keep job qualification independent.
- **Milestone 5:** Extract role requirements, compare them with the candidate profile, produce a fit assessment and prepare an application package only when the relevant human review gates are satisfied.
- **Milestones 6–7:** Browser execution and operational monitoring may consume approved application packages and assessment records, but must not reinterpret candidate capability or bypass approval.

## 3. Balanced competency model

The model has three equally important assessment dimensions. Their relative importance may be adjusted by explicit role requirements, but no universal weighted score should silently override a critical requirement.

### A. Technical capability

Assess role-relevant knowledge and demonstrated ability, including:

- Programming languages and core programming concepts.
- Data structures, algorithms, debugging and problem decomposition.
- APIs, databases, data modelling and integration.
- Software design, architecture, modularity and maintainability.
- Testing strategy, test quality and defect diagnosis.
- Relevant platforms, cloud, Linux, containers, deployment and operations.
- Security, privacy, authentication, authorization and responsible data handling.

The taxonomy must be role-aware. A junior frontend role should not be judged against the same technical checklist as a senior platform/SRE role.

### B. Engineering practice

Assess how the candidate produces dependable software:

- Version control, meaningful commits and pull-request practice.
- Readable, maintainable code and appropriate abstractions.
- Automated tests and verification before changes are considered complete.
- Code review, constructive feedback and response to review findings.
- Technical documentation, specifications and decision records.
- Debugging discipline, reproducibility and root-cause analysis.
- CI/CD, deployment safety, observability and operational readiness where relevant.
- Security-conscious handling of secrets, dependencies and user data.

### C. Professional engineering behaviours

Assess observable work behaviours, not personality or demographic proxies:

- **Problem solving:** decomposes unclear problems, tests assumptions and explains reasoning.
- **Ownership:** follows work through, communicates blockers and verifies outcomes.
- **Communication:** explains technical decisions, uncertainty, risks and progress clearly.
- **Collaboration:** works constructively through reviews, hand-offs and disagreement.
- **Reliability:** makes realistic commitments, surfaces delays and closes feedback loops.
- **Adaptability:** learns unfamiliar tools and changes approach when evidence warrants it.
- **Judgement and ethics:** considers security, privacy, accessibility, user impact and operational risk.
- **Learning discipline:** identifies gaps, seeks feedback and demonstrates improvement.

These behaviours must be inferred only from relevant evidence in engineering work or structured, human-reviewed examples. The system must not infer them from writing style alone, social-media activity, age, nationality, education prestige, employment gaps or other weak proxies.

## 4. Evidence model

Every competency assessment must be traceable to evidence. Evidence records should support:

- Evidence type: project, code sample, repository, pull request, test suite, design document, incident/postmortem, work example, structured interview response, certification or other declared source.
- Source reference and captured date.
- Candidate-provided, independently verified, or system-extracted provenance.
- Competency and role requirement supported.
- Short factual observation; avoid unsupported character judgements.
- Verification state and reviewer, where applicable.
- Recency and context, including whether the work was individual or collaborative.
- Limitations, missing context and confidence.

Evidence status for each competency:

- **Demonstrated:** credible evidence directly supports the competency.
- **Partial:** evidence supports some, but not all, of the required level or scope.
- **Claimed:** candidate states the capability, but supporting evidence has not been verified.
- **Unknown:** insufficient evidence to assess.
- **Not met:** credible evidence indicates the stated requirement is not currently met.

Unknown is not equivalent to Not met. A claim is not automatically demonstrated. A project or code sample must be interpreted in context; repository presence alone does not prove authorship, quality or professional behaviour.

## 5. Role requirement extraction and matching

For each qualified job:

1. Extract stated technical skills, engineering practices, professional expectations, seniority and experience requirements.
2. Preserve the original posting text and source reference for each extracted requirement.
3. Classify each requirement as mandatory, preferred or contextual; mark ambiguous extraction for review.
4. Map requirements to the competency taxonomy without inventing requirements that the posting does not state.
5. Compare each requirement with candidate evidence and assign an evidence status.
6. Produce an explainable assessment showing matched evidence, partial matches, unknowns, unmet mandatory requirements and conflicts.
7. Route ambiguous or high-impact judgements to human review.

LLMs may assist with extraction and summarisation, but cannot independently verify evidence, convert a claim into demonstrated ability, or override deterministic policy and human review.

## 6. Assessment output

A future FitAssessment should contain:

- Job identifier and policy/taxonomy versions.
- Role requirements and their mandatory/preferred classification.
- Requirement-to-competency mappings.
- Evidence references and status for each mapped requirement.
- Technical capability, engineering practice and professional behaviour summaries.
- Material strengths, gaps, unknowns and conflicting evidence.
- Seniority/experience alignment and rationale.
- Growth potential as a separate, explicitly qualified observation.
- Review flags, confidence limitations and human-review outcome.

The system may provide a transparent summary such as **Strong evidence**, **Partial alignment**, or **Insufficient evidence**. If a numerical score is later justified, publish its dimensions, weights, missing-data treatment and limitations. Never let an aggregate score conceal a failed mandatory requirement or override a hard job-policy rejection.

## 7. Candidate profile and privacy

The candidate profile is an explicit, editable record of skills, experience, projects, work preferences and evidence references. The applicant must be able to correct extracted facts and distinguish declared claims from verified evidence.

Collect only information needed for role matching and application preparation. Do not infer or store sensitive personal attributes for candidate ranking. Work-authorisation, location and other eligibility facts must be explicitly supplied and governed by separate policy; do not assume them from inferred location or education history.

No evidence source should be accessed, uploaded or disclosed to an employer without the applicant's knowledge and appropriate approval.

## 8. Learning and improvement loop

The system may turn recurring, role-relevant gaps into a development plan:

1. Identify the market requirement and its source.
2. Show the current evidence and exact gap.
3. Propose a bounded learning task or engineering project.
4. Define verification criteria (tests, review, deployed result, design explanation or other observable artefact).
5. Add the resulting evidence to the candidate profile only after the candidate confirms it.
6. Reassess affected competencies and retain the assessment history.

This is a learning aid, not an automatic credential or guarantee of employability.

## 9. Proposed bounded components

Names are architectural proposals, not a mandate to create all modules immediately:

- EngineeringCompetencyTaxonomy — versioned competency definitions and role mappings.
- CandidateProfile — candidate-declared skills, experience and preferences.
- EvidenceRecord — provenance-backed evidence with verification and context.
- RoleRequirement — extracted job requirement with source text and classification.
- RequirementExtractor — assisted extraction with review flags.
- CandidateFitValidator — deterministic mapping and evidence-status rules.
- FitAssessment — explainable, versioned output.
- SkillGapAnalyzer — optional learning-plan recommendations based on identified gaps.

Keep these separate from JobRecord, opportunity validators and the job qualification decision. Candidate fit must never turn an invalid job into a valid one.

## 10. Acceptance criteria before candidate-fit use

- Taxonomy is versioned, role-aware and balanced across the three dimensions.
- Every assessment claim links to evidence or is explicitly marked claimed/unknown.
- Missing evidence is not treated as proof of inability.
- Mandatory and preferred requirements remain distinct.
- Extracted requirements retain source traceability and can be corrected.
- The same profile, evidence, taxonomy and role requirements produce the same deterministic mapping/status output.
- Human review is required for ambiguous extraction and subjective professional-behaviour conclusions.
- Privacy, consent, correction and data-minimisation controls are defined.
- Tests cover positive, negative, partial, unknown, conflicting and stale evidence.
- Candidate suitability remains independent of opportunity qualification and application authorisation.
