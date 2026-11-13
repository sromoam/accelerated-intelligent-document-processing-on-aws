---
title: "Splitting and Section Classification Benchmarks"
---

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

# Splitting and Section Classification Benchmarks

These ablations answer how to find and classify the documents in a file: which mechanism,
whether to send page images, which classification model, and how long a packet the
accelerator can handle. For how section detection and classification work, see
[Splitting and Section Classification](../idp-fundamentals/splitting-and-classification.md).

**Metrics on this page:**

- *Page accuracy:* the share of pages that received the right document class.
- *Boundary accuracy:* the share of true sections that came back with exactly the right
  page range. The document class is not checked.
- *Label accuracy:* of the sections with the right page range, the share that also received
  the right document class.
- *Over-splits* and *merges:* the number of documents cut into several sections, and the
  number of sections that join several documents.

See [How to measure section detection and classification](../idp-fundamentals/splitting-and-classification.md#how-to-measure-section-detection-and-classification-on-your-own-files).

Every ablation holds everything except the setting it changes at the
[baseline](index.md#the-baseline-every-ablation-starts-from).

<!-- BEGIN GENERATED ABLATIONS -->

### SC-01: Help me choose a mechanism for packet splitting.

**Verdict:** Not yet measured.

Needs a dataset that does not exist yet: Same-class documents back to back (to be built).

| | |
|---|---|
| **Changes** | Granularity and strategy |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq); [Synthetic file holding two statements](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements); Same-class documents back to back (to be built) |
| **Runs** | 3 per document per value |

| Dataset | Granularity and strategy | Page accuracy | Boundary accuracy | Label accuracy | Over-splits | Merges | Classification tokens per page |
|---|---|---|---|---|---|---|---|
| DocSplit | Page by page, one call (default) | — | — | — | — | — | — |
| DocSplit | Holistic, one call | — | — | — | — | — | — |
| DocSplit | Detect sections first (page by page), then classify | — | — | — | — | — | — |
| DocSplit | Detect sections first (holistic), then classify | — | — | — | — | — | — |
| Two statements in one file | Page by page, one call (default) | — | — | — | — | — | — |
| Two statements in one file | Holistic, one call | — | — | — | — | — | — |
| Two statements in one file | Detect sections first (page by page), then classify | — | — | — | — | — | — |
| Two statements in one file | Detect sections first (holistic), then classify | — | — | — | — | — | — |
| Same-class packets | Page by page, one call (default) | — | — | — | — | — | — |
| Same-class packets | Holistic, one call | — | — | — | — | — | — |
| Same-class packets | Detect sections first (page by page), then classify | — | — | — | — | — | — |
| Same-class packets | Detect sections first (holistic), then classify | — | — | — | — | — | — |


### SC-02: Do I need page images in the classification prompt?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | What the classification model reads |
| **Held fixed** | Run at both granularities: page by page and holistic; everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq) |
| **Runs** | 3 per document per value |

| Dataset | What the classification model reads | Page accuracy | Boundary accuracy | Label accuracy | Classification tokens per page |
|---|---|---|---|---|---|
| DocSplit | Text and images (default) | — | — | — | — |
| DocSplit | Text only | — | — | — | — |
| DocSplit | Images only | — | — | — | — |


### SC-03: Which classification model should I use?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | Classification model |
| **Held fixed** | Run at both granularities: page by page and holistic; everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq) |
| **Runs** | 3 per document per value |

| Dataset | Classification model | Page accuracy | Boundary accuracy | Label accuracy | Classification tokens per page | Median seconds per document |
|---|---|---|---|---|---|---|
| DocSplit | Amazon Nova 2 Lite (default) | — | — | — | — | — |
| DocSplit | Amazon Nova Pro | — | — | — | — | — |
| DocSplit | Claude Haiku 5.5 | — | — | — | — | — |
| DocSplit | Claude Sonnet 5 | — | — | — | — | — |


### SC-04: How long a packet can holistic classification handle?

**Verdict:** Not yet measured.

