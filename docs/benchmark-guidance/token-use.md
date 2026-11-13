---
title: "Token Use and Cost"
---

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

# Token Use and Cost

- Where do the tokens go?
- How much does prompt caching save?
- What do page images cost in tokens?
- What is the cheapest configuration that keeps accuracy?

We report tokens, not prices, because tokens stay the same when prices change. To estimate
cost, multiply each step's tokens by the current price of its model. Some benchmarks here
reuse runs from other pages.

**Metrics**

- *Tokens per page:* input, output and prompt cache reads and writes, per step.
- *Share of input from cache:* Amazon Bedrock bills cache reads at a reduced rate.
- *Accuracy:* where a benchmark trades tokens against it.

## Benchmarks

<!-- BEGIN GENERATED ABLATIONS -->

### TU-01: Where do the tokens go?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Nothing: the preset, measured step by step |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document, per value |

| Dataset | Nothing: the preset, measured step by step | OCR tokens per page | Classification tokens per page | Extraction tokens per page | Scoring tokens per page | Total tokens per page | Share of input served from cache |
|---|---|---|---|---|---|---|---|
| RealKIE | Preset | — | — | — | — | — | — |

| Dataset | Nothing: the preset, measured step by step | OCR tokens per page | Classification tokens per page | Total tokens per page | Share of input served from cache |
|---|---|---|---|---|---|
| DocSplit | Preset | — | — | — | — |

| Dataset | Nothing: the preset, measured step by step | OCR tokens per page | Classification tokens per page | Extraction tokens per page | Scoring tokens per page | Total tokens per page | Share of input served from cache |
|---|---|---|---|---|---|---|---|
| Statement, 400 rows | Preset | — | — | — | — | — | — |


### TU-02: How much does prompt caching save in extraction?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | `extraction.prompt_cache` |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document, per value |

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

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Page images |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq) |
| **Runs** | 3 per document, per value |

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

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Configuration |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document, per value |

| Dataset | Configuration | Weighted accuracy | Total tokens per page |
|---|---|---|---|
| RealKIE | Preset | — | — |
| RealKIE | Holistic classification, text only | — | — |
| RealKIE | Textract layout only | — | — |
| RealKIE | Confidence off | — | — |
| RealKIE | All three together | — | — |

| Dataset | Configuration | Boundary accuracy | Total tokens per page |
|---|---|---|---|
| DocSplit | Preset | — | — |
| DocSplit | Holistic classification, text only | — | — |
| DocSplit | Textract layout only | — | — |
| DocSplit | Confidence off | — | — |
| DocSplit | All three together | — | — |

| Dataset | Configuration | Completeness | Total tokens per page |
|---|---|---|---|
| Statement, 400 rows | Preset | — | — |
| Statement, 400 rows | Holistic classification, text only | — | — |
| Statement, 400 rows | Textract layout only | — | — |
| Statement, 400 rows | Confidence off | — | — |
| Statement, 400 rows | All three together | — | — |


### TU-05: How many tokens does each extraction model use for the same document?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Extraction model |
| **Everything else** | Computed from the EX-02 runs; the rest as each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | None: computed from the EX-02 runs |

| Dataset | Extraction model | Extraction tokens per page | Total tokens per page |
|---|---|---|---|
| RealKIE | The models in EX-02 | — | — |

| Dataset | Extraction model | Extraction tokens per page | Total tokens per page |
|---|---|---|---|
| Statement, 400 rows | The models in EX-02 | — | — |

<!-- END GENERATED ABLATIONS -->
