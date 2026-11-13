---
title: "Token Use and Cost"
tableOfContents:
  maxHeadingLevel: 3
---

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

# Token Use and Cost

Every step after digitization sends tokens to a model, and tokens are what you pay for. We
report tokens, not prices, because tokens stay the same when prices change. To estimate cost,
multiply each step's tokens by the current price of its model.

## How to use fewer tokens on your documents

**Your definitions.** The accelerator sends your field descriptions and few-shot examples
with every request, so they add tokens to every section. Prompt caching reads a repeated
prompt prefix at a reduced rate.

**Data quality.** Page images cost tokens in every step that reads them, and long files cost
more in every step.

**Settings.**

| Setting | What it changes | Questions |
|---|---|---|
| Models | Each step's model sets its price and how many tokens it writes | [TU-05](#how-many-tokens-does-each-extraction-model-use-for-the-same-document) |
| Prompt caching | Reads a repeated prompt prefix at a reduced rate | [TU-02](#how-much-does-prompt-caching-save-in-extraction) |
| Page images | Adds image tokens to each step that reads them | [TU-03](#what-do-page-images-cost-in-tokens-step-by-step) |
| All of the above | The cheapest configuration that keeps accuracy | [TU-04](#what-is-the-cheapest-configuration-that-keeps-accuracy) |

Some benchmarks here reuse runs from other pages.

## Benchmark datasets and metrics

<!-- BEGIN GENERATED DATASETS -->

| Dataset | Preset |
|---|---|
| [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) | `bank-statement-sample` |
| [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified) | `realkie-fcc-verified` |
| [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq) | `docsplit` |

<!-- END GENERATED DATASETS -->

**Metrics**

- *Tokens per page:* input, output and prompt cache reads and writes, per step.
- *Share of input from cache:* Amazon Bedrock bills cache reads at a reduced rate.
- *Accuracy:* where a benchmark trades tokens against it.

## Questions

<!-- BEGIN GENERATED FAQ -->

### Where do the tokens go?

**Answer:** Not yet measured. [Details: TU-01](#tu-01-where-do-the-tokens-go)

### How much does prompt caching save in extraction?

**Answer:** Not yet measured. [Details: TU-02](#tu-02-how-much-does-prompt-caching-save-in-extraction)

### What do page images cost in tokens, step by step?

**Answer:** Not yet measured. [Details: TU-03](#tu-03-what-do-page-images-cost-in-tokens-step-by-step)

### What is the cheapest configuration that keeps accuracy?

**Answer:** Not yet measured. [Details: TU-04](#tu-04-what-is-the-cheapest-configuration-that-keeps-accuracy)

### How many tokens does each extraction model use for the same document?

**Answer:** Not yet measured. [Details: TU-05](#tu-05-how-many-tokens-does-each-extraction-model-use-for-the-same-document)

<!-- END GENERATED FAQ -->

## Benchmark details

<!-- BEGIN GENERATED ABLATIONS -->

#### TU-01: Where do the tokens go?

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


#### TU-02: How much does prompt caching save in extraction?

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


#### TU-03: What do page images cost in tokens, step by step?

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


#### TU-04: What is the cheapest configuration that keeps accuracy?

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


#### TU-05: How many tokens does each extraction model use for the same document?

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
