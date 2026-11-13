---
title: "Digitization (OCR) Benchmarks"
tableOfContents:
  maxHeadingLevel: 3
---

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

# Digitization (OCR) Benchmarks

Digitization turns each page into page text that the later steps read.
[Digitization (OCR)](../idp-fundamentals/digitization.md) explains how it works.

We don't benchmark OCR on its own today. We measure its effect on the steps after it: each
benchmark here scores the extraction accuracy an OCR reader produces, because that is what
lands in your database. To compare readers on OCR alone, use public OCR benchmarks.

## How to improve digitization on your documents

**Your definitions.** The reader doesn't use them: it reads every page the same way. When a
value is wrong, open [View Page Text](../web-ui.md#view-page-text) first. If the value is
right in the page text, the fix is in your classification or extraction definitions.

**Data quality.** Scan at 300 DPI, and turn on preprocessing for photos and poor scans. See
[Improving digitization](../idp-fundamentals/digitization.md#improving-digitization-once-your-pipeline-is-running).

**Settings.**

| Setting | What it changes | Questions |
|---|---|---|
| OCR reader (`ocr.backend`) | Amazon Textract, a vision model, or a specialized OCR model | [DG-01](#does-the-ocr-reader-make-a-difference-to-extraction-accuracy) to [DG-03](#does-a-specialized-ocr-model-beat-textract) |
| Resolution (`ocr.image.dpi`) | The DPI the accelerator renders pages at | [DG-04](#what-resolution-should-pages-be-rendered-at) |
| Preprocessing (`ocr.image.preprocessing`) | Cleans up shadows, uneven lighting and low contrast | [DG-05](#does-image-preprocessing-help-on-poor-scans) |
| Textract features (`ocr.features`) | Tables, layout and signatures | [DG-06](#which-textract-features-do-i-need) |

## Benchmark datasets and metrics

<!-- BEGIN GENERATED DATASETS -->

| Dataset | Preset |
|---|---|
| [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) | `bank-statement-sample` |
| [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified) | `realkie-fcc-verified` |
| [ConfBench (RealKIE invoices with scan noise)](../extensions/confbench-testset.md) | `realkie-fcc-verified` |
| [OmniAI-OCR-Benchmark, all 9 formats](../idp-fundamentals/benchmark-datasets.md#omniai-ocr-benchmark) | `ocr-benchmark` |
| [Fake-W2-Tax-Forms (W-2 forms, 45 fields)](../idp-fundamentals/benchmark-datasets.md#fake-w2-tax-forms) | `fake-w2` |
| Handwritten forms (to be built) | — |

<!-- END GENERATED DATASETS -->

**Metrics**

- *Weighted accuracy:* Stickler's field-weighted score against ground truth.
- *Documents with every field right:* the share of documents with no wrong field.
- *Completeness* and *cell accuracy:* see [Key Information Extraction Benchmarks](extraction.md).

## Questions

<!-- BEGIN GENERATED FAQ -->

### Does the OCR reader make a difference to extraction accuracy?

**Answer:** Not yet measured. [Details: DG-01](#dg-01-does-the-ocr-reader-make-a-difference-to-extraction-accuracy)

### If I read pages with a vision model, which model?

**Answer:** Not yet measured. [Details: DG-02](#dg-02-if-i-read-pages-with-a-vision-model-which-model)

### Does a specialized OCR model beat Textract?

**Answer:** Not yet measured. [Details: DG-03](#dg-03-does-a-specialized-ocr-model-beat-textract)

### What resolution should pages be rendered at?

**Answer:** Not yet measured. [Details: DG-04](#dg-04-what-resolution-should-pages-be-rendered-at)

### Does image preprocessing help on poor scans?

**Answer:** Not yet measured. [Details: DG-05](#dg-05-does-image-preprocessing-help-on-poor-scans)

### Which Textract features do I need?

**Answer:** Pick the features your documents need; none of the combinations we tried changed accuracy measurably. On RealKIE invoices and W-2 forms every combination scored within the noise of the default, and LAYOUT alone used about 3% fewer total tokens per page because it sends less page text. Textract prices each page by the features you select, so dropping a feature your documents do not need saves Textract charges rather than tokens. [Details: DG-06](#dg-06-which-textract-features-do-i-need)

![Weighted accuracy against total tokens per page for each `ocr.features`](../../images/benchmark-guidance/DG-06-fields.svg)

*Weighted accuracy against total tokens per page. Each point is one value of the setting; lines span two standard errors either side. Up and to the left is better.*

### How much accuracy does scan quality cost?

**Answer:** Not yet measured. [Details: DG-07](#dg-07-how-much-accuracy-does-scan-quality-cost)

### Which reader handles handwriting best?

**Answer:** Not yet measured. [Details: DG-08](#dg-08-which-reader-handles-handwriting-best)

<!-- END GENERATED FAQ -->

## Benchmark details

<!-- BEGIN GENERATED ABLATIONS -->

#### DG-01: Does the OCR reader make a difference to extraction accuracy?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | OCR reader |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [ConfBench (RealKIE invoices with scan noise)](../extensions/confbench-testset.md); [OmniAI-OCR-Benchmark, all 9 formats](../idp-fundamentals/benchmark-datasets.md#omniai-ocr-benchmark); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document, per value |

| Dataset | OCR reader | Weighted accuracy | OCR tokens per page | Total tokens per page |
|---|---|---|---|---|
| RealKIE | Textract, tables and layout (default) | — | — | — |
| RealKIE | Textract, layout only | — | — | — |
| RealKIE | Bedrock vision model (Nova 2 Lite) | — | — | — |
| ConfBench | Textract, tables and layout (default) | — | — | — |
| ConfBench | Textract, layout only | — | — | — |
| ConfBench | Bedrock vision model (Nova 2 Lite) | — | — | — |
| OmniAI | Textract, tables and layout (default) | — | — | — |
| OmniAI | Textract, layout only | — | — | — |
| OmniAI | Bedrock vision model (Nova 2 Lite) | — | — | — |

| Dataset | OCR reader | Completeness | Cell accuracy | OCR tokens per page | Total tokens per page |
|---|---|---|---|---|---|
| Statement, 400 rows | Textract, tables and layout (default) | — | — | — | — |
| Statement, 400 rows | Textract, layout only | — | — | — | — |
| Statement, 400 rows | Bedrock vision model (Nova 2 Lite) | — | — | — | — |


#### DG-02: If I read pages with a vision model, which model?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Model used for Bedrock vision OCR |
| **Everything else** | OCR reader set to the Bedrock vision model; the rest as each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [ConfBench (RealKIE invoices with scan noise)](../extensions/confbench-testset.md); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document, per value |

| Dataset | Model used for Bedrock vision OCR | Weighted accuracy | OCR tokens per page | Total tokens per page |
|---|---|---|---|---|
| RealKIE | Amazon Nova 2 Lite | — | — | — |
| RealKIE | Claude Haiku 5.5 | — | — | — |
| RealKIE | Claude Sonnet 5 | — | — | — |
| ConfBench | Amazon Nova 2 Lite | — | — | — |
| ConfBench | Claude Haiku 5.5 | — | — | — |
| ConfBench | Claude Sonnet 5 | — | — | — |

| Dataset | Model used for Bedrock vision OCR | Cell accuracy | OCR tokens per page | Total tokens per page |
|---|---|---|---|---|
| Statement, 400 rows | Amazon Nova 2 Lite | — | — | — |
| Statement, 400 rows | Claude Haiku 5.5 | — | — | — |
| Statement, 400 rows | Claude Sonnet 5 | — | — | — |


#### DG-03: Does a specialized OCR model beat Textract?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | OCR reader |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [ConfBench (RealKIE invoices with scan noise)](../extensions/confbench-testset.md); [OmniAI-OCR-Benchmark, all 9 formats](../idp-fundamentals/benchmark-datasets.md#omniai-ocr-benchmark) |
| **Runs** | 3 per document, per value |

| Dataset | OCR reader | Weighted accuracy | Documents with every field right | Total tokens per page |
|---|---|---|---|---|
| RealKIE | Textract, tables and layout (default) | — | — | — |
| RealKIE | Chandra (Lambda hook) | — | — | — |
| RealKIE | Mistral OCR (Lambda hook) | — | — | — |
| RealKIE | Cohere Parse (Lambda hook) | — | — | — |
| ConfBench | Textract, tables and layout (default) | — | — | — |
| ConfBench | Chandra (Lambda hook) | — | — | — |
| ConfBench | Mistral OCR (Lambda hook) | — | — | — |
| ConfBench | Cohere Parse (Lambda hook) | — | — | — |
| OmniAI | Textract, tables and layout (default) | — | — | — |
| OmniAI | Chandra (Lambda hook) | — | — | — |
| OmniAI | Mistral OCR (Lambda hook) | — | — | — |
| OmniAI | Cohere Parse (Lambda hook) | — | — | — |


#### DG-04: What resolution should pages be rendered at?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | `ocr.image.dpi` |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [ConfBench (RealKIE invoices with scan noise)](../extensions/confbench-testset.md); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document, per value |

| Dataset | `ocr.image.dpi` | Weighted accuracy | Total tokens per page |
|---|---|---|---|
| RealKIE | 300 (default) | — | — |
| RealKIE | 200 | — | — |
| RealKIE | 150 | — | — |
| ConfBench | 300 (default) | — | — |
| ConfBench | 200 | — | — |
| ConfBench | 150 | — | — |

| Dataset | `ocr.image.dpi` | Cell accuracy | Total tokens per page |
|---|---|---|---|
| Statement, 400 rows | 300 (default) | — | — |
| Statement, 400 rows | 200 | — | — |
| Statement, 400 rows | 150 | — | — |


#### DG-05: Does image preprocessing help on poor scans?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | `ocr.image.preprocessing` |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [ConfBench (RealKIE invoices with scan noise)](../extensions/confbench-testset.md); [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified) |
| **Runs** | 3 per document, per value |

| Dataset | `ocr.image.preprocessing` | Weighted accuracy | Documents with every field right | Total tokens per page |
|---|---|---|---|---|
| ConfBench | Off (default) | — | — | — |
| ConfBench | On | — | — | — |
| RealKIE | Off (default) | — | — | — |
| RealKIE | On | — | — | — |


#### DG-06: Which Textract features do I need?

**Answer:** Pick the features your documents need; none of the combinations we tried changed accuracy measurably. On RealKIE invoices and W-2 forms every combination scored within the noise of the default, and LAYOUT alone used about 3% fewer total tokens per page because it sends less page text. Textract prices each page by the features you select, so dropping a feature your documents do not need saves Textract charges rather than tokens.

*Measured on release 0.6.15.dev1, November 2026, us-east-1. Source: `Test Studio runs RealKIE-FCC-Verified-20261113-183155, RealKIE-FCC-Verified-20261113-183156, RealKIE-FCC-Verified-20261113-183157, RealKIE-FCC-Verified-20261113-183443, RealKIE-FCC-Verified-20261113-183516, RealKIE-FCC-Verified-20261113-183512, RealKIE-FCC-Verified-20261113-183741, RealKIE-FCC-Verified-20261113-183751, RealKIE-FCC-Verified-20261113-183840, RealKIE-FCC-Verified-20261113-184029, RealKIE-FCC-Verified-20261113-184136, RealKIE-FCC-Verified-20261113-184120, Fake-W2-Tax-Forms-20261113-184358, Fake-W2-Tax-Forms-20261113-184446, Fake-W2-Tax-Forms-20261113-184443, Fake-W2-Tax-Forms-20261113-184524, Fake-W2-Tax-Forms-20261113-184603, Fake-W2-Tax-Forms-20261113-184607, Fake-W2-Tax-Forms-20261113-184628, Fake-W2-Tax-Forms-20261113-184719, Fake-W2-Tax-Forms-20261113-184721, Fake-W2-Tax-Forms-20261113-184742, Fake-W2-Tax-Forms-20261113-184825, Fake-W2-Tax-Forms-20261113-184846`.*

| | |
|---|---|
| **Changes** | `ocr.features` |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [Fake-W2-Tax-Forms (W-2 forms, 45 fields)](../idp-fundamentals/benchmark-datasets.md#fake-w2-tax-forms); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document, per value |

| Dataset | `ocr.features` | Weighted accuracy | Total tokens per page |
|---|---|---|---|
| RealKIE | TABLES, LAYOUT, SIGNATURES (default) | 0.8 ± 0.06 | 20,870 ± 671 |
| RealKIE | LAYOUT only | 0.79 ± 0.07 | 19,457 ± 676 |
| RealKIE | TABLES only | 0.81 ± 0.06 | 21,293 ± 2,175 |
| RealKIE | TABLES, LAYOUT, SIGNATURES, FORMS | 0.79 ± 0.07 | 21,429 ± 2,720 |
| Fake-W2 | TABLES, LAYOUT, SIGNATURES (default) | 0.95 ± 0.02 | 15,195 ± 7.48 |
| Fake-W2 | LAYOUT only | 0.96 ± 0.02 | 14,705 ± 7.77 |
| Fake-W2 | TABLES only | 0.97 ± 0.01 | 15,178 ± 3.93 |
| Fake-W2 | TABLES, LAYOUT, SIGNATURES, FORMS | 0.97 ± 0.02 | 15,197 ± 1.59 |

| Dataset | `ocr.features` | Completeness | Cell accuracy | Total tokens per page |
|---|---|---|---|---|
| Statement, 400 rows | TABLES, LAYOUT, SIGNATURES (default) | — | — | — |
| Statement, 400 rows | LAYOUT only | — | — | — |
| Statement, 400 rows | TABLES only | — | — | — |
| Statement, 400 rows | TABLES, LAYOUT, SIGNATURES, FORMS | — | — | — |


#### DG-07: How much accuracy does scan quality cost?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Scan quality |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [ConfBench (RealKIE invoices with scan noise)](../extensions/confbench-testset.md) |
| **Runs** | 3 per document, per value |

| Dataset | Scan quality | Weighted accuracy | Documents with every field right | AUROC |
|---|---|---|---|---|
| ConfBench | Clean original | — | — | — |
| ConfBench | Light noise | — | — | — |
| ConfBench | Moderate noise | — | — | — |
| ConfBench | Heavy noise | — | — | — |


#### DG-08: Which reader handles handwriting best?

**Answer:** Not yet measured.

Needs a dataset we haven't built yet: Handwritten forms (to be built).

| | |
|---|---|
| **Changes** | OCR reader |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | Handwritten forms (to be built) |
| **Runs** | 3 per document, per value |

| Dataset | OCR reader | Weighted accuracy | Documents with every field right | Total tokens per page |
|---|---|---|---|---|
| Handwritten forms | Textract, tables and layout (default) | — | — | — |
| Handwritten forms | Bedrock vision model (Claude Sonnet 5) | — | — | — |
| Handwritten forms | Chandra (Lambda hook) | — | — | — |

<!-- END GENERATED ABLATIONS -->
