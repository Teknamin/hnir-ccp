> **Status: v1.0 — Research milestone reached.**
> This repository is a completed research artifact and the reference implementation evaluated in the HNIR-CCP study.

# HNIR-CCP: A Deterministic Control Plane for AI Agent Systems

HNIR-CCP separates deterministic policy enforcement from probabilistic reasoning in AI agent systems.

The model reasons. The control plane governs.

## Research Context

This repository is part of a broader research arc:

1. **[HNIR v1 — Theory](https://doi.org/10.5281/zenodo.18110920):** Introduced the architecture and design principles for deterministic intent routing in conversational systems.
2. **HNIR-CCP — Implementation (this repo):** A practical, deterministic control plane that enforces policy, handles control commands, and blocks invalid transitions before they reach an LLM.
3. **[HNIR-CCP v2 — Empirical Evidence](https://doi.org/10.5281/zenodo.19324744):** Presents a comparative evaluation of this implementation against frontier LLMs (GPT-4o, o3, Claude Sonnet, Claude Opus, Gemini 2.5 Pro) and guardrail frameworks (NeMo Guardrails, Guardrails AI) across 100 structured governance scenarios.

## Thesis

Not all agent inputs require LLM inference. Some represent procedural commands, policy-bound operations, or state transitions that can be evaluated deterministically. HNIR-CCP formalizes this separation across three layers:

1. **Control** — Deterministic detection and execution of commands and state transitions.
2. **Policy Enforcement** — Authorization, compliance validation, and safety constraints.
3. **Reasoning** — Open-ended understanding delegated to LLMs only when required.

## Architecture

```
Agent Input → Control Plane → Policy + Safety Check
                ├── Deterministic Action (no LLM needed)
                ├── Clarification (ambiguous input)
                └── Passthrough to LLM (reasoning required)
```

LLM reasoning cannot bypass deterministic policy or control decisions.

## Safety Invariants

1. Destructive or irreversible actions require explicit confirmation.
2. Policy-bound operations must pass all authorization steps.
3. State transitions are deterministic and auditable.
4. LLM reasoning cannot bypass control-plane decisions.
5. Ambiguous commands trigger structured clarification, not execution.

## Evaluation Results

Evaluated on 100 scenarios spanning control commands, policy-gated actions, state transitions, and adversarial probes.

| Metric | Result |
|--------|--------|
| Policy compliance | 100% |
| Adversarial injection deny rate | 100% |
| Reliability failures | 0 |
| P50 latency | ~24µs |
| P99 latency | ~34µs |
| LLM calls for control decisions | 0 |

Evaluation artifacts are deterministic and reproducible. See the [Evaluation Dataset](#evaluation-dataset) section below.

For the full comparative analysis against LLMs and guardrail frameworks, see the [v2 preprint](https://doi.org/10.5281/zenodo.19324744).

## Relationship to Existing Approaches

HNIR-CCP complements LLM orchestration and guardrail systems:

- **vs. Prompt routing / agent chaining**: These sequence reasoning tasks. HNIR-CCP provides a deterministic enforcement layer that precedes reasoning.
- **vs. Tool invocation frameworks**: These teach LLMs how to call functions. HNIR-CCP decides whether an action is permitted before it is executed.
- **vs. Runtime guardrails**: These filter LLM outputs. HNIR-CCP enforces policy before the LLM is invoked.

Analogous to admission controllers in Kubernetes or policy engines in zero-trust architectures.

## Project Structure

```
ccp/    — Core control plane implementation
config/ — Policy and command registry configuration
tests/  — Test suite
docs/adr/ — Architecture Decision Records
```

## Evaluation Dataset

This repository does not include the evaluation dataset used in the accompanying study. The evaluation harness is maintained in a separate, private project.

The dataset consists of structured governance scenarios covering:

- Control commands and baseline behaviors
- Safety triggers and adversarial inputs
- Policy enforcement cases (RBAC, state machine, confirmation rules)

The dataset is withheld to preserve research integrity and intellectual property. A subset or full release may be provided in future work. For research collaboration inquiries, contact the author.

## Limitations

- Evaluated on synthetic scenarios, not production traffic.
- The v2 study evaluates the deterministic layer in isolation — no hybrid CCP + LLM evaluation.
- Domain-specific applicability (healthcare, finance, etc.) has not been validated.

## Author

**Aravind Ravi** — Independent Researcher

- Lab: [Teknamin Labs](https://www.teknamin.com)
- Site: [raviaravind.com](https://www.raviaravind.com)

## Development Methodology

This project uses AI-assisted development tooling (Claude Code) for implementation. All architectural decisions, experimental design, and research claims are the author's own.

## Citation

If you use this work, please cite both the implementation and the relevant preprint(s):

### Preprint (v2 — Empirical Evaluation)

> Ravi, A. (2026). HNIR-CCP: Empirical Evaluation of Deterministic Control Planes for AI Agent Governance. Zenodo. https://doi.org/10.5281/zenodo.19324744

### Preprint (v1 — Architecture)

> Ravi, A. (2025). HNIR: A Deterministic Intent Routing Control Plane for Distributed Conversational Systems. Zenodo. https://doi.org/10.5281/zenodo.18110920

### Implementation

> Ravi, A. (2026). HNIR-CCP: A Deterministic Control Plane for AI Agent Systems [Software]. GitHub. https://github.com/Teknamin/hnir-ccp

## License

Apache License 2.0. See [LICENSE](LICENSE).
