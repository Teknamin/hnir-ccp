# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HNIR-CCP (Conversation Control Plane) is a deterministic safety middleware for LLM agents. It sits between a user/orchestrator and an LLM, intercepting control commands, gating proposed actions against policy rules, and governing conversation state via a finite state machine. The key insight: safety-critical decisions (cancel, undo, policy enforcement) must not depend on prompt-interpretable LLM output.

This is NOT an intent router. There is no "matching" or "routing" module. The CCP intercepts, gates, and governs.

## Commands

### Install
```bash
pip install -e ".[dev]"
```

### Run tests
```bash
pytest
```

### Lint
```bash
ruff check ccp/
```

### CI linting (docs)
```bash
markdownlint '**/*.md'
yamllint .
```

## Architecture

The `ccp/` package has five modules forming the control plane pipeline:

1. **control/** — Control command handler. Recognizes deterministic control signals (help, cancel, undo, reset, status) via keyword/shortcut matching. No LLM involved.

2. **policy/** — Policy enforcement engine. Classifies LLM-proposed actions and evaluates them against YAML-defined policy rules. Returns ALLOW, DENY, or CONFIRM decisions. Includes role/permission authorization checks.

3. **state/** — Conversation state machine. Defines states (idle, active, awaiting_confirmation, suspended, terminated) and valid transitions. Validates preconditions before transitions. Manages session state storage.

4. **audit/** — Deterministic observability. Structured decision logging with reason codes. Assembles full request traces for every CCP decision.

5. **integration/** — LLM integration layer. Pre-execution interception of LLM-proposed actions. Safe-mode fallback handler when the LLM is unavailable or untrusted.

### Configuration

Policy rules will be defined in YAML (not yet implemented). The control plane is config-driven: policy changes require config updates, not code changes.

## Key Design Decisions

- **Deterministic-first**: All safety-critical decisions are rule-based, not LLM-based
- **Not prompt-injectable**: Control plane logic cannot be influenced by prompt injection
- **Intercept, don't classify**: The CCP intercepts control commands and gates actions — it does not classify user intent
- **Config-driven policy**: Policy rules live in YAML, enforceable without code changes
- **Python 3.9+ / Pydantic v2**: Core stack

## Module Status

Currently at Phase 1 (skeleton). All modules contain only docstrings and `__init__.py` files. Phase 2 will implement the v0 demo.
