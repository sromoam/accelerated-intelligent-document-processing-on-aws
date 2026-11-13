---
title: "Confidence Assessment Benchmarks"
tableOfContents:
  maxHeadingLevel: 3
---

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

# Confidence Assessment Benchmarks

Confidence assessment gives every extracted value a score, so a person reviews the values
most likely to be wrong instead of every value.
[Confidence Assessment](../idp-fundamentals/confidence-assessment.md) explains how it works.

## How to improve confidence on your documents

**Your definitions.** The scoring model reads each field's description when it judges a
value. Say what a right value looks like. Mark the fields you can't do without as required:
an empty required field goes to review even though it has no score. See
[Improving confidence](../idp-fundamentals/confidence-assessment.md#improving-confidence-once-your-pipeline-is-running).

**Data quality.** Poor scans cause more extraction mistakes, and catching those mistakes is
the job confidence does. We measure it on [ConfBench](../extensions/confbench-testset.md),
which adds scan noise to real invoices.

**Settings.**

| Setting | What it changes | Questions |
|---|---|---|
| Scoring mode | A separate scoring pass, scores inside the extraction call, or none | [CF-03](#separate-scoring-pass-or-integrated-into-extraction) |
| Scoring model | The model that scores each value | [CF-02](#which-scoring-model-should-i-use) |
| Confidence threshold | The score below which a value goes to review | [CF-01](#can-i-route-human-review-by-confidence), [CF-04](#what-confidence-threshold-should-i-set) |
| Page images | Whether the scoring model sees the pages | [CF-06](#does-the-scoring-model-need-page-images) |
| List batch size | How many list rows the scoring model scores in one request | [CF-07](#how-should-long-lists-be-scored) |

## Benchmark datasets and metrics

<!-- BEGIN GENERATED DATASETS -->

| Dataset | Preset |
|---|---|
| [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) | `bank-statement-sample` |
| [Synthetic statement, 800 rows (17 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) | `bank-statement-sample` |
| [Synthetic statement, 1,600 rows (33 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) | `bank-statement-sample` |
| [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified) | `realkie-fcc-verified` |
| [ConfBench (RealKIE invoices with scan noise)](../extensions/confbench-testset.md) | `realkie-fcc-verified` |
| [Fake-W2-Tax-Forms (W-2 forms, 45 fields)](../idp-fundamentals/benchmark-datasets.md#fake-w2-tax-forms) | `fake-w2` |
| [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq) | `docsplit` |

<!-- END GENERATED DATASETS -->

**Metrics**

- *AUROC:* the chance that a wrong value scores lower than a right one. 0.5 is a coin flip.
- *Calibration error:* the gap between the scores and the measured accuracy.
- *Values below threshold:* the share of values the threshold sends to review.
- *Errors below threshold:* the share of wrong values the threshold sends to review.

## Questions

<!-- BEGIN GENERATED FAQ -->

### Can I route human review by confidence?

**Answer:** Not yet measured. [Details: CF-01](#cf-01-can-i-route-human-review-by-confidence)

### Which scoring model should I use?

**Answer:** Use Claude Haiku 5.5 or Claude Sonnet 5 when people review by confidence. On RealKIE invoices they separated right values from wrong ones (AUROC 0.81 and 0.83) at about the same scoring tokens per page as the default, Amazon Nova Lite, which scored 0.42: no better than a coin flip. [Details: CF-02](#cf-02-which-scoring-model-should-i-use)

![AUROC against scoring tokens per page for each Scoring model](../../images/benchmark-guidance/CF-02-fields.svg)

*AUROC against scoring tokens per page. Each point is one value of the setting; lines span two standard errors either side. Up and to the left is better.*

### Separate scoring pass or integrated into extraction?

**Answer:** Not yet measured. [Details: CF-03](#cf-03-separate-scoring-pass-or-integrated-into-extraction)

### What confidence threshold should I set?

**Answer:** Not yet measured. [Details: CF-04](#cf-04-what-confidence-threshold-should-i-set)

### Does classification confidence flag the wrong document class?

**Answer:** Not yet measured. [Details: CF-05](#cf-05-does-classification-confidence-flag-the-wrong-document-class)

### Does the scoring model need page images?

**Answer:** Not yet measured. [Details: CF-06](#cf-06-does-the-scoring-model-need-page-images)

### How should long lists be scored?

**Answer:** Not yet measured. [Details: CF-07](#cf-07-how-should-long-lists-be-scored)

<!-- END GENERATED FAQ -->

## Benchmark details

<!-- BEGIN GENERATED ABLATIONS -->

#### CF-01: Can I route human review by confidence?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Scoring model |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [ConfBench (RealKIE invoices with scan noise)](../extensions/confbench-testset.md); [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document, per value |

| Dataset | Scoring model | AUROC | Calibration error | Values below threshold | Errors below threshold |
|---|---|---|---|---|---|
| ConfBench | Amazon Nova Lite (default) | — | — | — | — |
| ConfBench | Claude Sonnet 5 | — | — | — | — |
| RealKIE | Amazon Nova Lite (default) | — | — | — | — |
| RealKIE | Claude Sonnet 5 | — | — | — | — |

| Dataset | Scoring model | AUROC | Calibration error | Values below threshold | Errors below threshold |
|---|---|---|---|---|---|
| Statement, 400 rows | Amazon Nova Lite (default) | — | — | — | — |
| Statement, 400 rows | Claude Sonnet 5 | — | — | — | — |


#### CF-02: Which scoring model should I use?

**Answer:** Use Claude Haiku 5.5 or Claude Sonnet 5 when people review by confidence. On RealKIE invoices they separated right values from wrong ones (AUROC 0.81 and 0.83) at about the same scoring tokens per page as the default, Amazon Nova Lite, which scored 0.42: no better than a coin flip.

*Measured on release 0.6.15.dev1, November 2026, us-east-1. Source: `Test Studio runs RealKIE-FCC-Verified-20261113-181724, RealKIE-FCC-Verified-20261113-181722, RealKIE-FCC-Verified-20261113-181723, RealKIE-FCC-Verified-20261113-182034, RealKIE-FCC-Verified-20261113-182041, RealKIE-FCC-Verified-20261113-182113, RealKIE-FCC-Verified-20261113-182352, RealKIE-FCC-Verified-20261113-182430, RealKIE-FCC-Verified-20261113-182432, RealKIE-FCC-Verified-20261113-182712, RealKIE-FCC-Verified-20261113-182736, RealKIE-FCC-Verified-20261113-182750`.*

| | |
|---|---|
| **Changes** | Scoring model |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [ConfBench (RealKIE invoices with scan noise)](../extensions/confbench-testset.md); [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified) |
| **Runs** | 3 per document, per value |

| Dataset | Scoring model | AUROC | Calibration error | Values below threshold | Errors below threshold | Scoring tokens per page |
|---|---|---|---|---|---|---|
| ConfBench | Amazon Nova Lite (default) | — | — | — | — | — |
| ConfBench | Amazon Nova 2 Lite | — | — | — | — | — |
| ConfBench | Claude Haiku 5.5 | — | — | — | — | — |
| ConfBench | Claude Sonnet 5 | — | — | — | — | — |
| RealKIE | Amazon Nova Lite (default) | 0.42 ± 0.07 | 0.17 ± 0.02 | — | — | 14,079 ± 166 |
| RealKIE | Amazon Nova 2 Lite | 0.61 ± 0.13 | 0.18 ± 0.05 | — | — | 5,290 ± 331 |
| RealKIE | Claude Haiku 5.5 | 0.81 ± 0.07 | 0.1 ± 0.03 | — | — | 13,193 ± 1,006 |
| RealKIE | Claude Sonnet 5 | 0.83 ± 0.03 | 0.09 ± 0.05 | — | — | 12,025 ± 93 |


#### CF-03: Separate scoring pass or integrated into extraction?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Confidence mode |
| **Everything else** | Single-pass (Simple) extraction; the rest as each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [ConfBench (RealKIE invoices with scan noise)](../extensions/confbench-testset.md); [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [Synthetic statement, 800 rows (17 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document, per value |

| Dataset | Confidence mode | Weighted accuracy | AUROC | Scoring tokens per page | Median seconds per document |
|---|---|---|---|---|---|
| ConfBench | Separate (default) | — | — | — | — |
| ConfBench | Integrated | — | — | — | — |
| ConfBench | Off | — | — | — | — |
| RealKIE | Separate (default) | — | — | — | — |
| RealKIE | Integrated | — | — | — | — |
| RealKIE | Off | — | — | — | — |

| Dataset | Confidence mode | Completeness | AUROC | Scoring tokens per page | Median seconds per document |
|---|---|---|---|---|---|
| Statement, 800 rows | Separate (default) | — | — | — | — |
| Statement, 800 rows | Integrated | — | — | — | — |
| Statement, 800 rows | Off | — | — | — | — |


#### CF-04: What confidence threshold should I set?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Confidence threshold |
| **Everything else** | Computed from the CF-02 runs, per scoring model; the rest as each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [ConfBench (RealKIE invoices with scan noise)](../extensions/confbench-testset.md); [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified) |
| **Runs** | None: computed from the CF-02 runs |

| Dataset | Confidence threshold | Values below threshold | Errors below threshold |
|---|---|---|---|
| ConfBench | 0.5 | — | — |
| ConfBench | 0.7 | — | — |
| ConfBench | 0.8 (default) | — | — |
| ConfBench | 0.9 | — | — |
| ConfBench | 0.95 | — | — |
| RealKIE | 0.5 | — | — |
| RealKIE | 0.7 | — | — |
| RealKIE | 0.8 (default) | — | — |
| RealKIE | 0.9 | — | — |
| RealKIE | 0.95 | — | — |


#### CF-05: Does classification confidence flag the wrong document class?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Classification model |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq) |
| **Runs** | 3 per document, per value |

| Dataset | Classification model | Label accuracy | AUROC | Values below threshold | Errors below threshold | Classification tokens per page |
|---|---|---|---|---|---|---|
| DocSplit | Amazon Nova 2 Lite (default) | — | — | — | — | — |
| DocSplit | Claude Haiku 5.5 | — | — | — | — | — |
| DocSplit | Claude Sonnet 5 | — | — | — | — | — |


#### CF-06: Does the scoring model need page images?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Page images in the scoring prompt |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [ConfBench (RealKIE invoices with scan noise)](../extensions/confbench-testset.md); [Fake-W2-Tax-Forms (W-2 forms, 45 fields)](../idp-fundamentals/benchmark-datasets.md#fake-w2-tax-forms) |
| **Runs** | 3 per document, per value |

| Dataset | Page images in the scoring prompt | AUROC | Calibration error | Scoring tokens per page |
|---|---|---|---|---|
| ConfBench | Text and images (default) | — | — | — |
| ConfBench | Text only | — | — | — |
| Fake-W2 | Text and images (default) | — | — | — |
| Fake-W2 | Text only | — | — | — |


#### CF-07: How should long lists be scored?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | `extraction.confidence.list_batch_size` |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements); [Synthetic statement, 800 rows (17 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements); [Synthetic statement, 1,600 rows (33 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document, per value |

| Dataset | `extraction.confidence.list_batch_size` | Completeness | AUROC | Scoring tokens per page | Median seconds per document |
|---|---|---|---|---|---|
| Statement, 400 rows | 25 (default) | — | — | — | — |
| Statement, 400 rows | 12 | — | — | — | — |
| Statement, 400 rows | 50 | — | — | — | — |
| Statement, 800 rows | 25 (default) | — | — | — | — |
| Statement, 800 rows | 12 | — | — | — | — |
| Statement, 800 rows | 50 | — | — | — | — |
| Statement, 1,600 rows | 25 (default) | — | — | — | — |
| Statement, 1,600 rows | 12 | — | — | — | — |
| Statement, 1,600 rows | 50 | — | — | — | — |

<!-- END GENERATED ABLATIONS -->
