# Project Constitution (claude.md)

## Data Schemas
*(To be defined after Discovery Phase)*

## Behavioral Rules
*(To be defined after Discovery Phase)*

## Architectural Invariants

Invariant 1: All signal processing must use deterministic FFT windowing before inference.

Invariant 2: Models must undergo post-training quantization before being marked "Ready for Edge."

Invariant 3: Fault classifications must always include a confidence score.