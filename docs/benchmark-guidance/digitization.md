---
title: "Digitization (OCR) Benchmarks"
---

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

# Digitization (OCR) Benchmarks

These ablations answer which OCR reader to use, at what resolution, and for which documents.
For how digitization works and how the accelerator reads each page, see
[Digitization (OCR)](../idp-fundamentals/digitization.md).

We measure digitization by its effect on the steps after it: every ablation scores
extraction against ground truth, so a better reader shows up as more accurate records in
your database. To shortlist readers on OCR alone, use public OCR benchmarks.

**Metrics on this page:** *weighted accuracy* is Stickler's field-weighted score against
ground truth; *documents with every field right* is the share of documents with no field
wrong; *completeness* and *cell accuracy* apply to the synthetic statements. See
[How to measure extraction](../idp-fundamentals/extraction.md).

Every ablation holds everything except the setting it changes at the
[baseline](index.md#the-baseline-every-ablation-starts-from).

<!-- BEGIN GENERATED ABLATIONS -->

### DG-01: Does the OCR reader make a difference to extraction accuracy?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | OCR reader |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [ConfBench (RealKIE invoices with scan noise)](../extensions/confbench-testset.md); [OmniAI-OCR-Benchmark, all 9 formats](../idp-fundamentals/benchmark-datasets.md#omniai-ocr-benchmark); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document per value |

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


### DG-02: If I read pages with a vision model, which model?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | Model used for Bedrock vision OCR |
| **Held fixed** | OCR reader set to the Bedrock vision model; everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [ConfBench (RealKIE invoices with scan noise)](../extensions/confbench-testset.md); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document per value |

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


### DG-03: Does a specialized OCR model beat Textract?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | OCR reader |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [ConfBench (RealKIE invoices with scan noise)](../extensions/confbench-testset.md); [OmniAI-OCR-Benchmark, all 9 formats](../idp-fundamentals/benchmark-datasets.md#omniai-ocr-benchmark) |
| **Runs** | 3 per document per value |

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


### DG-04: What resolution should pages be rendered at?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | `ocr.image.dpi` |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [ConfBench (RealKIE invoices with scan noise)](../extensions/confbench-testset.md); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document per value |

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


### DG-05: Does image preprocessing help on poor scans?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | `ocr.image.preprocessing` |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [ConfBench (RealKIE invoices with scan noise)](../extensions/confbench-testset.md); [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified) |
| **Runs** | 3 per document per value |

| Dataset | `ocr.image.preprocessing` | Weighted accuracy | Documents with every field right | Total tokens per page |
|---|---|---|---|---|
| ConfBench | Off (default) | — | — | — |
| ConfBench | On | — | — | — |
| RealKIE | Off (default) | — | — | — |
| RealKIE | On | — | — | — |


### DG-06: Which Textract features do I need?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | `ocr.features` |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [Fake-W2-Tax-Forms (W-2 forms, 45 fields)](../idp-fundamentals/benchmark-datasets.md#fake-w2-tax-forms); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document per value |

| Dataset | `ocr.features` | Weighted accuracy | Total tokens per page |
|---|---|---|---|
| RealKIE | TABLES, LAYOUT, SIGNATURES (default) | — | — |
| RealKIE | LAYOUT only | — | — |
| RealKIE | TABLES only | — | — |
| RealKIE | TABLES, LAYOUT, SIGNATURES, FORMS | — | — |
| Fake-W2 | TABLES, LAYOUT, SIGNATURES (default) | — | — |
| Fake-W2 | LAYOUT only | — | — |
| Fake-W2 | TABLES only | — | — |
| Fake-W2 | TABLES, LAYOUT, SIGNATURES, FORMS | — | — |

| Dataset | `ocr.features` | Completeness | Cell accuracy | Total tokens per page |
|---|---|---|---|---|
| Statement, 400 rows | TABLES, LAYOUT, SIGNATURES (default) | — | — | — |
| Statement, 400 rows | LAYOUT only | — | — | — |
| Statement, 400 rows | TABLES only | — | — | — |
| Statement, 400 rows | TABLES, LAYOUT, SIGNATURES, FORMS | — | — | — |


### DG-07: How much accuracy does scan quality cost?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | Scan quality |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [ConfBench (RealKIE invoices with scan noise)](../extensions/confbench-testset.md) |
| **Runs** | 3 per document per value |

| Dataset | Scan quality | Weighted accuracy | Documents with every field right | AUROC |
|---|---|---|---|---|
| ConfBench | Clean original | — | — | — |
| ConfBench | Light noise | — | — | — |
| ConfBench | Moderate noise | — | — | — |
| ConfBench | Heavy noise | — | — | — |


### DG-08: Which reader handles handwriting best?

**Verdict:** Not yet measured.

Needs a dataset that does not exist yet: Handwritten forms (to be built).

| | |
|---|---|
| **Changes** | OCR reader |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | Handwritten forms (to be built) |
| **Runs** | 3 per document per value |

| Dataset | OCR reader | Weighted accuracy | Documents with every field right | Total tokens per page |
|---|---|---|---|---|
| Handwritten forms | Textract, tables and layout (default) | — | — | — |
| Handwritten forms | Bedrock vision model (Claude Sonnet 5) | — | — | — |
| Handwritten forms | Chandra (Lambda hook) | — | — | — |

<!-- END GENERATED ABLATIONS -->
