---
title: "How We Benchmark Configurations"
---

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

# How We Benchmark Configurations

- When is agentic extraction worth it?
- Help me choose a mechanism for packet splitting.
- Does OCR make a difference?
- What's the spread between Opus and Haiku?
- Can I route review by confidence?
- How many tokens does a page use?

We answer these questions with benchmark datasets, one page per problem set:
[Digitization](digitization.md), [Splitting and Section Classification](splitting-and-classification.md),
[Key Information Extraction](extraction.md), [Confidence Assessment](confidence-assessment.md),
[Rule Validation](rule-validation.md) and [Token Use and Cost](token-use.md).

## How we run a benchmark

Each dataset has a configuration preset built for it. A benchmark starts from that preset,
changes one setting, and runs the same documents with each value of the setting. Each
benchmark has an ID, such as `EX-01`, and a results table. A table reads *Not yet
measured* until we run it.

| Dataset | Preset |
|---|---|
| Synthetic bank statements | `bank-statement-sample` |
| RealKIE-FCC-Verified, ConfBench | `realkie-fcc-verified` |
| OmniAI-OCR-Benchmark | `ocr-benchmark` |
| Fake-W2-Tax-Forms | `fake-w2` |
| DocSplit-Poly-Seq | `docsplit` |

Defaults differ from preset to preset. To configure your own stack, start from the
[preset](../../config_library/unified/README.md) closest to your documents.

## Why you can trust the results

- **Known answers.** Every dataset has ground truth, generated exactly for synthetic
  documents or checked by people for public ones. See
  [Benchmark Datasets](../idp-fundamentals/benchmark-datasets.md).
- **One change at a time,** on one stack, so the setting explains the difference.
- **Same documents, repeated.** We run every value on the same documents at least three
  times and report the spread.
- **Real differences only.** We name a winner only when the difference exceeds twice its
  standard error.
- **Pinned to a release.** Each table names the release, month and region, and the results
  file behind it.
- **Tokens, not prices.** Tokens stay the same when prices change. Multiply by current
  prices to estimate cost.
- **Repeatable in your account.** Most datasets come with every stack as Test Studio test
  sets.

## What the results don't cover

- **Your documents.** Confirm a choice on your own test set; see
  [Measure with ground truth](../idp-fundamentals/index.md#4-measure-with-ground-truth).
- **BDA mode.** These benchmarks cover Pipeline mode.
- **Datasets we haven't built yet:** long packets, same-class packets, packets with field
  ground truth, handwritten forms, and rule verdicts. Benchmarks that need one say so.

## Benchmarks for every problem set

<!-- BEGIN GENERATED ABLATIONS -->

### TR-01: How much do results vary between identical runs?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Nothing: the preset, run 10 times |
| **Everything else** | As each dataset's [preset](#how-we-run-a-benchmark) sets it |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 10 per document, per value |

| Dataset | Nothing: the preset, run 10 times | Weighted accuracy | Total tokens per page |
|---|---|---|---|
| RealKIE | Preset | — | — |

| Dataset | Nothing: the preset, run 10 times | Boundary accuracy | Total tokens per page |
|---|---|---|---|
| DocSplit | Preset | — | — |

| Dataset | Nothing: the preset, run 10 times | Completeness | Total tokens per page |
|---|---|---|---|
| Statement, 400 rows | Preset | — | — |


### TR-02: How long does a document take, and how many documents an hour?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Documents submitted at once |
| **Everything else** | As each dataset's [preset](#how-we-run-a-benchmark) sets it |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document, per value |

| Dataset | Documents submitted at once | Median seconds per document |
|---|---|---|
| RealKIE | 1 | — |
| RealKIE | 10 | — |
| RealKIE | 50 | — |

| Dataset | Documents submitted at once | Median seconds per document |
|---|---|---|
| Statement, 400 rows | 1 | — |
| Statement, 400 rows | 10 | — |
| Statement, 400 rows | 50 | — |

<!-- END GENERATED ABLATIONS -->
