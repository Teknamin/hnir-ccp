> **Status: v1.0 — Research milestone reached.**
> This repository is a completed research artifact and the deterministic baseline evaluated in the HNIR-CCP study.

# HNIR-CCP: A Deterministic Control Plane for AI Agent Systems

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19324744.svg)](https://doi.org/10.5281/zenodo.19324744)

HNIR-CCP is a **pre-inference governance system** for AI agent systems. It separates deterministic policy enforcement from probabilistic reasoning — the model reasons, the control plane governs. Certain operations — control commands, policy enforcement, state transitions — require correctness guarantees that probabilistic models cannot reliably provide.

This repository provides the deterministic baseline evaluated in the [HNIR-CCP empirical study](https://doi.org/10.5281/zenodo.19324744). It is **not** a prompt wrapper, a guardrails layer, or a post-hoc filter. Control logic runs before the LLM is ever invoked. This repository is not intended to reproduce the full evaluation results; the empirical study is described in the accompanying preprint.

## Quickstart

```bash
pip install -e .
python -m ccp           # 12-step scripted demo (deterministic, no API keys)
python -m ccp -i        # interactive REPL with mock LLM
```

The scripted demo walks through control commands, policy enforcement, state transitions, adversarial blocking, and audit logging using a mock LLM backend. No external dependencies or API keys are required.

The demo uses a healthcare workflow (intake, triage, recommendation, confirmation, execution) as a simplified illustrative workflow. HNIR-CCP is domain-agnostic; the state machine and policies are defined in YAML configuration.

## Research Context

This repository is part of a broader research arc:

1. **[HNIR v1 — Theory](https://doi.org/10.5281/zenodo.18110920):** Architecture and design principles for deterministic intent routing in conversational systems (2025).
2. **HNIR-CCP — Implementation (this repo):** A practical deterministic control plane that enforces policy, handles control commands, and blocks invalid state transitions before they reach an LLM.
3. **[HNIR-CCP v2 — Empirical Evidence](https://doi.org/10.5281/zenodo.19324744):** Comparative evaluation against frontier LLMs (GPT-4o, o3, Claude Sonnet, Claude Opus, Gemini 2.5 Pro) and guardrail frameworks (NeMo Guardrails, Guardrails AI) across 100 structured governance scenarios (2026).
4. **Blog post:** [HNIR-CCP vs LLMs](https://www.teknamin.com/blog/hnir-ccp-vs-llms/)

> **Note:** The evaluation harness, scoring logic, and scenario dataset are maintained separately and are not included in this repository. See the [v2 preprint](https://doi.org/10.5281/zenodo.19324744) for methodology and results.

## Contributions

This work makes three contributions:

1. It identifies a class of governance tasks where probabilistic LLM inference is insufficient even under deterministic decoding (temperature=0).
2. It provides a structured empirical evaluation comparing LLM-based governance with a deterministic control-plane approach across multiple frontier models.
3. It demonstrates that separating governance from reasoning yields strict correctness guarantees with significantly lower latency and cost.

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

The `ccp/` package implements the control plane as five modules:

| Module | Responsibility |
|--------|---------------|
| `control/` | Deterministic command handler — recognizes control signals (help, cancel, undo, reset, status) via keyword matching. No LLM involved. |
| `policy/` | Policy enforcement engine — evaluates LLM-proposed actions against YAML-defined rules. Returns ALLOW, DENY, or REQUIRE_CONFIRMATION. |
| `state/` | Conversation state machine — validates transitions and action-type permissions per state. |
| `audit/` | Structured decision logging with reason codes and full request traces. |
| `integration/` | LLM adapter layer — pre-execution interception of LLM-proposed actions. Mock, OpenAI, and Anthropic backends. |

All policy rules and state definitions are in `config/` as YAML. The control plane is configuration-driven.

## Safety Invariants

1. Destructive or irreversible actions require explicit confirmation.
2. Policy-bound operations must pass all authorization steps.
3. State transitions are deterministic and auditable.
4. LLM reasoning cannot bypass control-plane decisions.
5. Ambiguous commands trigger structured clarification, not execution.

## Evaluation Results

The following results are reported in the [v2 preprint](https://doi.org/10.5281/zenodo.19324744), evaluated using a separate, private harness. They are included here for reference; the evaluation code is not part of this repository.

The evaluation includes 100 scenarios spanning four categories: control commands, policy enforcement, state transitions, and adversarial probes. The focus is on coverage of governance patterns rather than dataset scale. All LLM evaluations were conducted with temperature set to 0 to eliminate sampling variability and isolate model behavior under deterministic decoding.

| Metric | Result |
|--------|--------|
| Policy compliance | 100% |
| Adversarial injection deny rate | 100% |
| Reliability failures | 0 |
| P50 latency | ~24µs |
| P99 latency | ~34µs |
| LLM calls for control decisions | 0 |

Latency reflects deterministic in-process evaluation without network calls, compared to remote inference for LLM-based systems.

While a deterministic system achieving 100% compliance on structured tasks is expected, the key result is that LLM-based approaches fail to match this even under identical conditions. The best-performing model (Claude Opus) achieves 91% compliance. The comparison highlights that governance tasks — unlike reasoning tasks — require strict correctness guarantees that probabilistic systems cannot reliably provide.

For the full comparative analysis against LLMs and guardrail frameworks, see the [v2 preprint](https://doi.org/10.5281/zenodo.19324744).

## Relationship to Existing Approaches

HNIR-CCP complements LLM orchestration and guardrail systems:

- **vs. Prompt routing / agent chaining**: These sequence reasoning tasks. HNIR-CCP provides a deterministic enforcement layer that precedes reasoning.
- **vs. Tool invocation frameworks**: These teach LLMs how to call functions. HNIR-CCP decides whether an action is permitted before it is executed.
- **vs. Runtime guardrails**: These filter LLM outputs. HNIR-CCP enforces policy before the LLM is invoked.

Analogous to admission controllers in Kubernetes or policy engines in zero-trust architectures.

## Project Structure

```
ccp/      — Core control plane implementation
config/   — Policy and command registry configuration (YAML)
tests/    — Test suite
docs/adr/ — Architecture Decision Records
```

## Evaluation Dataset and Reproducibility

The evaluation harness and scenario dataset are not publicly released at this time. The evaluation methodology, scenario categories, and scoring definitions are fully described in the [v2 preprint](https://doi.org/10.5281/zenodo.19324744).

This work is positioned as a systems study rather than a benchmark contribution. The goal is to characterize failure modes under controlled conditions rather than provide a standardized dataset.

The dataset consists of structured governance scenarios covering:

- Control commands and baseline behaviors
- Safety triggers and adversarial inputs
- Policy enforcement cases (RBAC, state machine, confirmation rules)

A subset or full release may be provided in future work. For research collaboration inquiries, contact the author.

## Limitations

This evaluation focuses on structured governance scenarios where the expected action is unambiguous. The goal is to isolate the governance problem from upstream interpretation tasks. We do not claim that these results directly generalize to open-ended natural language inputs. Instead, they demonstrate that even under idealized conditions (temperature=0, explicit policy prompts), LLM-based approaches fail to achieve full compliance in deterministic governance tasks.

Additional limitations:

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
