# HNIR-CCP Governance

This document outlines the governance model for the HNIR-CCP project.

## Current Governance Model

The HNIR-CCP project is currently governed under a **Benevolent Dictator for Life (BDFL)** model.

*   **BDFL:** Aravind Ravi
*   **Research Profile:** https://www.raviaravind.com
*   **Lab Affiliation:** Teknamin Labs (https://www.teknamin.com)

The BDFL is responsible for the strategic direction of the project and has the final say in all decisions, including technical direction, feature prioritization, and community management.

## Future Vision

As the project and community grow, the governance model may evolve. The long-term goal is to transition to a more community-driven model, potentially with a technical steering committee composed of core contributors. Any changes to the governance model will be made transparently and in consultation with the community.

## Rule and Policy Approval Workflow

Changes to the core rule and policy engine of the CCP are subject to a strict review process:

1.  All changes must be submitted as a pull request.
2.  All pull requests that modify rules or policies must be reviewed and approved by at least one core contributor (initially, the BDFL).
3.  The pull request must include updates to the evaluation harness to demonstrate that the change does not introduce regressions.
4.  The pull request must pass all continuous integration (CI) checks.
