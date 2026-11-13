---
title: "Key Information Extraction Benchmarks"
tableOfContents:
  maxHeadingLevel: 3
---

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

# Key Information Extraction Benchmarks

Extraction fills your database. For each section, it returns the values of the fields you
defined for the section's document class.
[Key Information Extraction](../idp-fundamentals/extraction.md) explains how it works.

## What decides extraction accuracy on your documents

This page measures how configuration choices change extraction accuracy. On your own
documents, two things matter more than any setting.

**1. Your definitions.** The extraction model returns the fields you define, in the structure
you define, and reads each field's description as its instruction. Good definitions:

- **Name the right fields.** Ask for the values your database needs, one value per field.
- **Get the relationships right.** Put values that belong together, such as the date, rate
  and description of a line item, in one list, so each row stays whole.
- **Say clearly what each field is.** Say where the value appears and what it is not: "the
  date the invoice was issued, not the due date".
- **Show what a value looks like.** Give the format you want, such as YYYY-MM-DD, or a number
  without a currency sign. For a hard document class, add a few-shot example.

See [Improving accuracy](../idp-fundamentals/extraction.md#improving-accuracy-once-your-pipeline-is-running).

**2. Your annotations.** Test Studio measures accuracy against the ground truth in your test
set, so a wrong annotation counts as an extraction error. In our experience, annotation
errors usually make up more than half of the errors Test Studio reports. Reliable numbers
need a test set with few annotation errors, and getting there usually takes a few rounds of
review: check each reported error, and fix the annotation when the extraction was right. See
[Measure with ground truth](../idp-fundamentals/index.md#4-measure-with-ground-truth) and
[Draft labeling](../test-studio.md#draft-labeling-unlabeled-documents--ground-truth).

**Data quality** matters too. The extraction model reads the OCR text and the page images.
Poor scans and handwriting give it less to read, and long tables need a mode built for them.

**Settings** are what the benchmarks below measure:

| Setting | What it changes | Questions |
|---|---|---|
| *Extraction mode* (`extraction.mode`) | One request per section (*Simple*), or an agent that works through the section in shards (*Advanced*) | [EX-01](#when-is-agentic-iterative-extraction-worth-it), [EX-07](#does-deterministic-table-parsing-help-iterative-extraction) to [EX-09](#should-iterative-extraction-load-page-images-only-when-it-needs-them) |
| *Extraction model* (`extraction.model`) | The model that reads the section | [EX-02](#which-extraction-model-should-i-use) |
| Reasoning effort (`extraction.reasoning_effort`) | How long the model reasons before it answers | [EX-03](#does-more-reasoning-effort-improve-extraction) |
| Few-shot examples | Sample documents with their correct values, added to the prompt | [EX-05](#do-few-shot-examples-help-extraction) |
| Page images | Whether the model sees the pages as well as the OCR text | [EX-06](#does-sending-page-images-to-the-extraction-model-help) |
| Value coercion and schema validation | Type repair and schema checks on every record | [EX-10](#do-schema-validation-and-value-coercion-improve-the-output), [EX-11](#should-i-retry-failed-fields-with-a-stronger-model) |

## Questions

<!-- BEGIN GENERATED FAQ -->

### When is agentic (iterative) extraction worth it?

**Answer:** Not for invoices or forms. On RealKIE invoices both modes scored 0.80; on W-2 forms iterative scored 0.97 against 0.95, a difference within the noise. Iterative used about the same total tokens per page on invoices and 3.4 times as many on W-2s. Use single pass unless your documents have long lists. [Details: EX-01](#ex-01-when-is-agentic-iterative-extraction-worth-it)

![Weighted accuracy against total tokens per page for each Extraction mode](../../images/benchmark-guidance/EX-01-fields.svg)

*Weighted accuracy against total tokens per page. Each point is one value of the setting; lines span two standard errors either side. Up and to the left is better.* Datasets: [RealKIE](datasets.md#realkie-fcc-verified-20-invoices), [RealKIE, short](datasets.md#realkie-fcc-verified-short-invoices-24-invoices-1-or-2-pages), [Fake-W2](datasets.md#fake-w2-tax-forms-w-2-forms-45-fields).

### Which extraction model should I use?

**Answer:** Not yet measured. [Details: EX-02](#ex-02-which-extraction-model-should-i-use)

### Does more reasoning effort improve extraction?

**Answer:** A little, for few tokens. High effort raised accuracy from 0.79 to 0.83 on RealKIE invoices and from 0.95 to 0.97 on W-2 forms, for 2 to 5% more total tokens per page and a few seconds per document. Both gains are near the edge of the noise on 20 documents, so confirm on your own test set before you change the default. [Details: EX-03](#ex-03-does-more-reasoning-effort-improve-extraction)

![Weighted accuracy against total tokens per page for each `extraction.reasoning_effort`](../../images/benchmark-guidance/EX-03-fields.svg)

*Weighted accuracy against total tokens per page. Each point is one value of the setting; lines span two standard errors either side. Up and to the left is better.* Datasets: [RealKIE](datasets.md#realkie-fcc-verified-20-invoices), [Fake-W2](datasets.md#fake-w2-tax-forms-w-2-forms-45-fields).

### How much do field descriptions matter?

**Answer:** Not yet measured. [Details: EX-04](#ex-04-how-much-do-field-descriptions-matter)

### Do few-shot examples help extraction?

**Answer:** Not yet measured. [Details: EX-05](#ex-05-do-few-shot-examples-help-extraction)

### Does sending page images to the extraction model help?

**Answer:** Not yet measured. [Details: EX-06](#ex-06-does-sending-page-images-to-the-extraction-model-help)

### Does deterministic table parsing help iterative extraction?

**Answer:** Not yet measured. [Details: EX-07](#ex-07-does-deterministic-table-parsing-help-iterative-extraction)

### What shard size should iterative extraction use?

**Answer:** Not yet measured. [Details: EX-08](#ex-08-what-shard-size-should-iterative-extraction-use)

### Should iterative extraction load page images only when it needs them?

**Answer:** Not yet measured. [Details: EX-09](#ex-09-should-iterative-extraction-load-page-images-only-when-it-needs-them)

### Do schema validation and value coercion improve the output?

**Answer:** Not yet measured. [Details: EX-10](#ex-10-do-schema-validation-and-value-coercion-improve-the-output)

### Should I retry failed fields with a stronger model?

**Answer:** Not yet measured. [Details: EX-11](#ex-11-should-i-retry-failed-fields-with-a-stronger-model)

### Does structured output make single-pass extraction more accurate?

**Answer:** Not yet measured. [Details: EX-12](#ex-12-does-structured-output-make-single-pass-extraction-more-accurate)

### How should I extract sections that hold several records?

**Answer:** Not yet measured. [Details: EX-13](#ex-13-how-should-i-extract-sections-that-hold-several-records)

### How accurate is extraction across many document formats?

**Answer:** Not yet measured. [Details: EX-14](#ex-14-how-accurate-is-extraction-across-many-document-formats)

### How much do splitting errors cost extraction in a packet?

**Answer:** Not yet measured. [Details: EX-15](#ex-15-how-much-do-splitting-errors-cost-extraction-in-a-packet)

<!-- END GENERATED FAQ -->

## Metrics on this page

- *Completeness:* rows returned ÷ rows in ground truth, on the synthetic statements.
- *Cell accuracy:* the share of returned cells that match ground truth, on the synthetic
  statements.
- *Weighted accuracy:* Stickler's field-weighted score against ground truth.
- *Documents with every field right:* the share of documents with no wrong field.

Read completeness and accuracy together: perfect accuracy on half the rows is still half
the rows.

[Benchmark Datasets](datasets.md) describes each dataset.

## Benchmark details

<!-- BEGIN GENERATED ABLATIONS -->

#### EX-01: When is agentic (iterative) extraction worth it?

**Answer:** Not for invoices or forms. On RealKIE invoices both modes scored 0.80; on W-2 forms iterative scored 0.97 against 0.95, a difference within the noise. Iterative used about the same total tokens per page on invoices and 3.4 times as many on W-2s. Use single pass unless your documents have long lists.

*Measured on release 0.6.15.dev1, November 2026, us-east-1. Source: `Test Studio runs RealKIE-FCC-Verified-20261113-173220, RealKIE-FCC-Verified-20261113-173644, RealKIE-FCC-Verified-20261113-173641, RealKIE-FCC-Verified-20261113-173219, RealKIE-FCC-Verified-20261113-173642, RealKIE-FCC-Verified-20261113-173643, Fake-W2-Tax-Forms-20261113-181721, Fake-W2-Tax-Forms-20261113-181722, Fake-W2-Tax-Forms-20261113-181723, Fake-W2-Tax-Forms-20261113-181901, Fake-W2-Tax-Forms-20261113-182002, Fake-W2-Tax-Forms-20261113-182011, realkie-fcc-short-20261113-201254, realkie-fcc-short-20261113-201252, realkie-fcc-short-20261113-201253, realkie-fcc-short-20261113-201713, realkie-fcc-short-20261113-201703, realkie-fcc-short-20261113-201714`.*

| | |
|---|---|
| **Changes** | Extraction mode |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [Synthetic statement, 100 rows (3 pages)](datasets.md#synthetic-statement-100-rows-3-pages); [Synthetic statement, 400 rows (9 pages)](datasets.md#synthetic-statement-400-rows-9-pages); [Synthetic statement, 800 rows (17 pages)](datasets.md#synthetic-statement-800-rows-17-pages); [Synthetic statement, 1,600 rows (33 pages)](datasets.md#synthetic-statement-1600-rows-33-pages); [Synthetic statement, 3,200 rows (66 pages)](datasets.md#synthetic-statement-3200-rows-66-pages); [RealKIE-FCC-Verified (20 invoices)](datasets.md#realkie-fcc-verified-20-invoices); [RealKIE-FCC-Verified, short invoices (24 invoices, 1 or 2 pages)](datasets.md#realkie-fcc-verified-short-invoices-24-invoices-1-or-2-pages); [RealKIE-FCC-Verified, long invoices (19 invoices, 8 to 33 pages)](datasets.md#realkie-fcc-verified-long-invoices-19-invoices-8-to-33-pages); [Fake-W2-Tax-Forms (W-2 forms, 45 fields)](datasets.md#fake-w2-tax-forms-w-2-forms-45-fields) |
| **Runs** | 3 per document, per value |

| Dataset | Extraction mode | Completeness | Cell accuracy | Extraction tokens per page | Total tokens per page | Median seconds per document |
|---|---|---|---|---|---|---|
| Statement, 100 rows | Single pass, Simple (default) | — | — | — | — | — |
| Statement, 100 rows | Iterative, Advanced | — | — | — | — | — |
| Statement, 400 rows | Single pass, Simple (default) | — | — | — | — | — |
| Statement, 400 rows | Iterative, Advanced | — | — | — | — | — |
| Statement, 800 rows | Single pass, Simple (default) | — | — | — | — | — |
| Statement, 800 rows | Iterative, Advanced | — | — | — | — | — |
| Statement, 1,600 rows | Single pass, Simple (default) | — | — | — | — | — |
| Statement, 1,600 rows | Iterative, Advanced | — | — | — | — | — |
| Statement, 3,200 rows | Single pass, Simple (default) | — | — | — | — | — |
| Statement, 3,200 rows | Iterative, Advanced | — | — | — | — | — |

| Dataset | Extraction mode | Weighted accuracy | Extraction tokens per page | Total tokens per page | Median seconds per document |
|---|---|---|---|---|---|
| RealKIE | Single pass, Simple (default) | 0.8 ± 0.06 | 7,042 ± 14 | 20,208 ± 339 | 58 ± 37 |
| RealKIE | Iterative, Advanced | 0.8 ± 0.08 | 15,368 ± 597 | 20,843 ± 516 | 65 ± 29 |
| RealKIE, short | Single pass, Simple (default) | 0.82 ± 0.06 | 8,593 ± 29 | 19,612 ± 253 | 22 ± 0.65 |
| RealKIE, short | Iterative, Advanced | 0.82 ± 0.06 | 34,802 ± 2,925 | 41,424 ± 2,846 | 28 ± 1.63 |
| RealKIE, long | Single pass, Simple (default) | — | — | — | — |
| RealKIE, long | Iterative, Advanced | — | — | — | — |
| Fake-W2 | Single pass, Simple (default) | 0.95 ± 0.02 | 6,876 ± 2.3 | 15,192 ± 2.09 | 38 ± 1.14 |
| Fake-W2 | Iterative, Advanced | 0.97 ± 0.01 | 46,661 ± 84 | 51,789 ± 84 | 30 ± 0.46 |


#### EX-02: Which extraction model should I use?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Extraction model |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](datasets.md#realkie-fcc-verified-20-invoices); [Fake-W2-Tax-Forms (W-2 forms, 45 fields)](datasets.md#fake-w2-tax-forms-w-2-forms-45-fields); [Synthetic statement, 400 rows (9 pages)](datasets.md#synthetic-statement-400-rows-9-pages) |
| **Runs** | 3 per document, per value |

| Dataset | Extraction model | Weighted accuracy | Extraction tokens per page | Total tokens per page | Median seconds per document |
|---|---|---|---|---|---|
| RealKIE | Claude Sonnet 5 (default) | — | — | — | — |
| RealKIE | Amazon Nova Lite | — | — | — | — |
| RealKIE | Amazon Nova Pro | — | — | — | — |
| RealKIE | Amazon Nova 2 Lite | — | — | — | — |
| RealKIE | Claude Haiku 5.5 | — | — | — | — |
| RealKIE | Claude Sonnet 4.6 | — | — | — | — |
| RealKIE | Claude Sonnet 5.5 | — | — | — | — |
| RealKIE | Claude Opus 5 | — | — | — | — |
| RealKIE | Claude Opus 5.5 | — | — | — | — |
| RealKIE | OpenAI GPT-6 Astra | — | — | — | — |
| RealKIE | xAI Grok 4.6 | — | — | — | — |
| Fake-W2 | Claude Sonnet 5 (default) | — | — | — | — |
| Fake-W2 | Amazon Nova Lite | — | — | — | — |
| Fake-W2 | Amazon Nova Pro | — | — | — | — |
| Fake-W2 | Amazon Nova 2 Lite | — | — | — | — |
| Fake-W2 | Claude Haiku 5.5 | — | — | — | — |
| Fake-W2 | Claude Sonnet 4.6 | — | — | — | — |
| Fake-W2 | Claude Sonnet 5.5 | — | — | — | — |
| Fake-W2 | Claude Opus 5 | — | — | — | — |
| Fake-W2 | Claude Opus 5.5 | — | — | — | — |
| Fake-W2 | OpenAI GPT-6 Astra | — | — | — | — |
| Fake-W2 | xAI Grok 4.6 | — | — | — | — |

| Dataset | Extraction model | Completeness | Cell accuracy | Extraction tokens per page | Total tokens per page | Median seconds per document |
|---|---|---|---|---|---|---|
| Statement, 400 rows | Claude Sonnet 5 (default) | — | — | — | — | — |
| Statement, 400 rows | Amazon Nova Lite | — | — | — | — | — |
| Statement, 400 rows | Amazon Nova Pro | — | — | — | — | — |
| Statement, 400 rows | Amazon Nova 2 Lite | — | — | — | — | — |
| Statement, 400 rows | Claude Haiku 5.5 | — | — | — | — | — |
| Statement, 400 rows | Claude Sonnet 4.6 | — | — | — | — | — |
| Statement, 400 rows | Claude Sonnet 5.5 | — | — | — | — | — |
| Statement, 400 rows | Claude Opus 5 | — | — | — | — | — |
| Statement, 400 rows | Claude Opus 5.5 | — | — | — | — | — |
| Statement, 400 rows | OpenAI GPT-6 Astra | — | — | — | — | — |
| Statement, 400 rows | xAI Grok 4.6 | — | — | — | — | — |


#### EX-03: Does more reasoning effort improve extraction?

**Answer:** A little, for few tokens. High effort raised accuracy from 0.79 to 0.83 on RealKIE invoices and from 0.95 to 0.97 on W-2 forms, for 2 to 5% more total tokens per page and a few seconds per document. Both gains are near the edge of the noise on 20 documents, so confirm on your own test set before you change the default.

*Measured on release 0.6.15.dev1, November 2026, us-east-1. Source: `Test Studio runs RealKIE-FCC-Verified-20261113-182228, RealKIE-FCC-Verified-20261113-182227, RealKIE-FCC-Verified-20261113-182229, RealKIE-FCC-Verified-20261113-182526, RealKIE-FCC-Verified-20261113-182544, RealKIE-FCC-Verified-20261113-182545, RealKIE-FCC-Verified-20261113-182844, RealKIE-FCC-Verified-20261113-182910, RealKIE-FCC-Verified-20261113-182913, Fake-W2-Tax-Forms-20261113-183212, Fake-W2-Tax-Forms-20261113-183229, Fake-W2-Tax-Forms-20261113-183239, Fake-W2-Tax-Forms-20261113-183329, Fake-W2-Tax-Forms-20261113-183342, Fake-W2-Tax-Forms-20261113-183353, Fake-W2-Tax-Forms-20261113-183514, Fake-W2-Tax-Forms-20261113-183519, Fake-W2-Tax-Forms-20261113-183520`.*

| | |
|---|---|
| **Changes** | `extraction.reasoning_effort` |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](datasets.md#realkie-fcc-verified-20-invoices); [Fake-W2-Tax-Forms (W-2 forms, 45 fields)](datasets.md#fake-w2-tax-forms-w-2-forms-45-fields); [Synthetic statement, 400 rows (9 pages)](datasets.md#synthetic-statement-400-rows-9-pages) |
| **Runs** | 3 per document, per value |

| Dataset | `extraction.reasoning_effort` | Weighted accuracy | Extraction tokens per page | Total tokens per page | Median seconds per document |
|---|---|---|---|---|---|
| RealKIE | Low (default) | 0.79 ± 0.06 | 7,044 ± 4.43 | 20,562 ± 625 | 39 ± 3.15 |
| RealKIE | Medium | 0.81 ± 0.07 | 7,135 ± 35 | 20,586 ± 702 | 37 ± 4.02 |
| RealKIE | High | 0.83 ± 0.07 | 7,366 ± 39 | 20,883 ± 672 | 42 ± 6.27 |
| Fake-W2 | Low (default) | 0.95 ± 0.02 | 6,879 ± 4.2 | 15,196 ± 3.7 | 25 ± 1.07 |
| Fake-W2 | Medium | 0.97 ± 0.01 | 7,128 ± 63 | 15,444 ± 64 | 27 ± 0.5 |
| Fake-W2 | High | 0.97 ± 0.01 | 7,585 ± 80 | 15,900 ± 80 | 33 ± 1.73 |

| Dataset | `extraction.reasoning_effort` | Completeness | Extraction tokens per page | Total tokens per page | Median seconds per document |
|---|---|---|---|---|---|
| Statement, 400 rows | Low (default) | — | — | — | — |
| Statement, 400 rows | Medium | — | — | — | — |
| Statement, 400 rows | High | — | — | — | — |


#### EX-04: How much do field descriptions matter?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Field descriptions |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](datasets.md#realkie-fcc-verified-20-invoices); [Fake-W2-Tax-Forms (W-2 forms, 45 fields)](datasets.md#fake-w2-tax-forms-w-2-forms-45-fields) |
| **Runs** | 3 per document, per value |

| Dataset | Field descriptions | Weighted accuracy | Documents with every field right | Extraction tokens per page |
|---|---|---|---|---|
| RealKIE | Field names only | — | — | — |
| RealKIE | Short descriptions | — | — | — |
| RealKIE | Descriptions with location, exclusions and format | — | — | — |
| Fake-W2 | Field names only | — | — | — |
| Fake-W2 | Short descriptions | — | — | — |
| Fake-W2 | Descriptions with location, exclusions and format | — | — | — |


#### EX-05: Do few-shot examples help extraction?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Few-shot examples |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](datasets.md#realkie-fcc-verified-20-invoices); [Fake-W2-Tax-Forms (W-2 forms, 45 fields)](datasets.md#fake-w2-tax-forms-w-2-forms-45-fields) |
| **Runs** | 3 per document, per value |

| Dataset | Few-shot examples | Weighted accuracy | Documents with every field right | Extraction tokens per page |
|---|---|---|---|---|
| RealKIE | None (default) | — | — | — |
| RealKIE | One example per class | — | — | — |
| RealKIE | Three examples per class | — | — | — |
| Fake-W2 | None (default) | — | — | — |
| Fake-W2 | One example per class | — | — | — |
| Fake-W2 | Three examples per class | — | — | — |


#### EX-06: Does sending page images to the extraction model help?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Page images in the extraction prompt |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](datasets.md#realkie-fcc-verified-20-invoices); [Fake-W2-Tax-Forms (W-2 forms, 45 fields)](datasets.md#fake-w2-tax-forms-w-2-forms-45-fields); [ConfBench (RealKIE invoices with scan noise)](datasets.md#confbench-realkie-invoices-with-scan-noise) |
| **Runs** | 3 per document, per value |

| Dataset | Page images in the extraction prompt | Weighted accuracy | Documents with every field right | Extraction tokens per page |
|---|---|---|---|---|
| RealKIE | Text and images (default) | — | — | — |
| RealKIE | Text only | — | — | — |
| Fake-W2 | Text and images (default) | — | — | — |
| Fake-W2 | Text only | — | — | — |
| ConfBench | Text and images (default) | — | — | — |
| ConfBench | Text only | — | — | — |


#### EX-07: Does deterministic table parsing help iterative extraction?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | `extraction.agentic.table_parsing.enabled` |
| **Everything else** | Iterative (Advanced) extraction; the rest as each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [Synthetic statement, 400 rows (9 pages)](datasets.md#synthetic-statement-400-rows-9-pages); [Synthetic statement, 800 rows (17 pages)](datasets.md#synthetic-statement-800-rows-17-pages); [Synthetic statement, 3,200 rows (66 pages)](datasets.md#synthetic-statement-3200-rows-66-pages) |
| **Runs** | 3 per document, per value |

| Dataset | `extraction.agentic.table_parsing.enabled` | Completeness | Cell accuracy | Extraction tokens per page | Median seconds per document |
|---|---|---|---|---|---|
| Statement, 400 rows | On (default) | — | — | — | — |
| Statement, 400 rows | Off | — | — | — | — |
| Statement, 800 rows | On (default) | — | — | — | — |
| Statement, 800 rows | Off | — | — | — | — |
| Statement, 3,200 rows | On (default) | — | — | — | — |
| Statement, 3,200 rows | Off | — | — | — | — |


#### EX-08: What shard size should iterative extraction use?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Pages per shard (`max_pages_per_shard`) |
| **Everything else** | Iterative (Advanced) extraction; the rest as each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [Synthetic statement, 800 rows (17 pages)](datasets.md#synthetic-statement-800-rows-17-pages); [Synthetic statement, 3,200 rows (66 pages)](datasets.md#synthetic-statement-3200-rows-66-pages) |
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


#### EX-09: Should iterative extraction load page images only when it needs them?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | `extraction.agentic.table_parsing.lazy_images` |
| **Everything else** | Iterative (Advanced) extraction; the rest as each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [Synthetic statement, 400 rows (9 pages)](datasets.md#synthetic-statement-400-rows-9-pages); [Synthetic statement, 800 rows (17 pages)](datasets.md#synthetic-statement-800-rows-17-pages); [RealKIE-FCC-Verified (20 invoices)](datasets.md#realkie-fcc-verified-20-invoices) |
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


#### EX-10: Do schema validation and value coercion improve the output?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | `extraction.validation` and `extraction.coercion` |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [Fake-W2-Tax-Forms (W-2 forms, 45 fields)](datasets.md#fake-w2-tax-forms-w-2-forms-45-fields); [RealKIE-FCC-Verified (20 invoices)](datasets.md#realkie-fcc-verified-20-invoices) |
| **Runs** | 3 per document, per value |

| Dataset | `extraction.validation` and `extraction.coercion` | Weighted accuracy | Documents with every field right | Extraction tokens per page |
|---|---|---|---|---|
| Fake-W2 | Both on (default) | — | — | — |
| Fake-W2 | Coercion off | — | — | — |
| Fake-W2 | Validation off | — | — | — |
| RealKIE | Both on (default) | — | — | — |
| RealKIE | Coercion off | — | — | — |
| RealKIE | Validation off | — | — | — |


#### EX-11: Should I retry failed fields with a stronger model?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | `extraction.validation.fail_action` |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [Fake-W2-Tax-Forms (W-2 forms, 45 fields)](datasets.md#fake-w2-tax-forms-w-2-forms-45-fields); [RealKIE-FCC-Verified (20 invoices)](datasets.md#realkie-fcc-verified-20-invoices) |
| **Runs** | 3 per document, per value |

| Dataset | `extraction.validation.fail_action` | Weighted accuracy | Documents with every field right | Extraction tokens per page |
|---|---|---|---|---|
| Fake-W2 | warn (default) | — | — | — |
| Fake-W2 | escalate | — | — | — |
| Fake-W2 | reject | — | — | — |
| RealKIE | warn (default) | — | — | — |
| RealKIE | escalate | — | — | — |
| RealKIE | reject | — | — | — |


#### EX-12: Does structured output make single-pass extraction more accurate?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Schema enforcement (`extraction.schema_enforcement.mode`) |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](datasets.md#realkie-fcc-verified-20-invoices); [Fake-W2-Tax-Forms (W-2 forms, 45 fields)](datasets.md#fake-w2-tax-forms-w-2-forms-45-fields); [RealKIE-FCC-Verified, long invoices (19 invoices, 8 to 33 pages)](datasets.md#realkie-fcc-verified-long-invoices-19-invoices-8-to-33-pages) |
| **Runs** | 3 per document, per value |

| Dataset | Schema enforcement (`extraction.schema_enforcement.mode`) | Weighted accuracy | Documents with every field right | Extraction tokens per page | Total tokens per page | Median seconds per document |
|---|---|---|---|---|---|---|
| RealKIE | Off: schema in the prompt (default) | — | — | — | — | — |
| RealKIE | Structured output | — | — | — | — | — |
| RealKIE | Forced tool | — | — | — | — | — |
| Fake-W2 | Off: schema in the prompt (default) | — | — | — | — | — |
| Fake-W2 | Structured output | — | — | — | — | — |
| Fake-W2 | Forced tool | — | — | — | — | — |
| RealKIE, long | Off: schema in the prompt (default) | — | — | — | — | — |
| RealKIE, long | Structured output | — | — | — | — | — |
| RealKIE, long | Forced tool | — | — | — | — | — |


#### EX-13: How should I extract sections that hold several records?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Multi-instance sections |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [Synthetic file holding two statements](datasets.md#synthetic-file-holding-two-statements); [Fake-W2-Tax-Forms (W-2 forms, 45 fields)](datasets.md#fake-w2-tax-forms-w-2-forms-45-fields) |
| **Runs** | 3 per document, per value |

| Dataset | Multi-instance sections | Weighted accuracy | Extraction tokens per page |
|---|---|---|---|
| Fake-W2 | Off (default) | — | — |
| Fake-W2 | On | — | — |


#### EX-14: How accurate is extraction across many document formats?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Document format |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [OmniAI-OCR-Benchmark, all 9 formats (293 documents)](datasets.md#omniai-ocr-benchmark-all-9-formats-293-documents) |
| **Runs** | 3 per document, per value |

| Dataset | Document format | Weighted accuracy | Documents with every field right | Extraction tokens per page |
|---|---|---|---|---|
| OmniAI | Each of the 9 OmniAI formats | — | — | — |


#### EX-15: How much do splitting errors cost extraction in a packet?

**Answer:** Not yet measured.

Needs a dataset we haven't built yet: Packets with section and field ground truth (to be built).

| | |
|---|---|
| **Changes** | Granularity and strategy |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [Packets with section and field ground truth (to be built)](datasets.md#packets-with-section-and-field-ground-truth-to-be-built) |
| **Runs** | 3 per document, per value |

| Dataset | Granularity and strategy | Boundary accuracy | Weighted accuracy | Total tokens per page |
|---|---|---|---|---|
| Packets with fields | Page by page, one call (default) | — | — | — |
| Packets with fields | Holistic, one call | — | — | — |
| Packets with fields | Detect sections first, then classify | — | — | — |

<!-- END GENERATED ABLATIONS -->
