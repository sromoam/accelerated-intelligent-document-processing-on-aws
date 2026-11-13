---
title: "Splitting and Section Classification Benchmarks"
---

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

# Splitting and Section Classification Benchmarks

- Help me choose a mechanism for packet splitting.
- Do I need page images in the classification prompt?
- Which classification model should I use?
- How long a packet can holistic classification handle?

[Splitting and Section Classification](../idp-fundamentals/splitting-and-classification.md)
explains how the accelerator finds and classifies the documents in a file.

**Metrics**

- *Page accuracy:* the share of pages with the right document class.
- *Boundary accuracy:* the share of sections with exactly the right page range. The
  document class is not checked.
- *Label accuracy:* of the sections with the right page range, the share with the right
  document class.
- *Over-splits:* documents cut into more than one section.
- *Merges:* sections that join more than one document.

## Benchmarks

<!-- BEGIN GENERATED ABLATIONS -->

### SC-01: Help me choose a mechanism for packet splitting.

**Answer:** Not yet measured.

Needs a dataset we haven't built yet: Same-class documents back to back (to be built).

| | |
|---|---|
| **Changes** | Granularity and strategy |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq); [Synthetic file holding two statements](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements); Same-class documents back to back (to be built) |
| **Runs** | 3 per document, per value |

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

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | What the classification model reads |
| **Everything else** | Run at both granularities: page by page and holistic; the rest as each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq) |
| **Runs** | 3 per document, per value |

| Dataset | What the classification model reads | Page accuracy | Boundary accuracy | Label accuracy | Classification tokens per page |
|---|---|---|---|---|---|
| DocSplit | Text and images (default) | — | — | — | — |
| DocSplit | Text only | — | — | — | — |
| DocSplit | Images only | — | — | — | — |


### SC-03: Which classification model should I use?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Classification model |
| **Everything else** | Run at both granularities: page by page and holistic; the rest as each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq) |
| **Runs** | 3 per document, per value |

| Dataset | Classification model | Page accuracy | Boundary accuracy | Label accuracy | Classification tokens per page | Median seconds per document |
|---|---|---|---|---|---|---|
| DocSplit | Amazon Nova 2 Lite (default) | — | — | — | — | — |
| DocSplit | Amazon Nova Pro | — | — | — | — | — |
| DocSplit | Claude Haiku 5.5 | — | — | — | — | — |
| DocSplit | Claude Sonnet 5 | — | — | — | — | — |


### SC-04: How long a packet can holistic classification handle?

**Answer:** Not yet measured.

Needs a dataset we haven't built yet: Long packets, 30-60 pages (to be built).

| | |
|---|---|
| **Changes** | Pages per holistic call (`window_pages`) |
| **Everything else** | Holistic, one call; the rest as each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | Long packets, 30-60 pages (to be built); [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq) |
| **Runs** | 3 per document, per value |

| Dataset | Pages per holistic call (`window_pages`) | Page accuracy | Boundary accuracy | Label accuracy | Classification tokens per page |
|---|---|---|---|---|---|
| Long packets | 20 (default) | — | — | — | — |
| Long packets | 10 | — | — | — | — |
| Long packets | 40 | — | — | — | — |
| DocSplit | 20 (default) | — | — | — | — |
| DocSplit | 10 | — | — | — | — |
| DocSplit | 40 | — | — | — | — |


### SC-05: Does neighboring-page context help page-by-page classification?

**Answer:** Not yet measured.

Needs a dataset we haven't built yet: Same-class documents back to back (to be built).

| | |
|---|---|
| **Changes** | `contextPagesCount` |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq); Same-class documents back to back (to be built) |
| **Runs** | 3 per document, per value |

| Dataset | `contextPagesCount` | Boundary accuracy | Label accuracy | Over-splits | Merges | Classification tokens per page |
|---|---|---|---|---|---|---|
| DocSplit | 0 (default) | — | — | — | — | — |
| DocSplit | 1 | — | — | — | — | — |
| DocSplit | 2 | — | — | — | — | — |
| Same-class packets | 0 (default) | — | — | — | — | — |
| Same-class packets | 1 | — | — | — | — | — |
| Same-class packets | 2 | — | — | — | — | — |


### SC-06: Do few-shot examples help classification?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Few-shot examples |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq) |
| **Runs** | 3 per document, per value |

| Dataset | Few-shot examples | Page accuracy | Label accuracy | Classification tokens per page |
|---|---|---|---|---|
| DocSplit | None (default) | — | — | — |
| DocSplit | One example per class | — | — | — |
| DocSplit | Two examples per class | — | — | — |


### SC-07: How much do class descriptions matter?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Class descriptions |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq) |
| **Runs** | 3 per document, per value |

| Dataset | Class descriptions | Page accuracy | Label accuracy |
|---|---|---|---|
| DocSplit | Class names only | — | — |
| DocSplit | Generic descriptions | — | — |
| DocSplit | Descriptions that name distinguishing features | — | — |


### SC-08: Does accuracy drop as I add document classes?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Number of document classes in the configuration |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq) |
| **Runs** | 3 per document, per value |

| Dataset | Number of document classes in the configuration | Page accuracy | Label accuracy | Classification tokens per page |
|---|---|---|---|---|
| DocSplit | 5 | — | — | — |
| DocSplit | 13 | — | — | — |
| DocSplit | 30 (13 plus 17 distractor classes) | — | — | — |


### SC-09: How small can classification images be?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Classification image size (long edge) |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq) |
| **Runs** | 3 per document, per value |

| Dataset | Classification image size (long edge) | Page accuracy | Boundary accuracy | Classification tokens per page |
|---|---|---|---|---|
| DocSplit | As rendered (default) | — | — | — |
| DocSplit | 1,024 pixels | — | — | — |
| DocSplit | 512 pixels | — | — | — |


### SC-10: If every file is one document, should I turn splitting off?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Section splitting |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements); [Synthetic statement, 800 rows (17 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document, per value |

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
