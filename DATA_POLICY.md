# Data Policy

This document describes the data handling policies for the HNIR-CCP project.

## Core Principle: No Private Data

The HNIR-CCP project is designed to be demonstrated, evaluated, and developed **without the use of any private or personally identifiable information (PII)**.

## Datasets

All datasets used for evaluation and testing are either synthetically generated or are derived from public data sources that contain no PII. The provenance of all datasets will be clearly documented in the `eval/` directory.

## Logging

The reference implementation of the CCP includes logging capabilities for observability and evaluation. The default logging configuration is designed to capture only the information necessary to evaluate the performance of the control plane, such as timestamps, rule hits/misses, and latency. It does not log the full content of user conversations unless explicitly configured to do so for development purposes.

It is the responsibility of the downstream user of this library to ensure that their use of logging complies with all applicable privacy regulations.