Needs a dataset that does not exist yet: Long packets, 30-60 pages (to be built).

| | |
|---|---|
| **Changes** | Pages per holistic call (`window_pages`) |
| **Held fixed** | Holistic, one call; everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | Long packets, 30-60 pages (to be built); [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq) |
| **Runs** | 3 per document per value |

| Dataset | Pages per holistic call (`window_pages`) | Page accuracy | Boundary accuracy | Label accuracy | Classification tokens per page |
|---|---|---|---|---|---|
| Long packets | 20 (default) | — | — | — | — |
| Long packets | 10 | — | — | — | — |
| Long packets | 40 | — | — | — | — |
| DocSplit | 20 (default) | — | — | — | — |
| DocSplit | 10 | — | — | — | — |
| DocSplit | 40 | — | — | — | — |


### SC-05: Does neighboring-page context help page-by-page classification?

**Verdict:** Not yet measured.

Needs a dataset that does not exist yet: Same-class documents back to back (to be built).

| | |
|---|---|
| **Changes** | `contextPagesCount` |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq); Same-class documents back to back (to be built) |
| **Runs** | 3 per document per value |

| Dataset | `contextPagesCount` | Boundary accuracy | Label accuracy | Over-splits | Merges | Classification tokens per page |
|---|---|---|---|---|---|---|
| DocSplit | 0 (default) | — | — | — | — | — |
| DocSplit | 1 | — | — | — | — | — |
| DocSplit | 2 | — | — | — | — | — |
| Same-class packets | 0 (default) | — | — | — | — | — |
| Same-class packets | 1 | — | — | — | — | — |
| Same-class packets | 2 | — | — | — | — | — |


### SC-06: Do few-shot examples help classification?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | Few-shot examples |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq) |
| **Runs** | 3 per document per value |

| Dataset | Few-shot examples | Page accuracy | Label accuracy | Classification tokens per page |
|---|---|---|---|---|
| DocSplit | None (default) | — | — | — |
| DocSplit | One example per class | — | — | — |
| DocSplit | Two examples per class | — | — | — |


### SC-07: How much do class descriptions matter?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | Class descriptions |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq) |
| **Runs** | 3 per document per value |

| Dataset | Class descriptions | Page accuracy | Label accuracy |
|---|---|---|---|
| DocSplit | Class names only | — | — |
| DocSplit | Generic descriptions | — | — |
| DocSplit | Descriptions that name distinguishing features | — | — |


### SC-08: Does accuracy drop as I add document classes?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | Number of document classes in the configuration |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq) |
| **Runs** | 3 per document per value |

| Dataset | Number of document classes in the configuration | Page accuracy | Label accuracy | Classification tokens per page |
|---|---|---|---|---|
| DocSplit | 5 | — | — | — |
| DocSplit | 13 | — | — | — |
| DocSplit | 30 (13 plus 17 distractor classes) | — | — | — |


### SC-09: How small can classification images be?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | Classification image size (long edge) |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq) |
| **Runs** | 3 per document per value |

| Dataset | Classification image size (long edge) | Page accuracy | Boundary accuracy | Classification tokens per page |
|---|---|---|---|---|
| DocSplit | As rendered (default) | — | — | — |
| DocSplit | 1,024 pixels | — | — | — |
| DocSplit | 512 pixels | — | — | — |


### SC-10: If every file is one document, should I turn splitting off?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | Section splitting |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements); [Synthetic statement, 800 rows (17 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document per value |

| Dataset | Section splitting | Weighted accuracy | Classification tokens per page |
|---|---|---|---|
| RealKIE | Model decides (default) | — | — |
| RealKIE | One section | — | — |

| Dataset | Section splitting | Completeness | Classification tokens per page |
|---|---|---|---|
| Statement, 400 rows | Model decides (default) | — | — |
| Statement, 400 rows | One section | — | — |
| Statement, 800 rows | Model decides (default) | — | — |
| Statement, 800 rows | One section | — | — |

<!-- END GENERATED ABLATIONS -->
