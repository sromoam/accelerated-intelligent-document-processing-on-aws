---
title: "Confidence Assessment Benchmarks"
---

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

# Confidence Assessment Benchmarks

These ablations answer whether confidence scores can decide which results a person reviews,
which scoring model to use, and which threshold to set. For how the accelerator assigns
confidence, see [Confidence Assessment](../idp-fundamentals/confidence-assessment.md).

Measuring confidence needs documents on which extraction makes mistakes, so these
ablations rely on [ConfBench](../extensions/confbench-testset.md), which adds scan noise to
real invoices without changing their ground truth.

**Metrics on this page:**

- *AUROC:* the probability that a wrong value scores lower than a right one. 0.5 is chance.
- *Calibration error:* how far the scores are from the observed accuracy.
- *Values below threshold:* the share of values a threshold sends to review.
- *Errors below threshold:* the share of wrong values that the threshold sends to review.

Every ablation holds everything except the setting it changes at the
[baseline](index.md#the-baseline-every-ablation-starts-from).

<!-- BEGIN GENERATED ABLATIONS -->

### CF-01: Can I route human review by confidence?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | Scoring model |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [ConfBench (RealKIE invoices with scan noise)](../extensions/confbench-testset.md); [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document per value |

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


### CF-02: Which scoring model should I use?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | Scoring model |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [ConfBench (RealKIE invoices with scan noise)](../extensions/confbench-testset.md); [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified) |
| **Runs** | 3 per document per value |

| Dataset | Scoring model | AUROC | Calibration error | Values below threshold | Errors below threshold | Scoring tokens per page |
|---|---|---|---|---|---|---|
| ConfBench | Amazon Nova Lite (default) | — | — | — | — | — |
| ConfBench | Amazon Nova 2 Lite | — | — | — | — | — |
| ConfBench | Claude Haiku 5.5 | — | — | — | — | — |
| ConfBench | Claude Sonnet 5 | — | — | — | — | — |
| RealKIE | Amazon Nova Lite (default) | — | — | — | — | — |
| RealKIE | Amazon Nova 2 Lite | — | — | — | — | — |
| RealKIE | Claude Haiku 5.5 | — | — | — | — | — |
| RealKIE | Claude Sonnet 5 | — | — | — | — | — |


### CF-03: Separate scoring pass or integrated into extraction?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | Confidence mode |
| **Held fixed** | Run in both extraction modes; everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [ConfBench (RealKIE invoices with scan noise)](../extensions/confbench-testset.md); [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [Synthetic statement, 800 rows (17 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document per value |

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


### CF-04: What confidence threshold should I set?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | Confidence threshold |
| **Held fixed** | Computed from the CF-02 runs, per scoring model; everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [ConfBench (RealKIE invoices with scan noise)](../extensions/confbench-testset.md); [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified) |
| **Runs** | No new runs: computed from the CF-02 runs |

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


### CF-05: Does classification confidence flag the wrong document class?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | Classification model |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq) |
| **Runs** | 3 per document per value |

| Dataset | Classification model | Label accuracy | AUROC | Values below threshold | Errors below threshold | Classification tokens per page |
|---|---|---|---|---|---|---|
| DocSplit | Amazon Nova 2 Lite (default) | — | — | — | — | — |
| DocSplit | Claude Haiku 5.5 | — | — | — | — | — |
| DocSplit | Claude Sonnet 5 | — | — | — | — | — |


### CF-06: Does the scoring model need page images?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | Page images in the scoring prompt |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [ConfBench (RealKIE invoices with scan noise)](../extensions/confbench-testset.md); [Fake-W2-Tax-Forms (W-2 forms, 45 fields)](../idp-fundamentals/benchmark-datasets.md#fake-w2-tax-forms) |
| **Runs** | 3 per document per value |

| Dataset | Page images in the scoring prompt | AUROC | Calibration error | Scoring tokens per page |
|---|---|---|---|---|
| ConfBench | Text and images (default) | — | — | — |
| ConfBench | Text only | — | — | — |
| Fake-W2 | Text and images (default) | — | — | — |
| Fake-W2 | Text only | — | — | — |


### CF-07: How should long lists be scored?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | `extraction.confidence.list_batch_size` |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements); [Synthetic statement, 800 rows (17 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements); [Synthetic statement, 1,600 rows (33 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document per value |

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
