---
title: "Key Information Extraction Benchmarks"
---

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

# Key Information Extraction Benchmarks

- When is agentic (iterative) extraction worth it?
- Which extraction model should I use?
- What's the spread between Opus and Haiku?
- Do few-shot examples help extraction?

[Key Information Extraction](../idp-fundamentals/extraction.md) explains how the
accelerator extracts fields.

**Metrics**

- *Completeness:* rows returned ÷ rows in ground truth, on the synthetic statements.
- *Cell accuracy:* the share of returned cells that match ground truth, on the synthetic
  statements.
- *Weighted accuracy:* Stickler's field-weighted score against ground truth.
- *Documents with every field right:* the share of documents with no wrong field.

Read completeness and accuracy together: perfect accuracy on half the rows is still half
the rows.

## Benchmarks

<!-- BEGIN GENERATED ABLATIONS -->

### EX-01: When is agentic (iterative) extraction worth it?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Extraction mode |
| **Everything else** | The [defaults](index.md#the-default-configuration) |
| **Datasets** | [Synthetic statement, 100 rows (3 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements); [Synthetic statement, 800 rows (17 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements); [Synthetic statement, 1,600 rows (33 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements); [Synthetic statement, 3,200 rows (66 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements); [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [Fake-W2-Tax-Forms (W-2 forms, 45 fields)](../idp-fundamentals/benchmark-datasets.md#fake-w2-tax-forms) |
| **Runs** | 3 per document, per value |

| Dataset | Extraction mode | Completeness | Cell accuracy | Extraction tokens per page | Median seconds per document |
|---|---|---|---|---|---|
| Statement, 100 rows | Single pass, Simple (default) | — | — | — | — |
| Statement, 100 rows | Iterative, Advanced | — | — | — | — |
| Statement, 400 rows | Single pass, Simple (default) | — | — | — | — |
| Statement, 400 rows | Iterative, Advanced | — | — | — | — |
| Statement, 800 rows | Single pass, Simple (default) | — | — | — | — |
| Statement, 800 rows | Iterative, Advanced | — | — | — | — |
| Statement, 1,600 rows | Single pass, Simple (default) | — | — | — | — |
| Statement, 1,600 rows | Iterative, Advanced | — | — | — | — |
| Statement, 3,200 rows | Single pass, Simple (default) | — | — | — | — |
| Statement, 3,200 rows | Iterative, Advanced | — | — | — | — |

| Dataset | Extraction mode | Weighted accuracy | Extraction tokens per page | Median seconds per document |
|---|---|---|---|---|
| RealKIE | Single pass, Simple (default) | — | — | — |
| RealKIE | Iterative, Advanced | — | — | — |
| Fake-W2 | Single pass, Simple (default) | — | — | — |
| Fake-W2 | Iterative, Advanced | — | — | — |


### EX-02: Which extraction model should I use?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Extraction model |
| **Everything else** | The [defaults](index.md#the-default-configuration) |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [Fake-W2-Tax-Forms (W-2 forms, 45 fields)](../idp-fundamentals/benchmark-datasets.md#fake-w2-tax-forms); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document, per value |

| Dataset | Extraction model | Weighted accuracy | Extraction tokens per page | Median seconds per document |
|---|---|---|---|---|
| RealKIE | Claude Sonnet 5 (default) | — | — | — |
| RealKIE | Amazon Nova Lite | — | — | — |
| RealKIE | Amazon Nova Pro | — | — | — |
| RealKIE | Amazon Nova 2 Lite | — | — | — |
| RealKIE | Claude Haiku 5.5 | — | — | — |
| RealKIE | Claude Sonnet 4.6 | — | — | — |
| RealKIE | Claude Sonnet 5.5 | — | — | — |
| RealKIE | Claude Opus 5 | — | — | — |
| RealKIE | Claude Opus 5.5 | — | — | — |
| RealKIE | OpenAI GPT-6 Astra | — | — | — |
| RealKIE | xAI Grok 4.6 | — | — | — |
| Fake-W2 | Claude Sonnet 5 (default) | — | — | — |
| Fake-W2 | Amazon Nova Lite | — | — | — |
| Fake-W2 | Amazon Nova Pro | — | — | — |
| Fake-W2 | Amazon Nova 2 Lite | — | — | — |
| Fake-W2 | Claude Haiku 5.5 | — | — | — |
| Fake-W2 | Claude Sonnet 4.6 | — | — | — |
| Fake-W2 | Claude Sonnet 5.5 | — | — | — |
| Fake-W2 | Claude Opus 5 | — | — | — |
| Fake-W2 | Claude Opus 5.5 | — | — | — |
| Fake-W2 | OpenAI GPT-6 Astra | — | — | — |
| Fake-W2 | xAI Grok 4.6 | — | — | — |

| Dataset | Extraction model | Completeness | Cell accuracy | Extraction tokens per page | Median seconds per document |
|---|---|---|---|---|---|
| Statement, 400 rows | Claude Sonnet 5 (default) | — | — | — | — |
| Statement, 400 rows | Amazon Nova Lite | — | — | — | — |
| Statement, 400 rows | Amazon Nova Pro | — | — | — | — |
| Statement, 400 rows | Amazon Nova 2 Lite | — | — | — | — |
| Statement, 400 rows | Claude Haiku 5.5 | — | — | — | — |
| Statement, 400 rows | Claude Sonnet 4.6 | — | — | — | — |
| Statement, 400 rows | Claude Sonnet 5.5 | — | — | — | — |
| Statement, 400 rows | Claude Opus 5 | — | — | — | — |
| Statement, 400 rows | Claude Opus 5.5 | — | — | — | — |
| Statement, 400 rows | OpenAI GPT-6 Astra | — | — | — | — |
| Statement, 400 rows | xAI Grok 4.6 | — | — | — | — |


### EX-03: What's the spread between Opus and Haiku?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Extraction model |
| **Everything else** | Run in both extraction modes; the rest at the [defaults](index.md#the-default-configuration) |
| **Datasets** | [Fake-W2-Tax-Forms (W-2 forms, 45 fields)](../idp-fundamentals/benchmark-datasets.md#fake-w2-tax-forms); [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [ConfBench (RealKIE invoices with scan noise)](../extensions/confbench-testset.md); [Synthetic statement, 800 rows (17 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document, per value |

| Dataset | Extraction model | Weighted accuracy | Documents with every field right | Extraction tokens per page | Median seconds per document |
|---|---|---|---|---|---|
| Fake-W2 | Claude Haiku 5.5 | — | — | — | — |
| Fake-W2 | Claude Sonnet 5 (default) | — | — | — | — |
| Fake-W2 | Claude Opus 5.5 | — | — | — | — |
| RealKIE | Claude Haiku 5.5 | — | — | — | — |
| RealKIE | Claude Sonnet 5 (default) | — | — | — | — |
| RealKIE | Claude Opus 5.5 | — | — | — | — |
| ConfBench | Claude Haiku 5.5 | — | — | — | — |
| ConfBench | Claude Sonnet 5 (default) | — | — | — | — |
| ConfBench | Claude Opus 5.5 | — | — | — | — |

| Dataset | Extraction model | Completeness | Extraction tokens per page | Median seconds per document |
|---|---|---|---|---|
| Statement, 800 rows | Claude Haiku 5.5 | — | — | — |
| Statement, 800 rows | Claude Sonnet 5 (default) | — | — | — |
| Statement, 800 rows | Claude Opus 5.5 | — | — | — |


### EX-04: Does more reasoning effort improve extraction?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | `extraction.reasoning_effort` |
| **Everything else** | The [defaults](index.md#the-default-configuration) |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [Fake-W2-Tax-Forms (W-2 forms, 45 fields)](../idp-fundamentals/benchmark-datasets.md#fake-w2-tax-forms); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document, per value |

| Dataset | `extraction.reasoning_effort` | Weighted accuracy | Extraction tokens per page | Median seconds per document |
|---|---|---|---|---|
| RealKIE | Low (default) | — | — | — |
| RealKIE | Medium | — | — | — |
| RealKIE | High | — | — | — |
| Fake-W2 | Low (default) | — | — | — |
| Fake-W2 | Medium | — | — | — |
| Fake-W2 | High | — | — | — |

| Dataset | `extraction.reasoning_effort` | Completeness | Extraction tokens per page | Median seconds per document |
|---|---|---|---|---|
| Statement, 400 rows | Low (default) | — | — | — |
| Statement, 400 rows | Medium | — | — | — |
| Statement, 400 rows | High | — | — | — |


### EX-05: How much do field descriptions matter?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Field descriptions |
| **Everything else** | The [defaults](index.md#the-default-configuration) |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [Fake-W2-Tax-Forms (W-2 forms, 45 fields)](../idp-fundamentals/benchmark-datasets.md#fake-w2-tax-forms) |
| **Runs** | 3 per document, per value |

| Dataset | Field descriptions | Weighted accuracy | Documents with every field right | Extraction tokens per page |
|---|---|---|---|---|
| RealKIE | Field names only | — | — | — |
| RealKIE | Short descriptions | — | — | — |
| RealKIE | Descriptions with location, exclusions and format | — | — | — |
| Fake-W2 | Field names only | — | — | — |
| Fake-W2 | Short descriptions | — | — | — |
| Fake-W2 | Descriptions with location, exclusions and format | — | — | — |


### EX-06: Do few-shot examples help extraction?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Few-shot examples |
| **Everything else** | The [defaults](index.md#the-default-configuration) |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [Fake-W2-Tax-Forms (W-2 forms, 45 fields)](../idp-fundamentals/benchmark-datasets.md#fake-w2-tax-forms) |
| **Runs** | 3 per document, per value |

| Dataset | Few-shot examples | Weighted accuracy | Documents with every field right | Extraction tokens per page |
|---|---|---|---|---|
| RealKIE | None (default) | — | — | — |
| RealKIE | One example per class | — | — | — |
| RealKIE | Three examples per class | — | — | — |
| Fake-W2 | None (default) | — | — | — |
| Fake-W2 | One example per class | — | — | — |
| Fake-W2 | Three examples per class | — | — | — |


### EX-07: Does sending page images to the extraction model help?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Page images in the extraction prompt |
| **Everything else** | The [defaults](index.md#the-default-configuration) |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [Fake-W2-Tax-Forms (W-2 forms, 45 fields)](../idp-fundamentals/benchmark-datasets.md#fake-w2-tax-forms); [ConfBench (RealKIE invoices with scan noise)](../extensions/confbench-testset.md) |
| **Runs** | 3 per document, per value |

| Dataset | Page images in the extraction prompt | Weighted accuracy | Documents with every field right | Extraction tokens per page |
|---|---|---|---|---|
| RealKIE | Text and images (default) | — | — | — |
| RealKIE | Text only | — | — | — |
| Fake-W2 | Text and images (default) | — | — | — |
| Fake-W2 | Text only | — | — | — |
| ConfBench | Text and images (default) | — | — | — |
| ConfBench | Text only | — | — | — |


### EX-08: Does deterministic table parsing help iterative extraction?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | `extraction.agentic.table_parsing.enabled` |
| **Everything else** | Iterative (Advanced) extraction; the rest at the [defaults](index.md#the-default-configuration) |
| **Datasets** | [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements); [Synthetic statement, 800 rows (17 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements); [Synthetic statement, 3,200 rows (66 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document, per value |

| Dataset | `extraction.agentic.table_parsing.enabled` | Completeness | Cell accuracy | Extraction tokens per page | Median seconds per document |
|---|---|---|---|---|---|
| Statement, 400 rows | On (default) | — | — | — | — |
| Statement, 400 rows | Off | — | — | — | — |
| Statement, 800 rows | On (default) | — | — | — | — |
| Statement, 800 rows | Off | — | — | — | — |
| Statement, 3,200 rows | On (default) | — | — | — | — |
| Statement, 3,200 rows | Off | — | — | — | — |


### EX-09: What shard size should iterative extraction use?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Pages per shard (`max_pages_per_shard`) |
| **Everything else** | Iterative (Advanced) extraction; the rest at the [defaults](index.md#the-default-configuration) |
| **Datasets** | [Synthetic statement, 800 rows (17 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements); [Synthetic statement, 3,200 rows (66 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document, per value |

| Dataset | Pages per shard (`max_pages_per_shard`) | Completeness | Cell accuracy | Extraction tokens per page | Median seconds per document |
|---|---|---|---|---|---|
| Statement, 800 rows | 5 (default) | — | — | — | — |
| Statement, 800 rows | 3 | — | — | — | — |
| Statement, 800 rows | 10 | — | — | — | — |
| Statement, 800 rows | 25 | — | — | — | — |
| Statement, 3,200 rows | 5 (default) | — | — | — | — |
| Statement, 3,200 rows | 3 | — | — | — | — |
| Statement, 3,200 rows | 10 | — | — | — | — |
| Statement, 3,200 rows | 25 | — | — | — | — |


### EX-10: Should iterative extraction load page images only when it needs them?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | `extraction.agentic.table_parsing.lazy_images` |
| **Everything else** | Iterative (Advanced) extraction; the rest at the [defaults](index.md#the-default-configuration) |
| **Datasets** | [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements); [Synthetic statement, 800 rows (17 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements); [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified) |
| **Runs** | 3 per document, per value |

| Dataset | `extraction.agentic.table_parsing.lazy_images` | Completeness | Cell accuracy | Extraction tokens per page |
|---|---|---|---|---|
| Statement, 400 rows | On (default) | — | — | — |
| Statement, 400 rows | Off | — | — | — |
| Statement, 800 rows | On (default) | — | — | — |
| Statement, 800 rows | Off | — | — | — |

| Dataset | `extraction.agentic.table_parsing.lazy_images` | Weighted accuracy | Extraction tokens per page |
|---|---|---|---|
| RealKIE | On (default) | — | — |
| RealKIE | Off | — | — |


### EX-11: Do schema validation and value coercion improve the output?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | `extraction.validation` and `extraction.coercion` |
| **Everything else** | The [defaults](index.md#the-default-configuration) |
| **Datasets** | [Fake-W2-Tax-Forms (W-2 forms, 45 fields)](../idp-fundamentals/benchmark-datasets.md#fake-w2-tax-forms); [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified) |
| **Runs** | 3 per document, per value |

| Dataset | `extraction.validation` and `extraction.coercion` | Weighted accuracy | Documents with every field right | Extraction tokens per page |
|---|---|---|---|---|
| Fake-W2 | Both on (default) | — | — | — |
| Fake-W2 | Coercion off | — | — | — |
| Fake-W2 | Validation off | — | — | — |
| RealKIE | Both on (default) | — | — | — |
| RealKIE | Coercion off | — | — | — |
| RealKIE | Validation off | — | — | — |


### EX-12: Should I retry failed fields with a stronger model?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | `extraction.validation.fail_action` |
| **Everything else** | The [defaults](index.md#the-default-configuration) |
| **Datasets** | [Fake-W2-Tax-Forms (W-2 forms, 45 fields)](../idp-fundamentals/benchmark-datasets.md#fake-w2-tax-forms); [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified) |
| **Runs** | 3 per document, per value |

| Dataset | `extraction.validation.fail_action` | Weighted accuracy | Documents with every field right | Extraction tokens per page |
|---|---|---|---|---|
| Fake-W2 | warn (default) | — | — | — |
| Fake-W2 | escalate | — | — | — |
| Fake-W2 | reject | — | — | — |
| RealKIE | warn (default) | — | — | — |
| RealKIE | escalate | — | — | — |
| RealKIE | reject | — | — | — |


### EX-13: Does forced tool use make single-pass output more reliable?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | `extraction.forced_tool.enabled` |
| **Everything else** | The [defaults](index.md#the-default-configuration) |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document, per value |

| Dataset | `extraction.forced_tool.enabled` | Weighted accuracy | Extraction tokens per page |
|---|---|---|---|
| RealKIE | Off (default) | — | — |
| RealKIE | On | — | — |

| Dataset | `extraction.forced_tool.enabled` | Completeness | Extraction tokens per page |
|---|---|---|---|
| Statement, 400 rows | Off (default) | — | — |
| Statement, 400 rows | On | — | — |


### EX-14: How should I extract sections that hold several records?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Multi-instance sections |
| **Everything else** | The [defaults](index.md#the-default-configuration) |
| **Datasets** | [Synthetic file holding two statements](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements); [Fake-W2-Tax-Forms (W-2 forms, 45 fields)](../idp-fundamentals/benchmark-datasets.md#fake-w2-tax-forms) |
| **Runs** | 3 per document, per value |

| Dataset | Multi-instance sections | Weighted accuracy | Extraction tokens per page |
|---|---|---|---|
| Fake-W2 | Off (default) | — | — |
| Fake-W2 | On | — | — |


### EX-15: How accurate is extraction across many document formats?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Document format |
| **Everything else** | The [defaults](index.md#the-default-configuration) |
| **Datasets** | [OmniAI-OCR-Benchmark, all 9 formats](../idp-fundamentals/benchmark-datasets.md#omniai-ocr-benchmark) |
| **Runs** | 3 per document, per value |

| Dataset | Document format | Weighted accuracy | Documents with every field right | Extraction tokens per page |
|---|---|---|---|---|
| OmniAI | Each of the 9 OmniAI formats | — | — | — |


### EX-16: How much do splitting errors cost extraction in a packet?

**Answer:** Not yet measured.

Needs a dataset we haven't built yet: Packets with section and field ground truth (to be built).

| | |
|---|---|
| **Changes** | Granularity and strategy |
| **Everything else** | The [defaults](index.md#the-default-configuration) |
| **Datasets** | Packets with section and field ground truth (to be built) |
| **Runs** | 3 per document, per value |

| Dataset | Granularity and strategy | Boundary accuracy | Weighted accuracy | Total tokens per page |
|---|---|---|---|---|
| Packets with fields | Page by page, one call (default) | — | — | — |
| Packets with fields | Holistic, one call | — | — | — |
| Packets with fields | Detect sections first, then classify | — | — | — |

<!-- END GENERATED ABLATIONS -->
