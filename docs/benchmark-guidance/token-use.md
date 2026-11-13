---
title: "Token Use and Cost"
---

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

# Token Use and Cost

These ablations answer how many tokens each step of the pipeline uses, what drives the
count, and which configurations use fewer tokens without losing accuracy. The tables report
tokens rather than prices, because tokens do not change when prices do. To estimate cost,
multiply each step's tokens by the current price of the model that step uses.

**Metrics on this page:** tokens per page for each step, counting input, output and prompt
cache reads and writes together; the *share of input served from cache*, which Amazon
Bedrock bills at a reduced rate; and accuracy where an ablation trades tokens against it.

Some ablations here reuse runs from other pages and need no new runs. Every ablation holds
everything except the setting it changes at the
[baseline](index.md#the-baseline-every-ablation-starts-from).

<!-- BEGIN GENERATED ABLATIONS -->

### TU-01: Where do the tokens go?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | Nothing: the baseline, measured step by step |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document per value |

| Dataset | Nothing: the baseline, measured step by step | OCR tokens per page | Classification tokens per page | Extraction tokens per page | Scoring tokens per page | Total tokens per page | Share of input served from cache |
|---|---|---|---|---|---|---|---|
| RealKIE | Baseline | — | — | — | — | — | — |

| Dataset | Nothing: the baseline, measured step by step | OCR tokens per page | Classification tokens per page | Total tokens per page | Share of input served from cache |
|---|---|---|---|---|---|
| DocSplit | Baseline | — | — | — | — |

| Dataset | Nothing: the baseline, measured step by step | OCR tokens per page | Classification tokens per page | Extraction tokens per page | Scoring tokens per page | Total tokens per page | Share of input served from cache |
|---|---|---|---|---|---|---|---|
| Statement, 400 rows | Baseline | — | — | — | — | — | — |


### TU-02: How much does prompt caching save in extraction?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | `extraction.prompt_cache` |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document per value |

| Dataset | `extraction.prompt_cache` | Total tokens per page | Share of input served from cache | Median seconds per document |
|---|---|---|---|---|
| RealKIE | auto (default) | — | — | — |
| RealKIE | off | — | — | — |

| Dataset | `extraction.prompt_cache` | Total tokens per page | Share of input served from cache | Median seconds per document |
|---|---|---|---|---|
| DocSplit | auto (default) | — | — | — |
| DocSplit | off | — | — | — |

| Dataset | `extraction.prompt_cache` | Total tokens per page | Share of input served from cache | Median seconds per document |
|---|---|---|---|---|
| Statement, 400 rows | auto (default) | — | — | — |
| Statement, 400 rows | off | — | — | — |


### TU-03: What do page images cost in tokens, step by step?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | Page images |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq) |
| **Runs** | 3 per document per value |

| Dataset | Page images | Classification tokens per page | Extraction tokens per page | Scoring tokens per page | Total tokens per page |
|---|---|---|---|---|---|
| RealKIE | In every step (default) | — | — | — | — |
| RealKIE | Off in classification | — | — | — | — |
| RealKIE | Off in extraction | — | — | — | — |
| RealKIE | Off in scoring | — | — | — | — |

| Dataset | Page images | Classification tokens per page | Total tokens per page |
|---|---|---|---|
| DocSplit | In every step (default) | — | — |
| DocSplit | Off in classification | — | — |
| DocSplit | Off in extraction | — | — |
| DocSplit | Off in scoring | — | — |


### TU-04: What is the cheapest configuration that keeps accuracy?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | Configuration |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document per value |

| Dataset | Configuration | Weighted accuracy | Total tokens per page |
|---|---|---|---|
| RealKIE | Baseline | — | — |
| RealKIE | Holistic classification, text only | — | — |
| RealKIE | Textract layout only | — | — |
| RealKIE | Confidence off | — | — |
| RealKIE | All three together | — | — |

| Dataset | Configuration | Boundary accuracy | Total tokens per page |
|---|---|---|---|
| DocSplit | Baseline | — | — |
| DocSplit | Holistic classification, text only | — | — |
| DocSplit | Textract layout only | — | — |
| DocSplit | Confidence off | — | — |
| DocSplit | All three together | — | — |

| Dataset | Configuration | Completeness | Total tokens per page |
|---|---|---|---|
| Statement, 400 rows | Baseline | — | — |
| Statement, 400 rows | Holistic classification, text only | — | — |
| Statement, 400 rows | Textract layout only | — | — |
| Statement, 400 rows | Confidence off | — | — |
| Statement, 400 rows | All three together | — | — |


### TU-05: How many tokens does each extraction model use for the same document?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | Extraction model |
| **Held fixed** | Computed from the EX-02 runs; everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | No new runs: computed from the EX-02 runs |

| Dataset | Extraction model | Extraction tokens per page | Total tokens per page |
|---|---|---|---|
| RealKIE | The models in EX-02 | — | — |

| Dataset | Extraction model | Extraction tokens per page | Total tokens per page |
|---|---|---|---|
| Statement, 400 rows | The models in EX-02 | — | — |

<!-- END GENERATED ABLATIONS -->
