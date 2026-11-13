---
title: "Splitting and Section Classification Benchmarks"
tableOfContents:
  maxHeadingLevel: 3
---

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

# Splitting and Section Classification Benchmarks

Splitting finds where each document in a file starts and ends, and classification gives each
of those sections a document class.
[Splitting and Section Classification](../idp-fundamentals/splitting-and-classification.md) explains how it
works.

## How to improve splitting and classification on your documents

**Your definitions.** The classification model picks a document class by comparing each
section with the description of every document class. Name the features that tell a class
apart from its closest neighbor. For classes that still get confused, add a few-shot example.
See [Improving accuracy](../idp-fundamentals/splitting-and-classification.md#improving-accuracy-once-your-pipeline-is-running).

**Data quality.** Long files, documents of the same class back to back, and pages that match
no class are the hard cases. Poor scans hide the headers and page numbers the model uses to
find where a document starts.

**Settings.**

| Setting | What it changes | Questions |
|---|---|---|
| Granularity and strategy | Page by page or the whole file at once, in one call or with section detection first | [SC-01](#help-me-choose-a-mechanism-for-packet-splitting) |
| What the model reads | Page text, page images, or both | [SC-02](#do-i-need-page-images-in-the-classification-prompt), [SC-09](#how-small-can-classification-images-be) |
| Classification model | The model that reads the pages | [SC-03](#which-classification-model-should-i-use) |
| Window size | How many pages a holistic call sees at once | [SC-04](#how-long-a-packet-can-holistic-classification-handle) |
| Context pages | Neighboring pages sent with each page, page by page | [SC-05](#does-neighboring-page-context-help-page-by-page-classification) |
| Few-shot examples | Sample pages with their correct class, added to the prompt | [SC-06](#do-few-shot-examples-help-classification) |
| Section splitting | Detect sections, or keep every file as one section | [SC-10](#if-every-file-is-one-document-should-i-turn-splitting-off) |

## Benchmark datasets and metrics

<!-- BEGIN GENERATED DATASETS -->

| Dataset | Preset |
|---|---|
| [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) | `bank-statement-sample` |
| [Synthetic statement, 800 rows (17 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) | `bank-statement-sample` |
| [Synthetic file holding two statements](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) | `bank-statement-sample` |
| [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified) | `realkie-fcc-verified` |
| [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq) | `docsplit` |
| Long packets, 30-60 pages (to be built) | — |
| Same-class documents back to back (to be built) | — |

<!-- END GENERATED DATASETS -->

**Metrics**

- *Page accuracy:* the share of pages with the right document class.
- *Section accuracy:* the share of true sections returned with exactly the right pages and
  the right document class.
- *Grouping score:* how well the accelerator groups pages into documents, from 0 to 1,
  whatever their class. It is DocSplit's packet score, which combines how pages are
  clustered and how they are ordered.
- *Boundary accuracy:* the share of sections with exactly the right page range. The
  document class is not checked.
- *Label accuracy:* of the sections with the right page range, the share with the right
  document class.

## Questions

<!-- BEGIN GENERATED FAQ -->

### Help me choose a mechanism for packet splitting.

**Answer:** On DocSplit packets, detect sections first, page by page. It got the most sections exactly right (0.65, against 0.52 for the default) and kept the default's page accuracy (0.81) at the same tokens per page. Holistic classification grouped pages into documents best (grouping score 0.90) and used about 20% fewer tokens, but gave the wrong class to more pages (page accuracy 0.70): choose it when finding where each document starts matters more than its class. [Details: SC-01](#sc-01-help-me-choose-a-mechanism-for-packet-splitting)

![Section accuracy against total tokens per page for each Granularity and strategy](../../images/benchmark-guidance/SC-01-packet.svg)

*Section accuracy against total tokens per page. Each point is one value of the setting; lines span two standard errors either side. Up and to the left is better.*

### Do I need page images in the classification prompt?

**Answer:** Not yet measured. [Details: SC-02](#sc-02-do-i-need-page-images-in-the-classification-prompt)

### Which classification model should I use?

**Answer:** Not yet measured. [Details: SC-03](#sc-03-which-classification-model-should-i-use)

### How long a packet can holistic classification handle?

**Answer:** Not yet measured. [Details: SC-04](#sc-04-how-long-a-packet-can-holistic-classification-handle)

### Does neighboring-page context help page-by-page classification?

**Answer:** Not yet measured. [Details: SC-05](#sc-05-does-neighboring-page-context-help-page-by-page-classification)

### Do few-shot examples help classification?

**Answer:** Not yet measured. [Details: SC-06](#sc-06-do-few-shot-examples-help-classification)

### How much do class descriptions matter?

**Answer:** Not yet measured. [Details: SC-07](#sc-07-how-much-do-class-descriptions-matter)

### Does accuracy drop as I add document classes?

**Answer:** Not yet measured. [Details: SC-08](#sc-08-does-accuracy-drop-as-i-add-document-classes)

### How small can classification images be?

**Answer:** Not yet measured. [Details: SC-09](#sc-09-how-small-can-classification-images-be)

### If every file is one document, should I turn splitting off?

**Answer:** Not yet measured. [Details: SC-10](#sc-10-if-every-file-is-one-document-should-i-turn-splitting-off)

<!-- END GENERATED FAQ -->

## Benchmark details

<!-- BEGIN GENERATED ABLATIONS -->

#### SC-01: Help me choose a mechanism for packet splitting.

**Answer:** On DocSplit packets, detect sections first, page by page. It got the most sections exactly right (0.65, against 0.52 for the default) and kept the default's page accuracy (0.81) at the same tokens per page. Holistic classification grouped pages into documents best (grouping score 0.90) and used about 20% fewer tokens, but gave the wrong class to more pages (page accuracy 0.70): choose it when finding where each document starts matters more than its class.

*Measured on release 0.6.15.dev1, November 2026, us-east-1. Source: `Test Studio runs DocSplit-Poly-Seq-20261113-192327, DocSplit-Poly-Seq-20261113-192328, DocSplit-Poly-Seq-20261113-192329, DocSplit-Poly-Seq-20261113-192706, DocSplit-Poly-Seq-20261113-192708, DocSplit-Poly-Seq-20261113-192711, DocSplit-Poly-Seq-20261113-194400, DocSplit-Poly-Seq-20261113-194401, DocSplit-Poly-Seq-20261113-194402, DocSplit-Poly-Seq-20261113-195220, DocSplit-Poly-Seq-20261113-195216, DocSplit-Poly-Seq-20261113-195221 (4 failed documents left out of the scores)`.*

Needs a dataset we haven't built yet: Same-class documents back to back (to be built).

| | |
|---|---|
| **Changes** | Granularity and strategy |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq); [Synthetic file holding two statements](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements); Same-class documents back to back (to be built) |
| **Runs** | 3 per document, per value |

| Dataset | Granularity and strategy | Page accuracy | Section accuracy | Grouping score | Boundary accuracy | Label accuracy | Classification tokens per page | Total tokens per page |
|---|---|---|---|---|---|---|---|---|
| DocSplit | Page by page, one call (default) | 0.82 ± 0.02 | 0.52 ± 0.02 | 0.66 ± 0.02 | — | — | 2,859 ± 16 | 14,822 ± 58 |
| DocSplit | Holistic, one call | 0.7 ± 0.03 | 0.55 ± 0.05 | 0.9 ± 0.01 | — | — | 1,133 ± 0.65 | 11,857 ± 96 |
| DocSplit | Detect sections first (page by page), then classify | 0.81 ± 0.02 | 0.65 ± 0.01 | 0.8 ± 0.01 | — | — | 2,821 ± 28 | 14,408 ± 116 |
| DocSplit | Detect sections first (holistic), then classify | 0.76 ± 0.02 | 0.55 ± 0.04 | 0.9 ± 0.01 | — | — | 1,741 ± 26 | 12,350 ± 42 |
| Two statements in one file | Page by page, one call (default) | — | — | — | — | — | — | — |
| Two statements in one file | Holistic, one call | — | — | — | — | — | — | — |
| Two statements in one file | Detect sections first (page by page), then classify | — | — | — | — | — | — | — |
| Two statements in one file | Detect sections first (holistic), then classify | — | — | — | — | — | — | — |
| Same-class packets | Page by page, one call (default) | — | — | — | — | — | — | — |
| Same-class packets | Holistic, one call | — | — | — | — | — | — | — |
| Same-class packets | Detect sections first (page by page), then classify | — | — | — | — | — | — | — |
| Same-class packets | Detect sections first (holistic), then classify | — | — | — | — | — | — | — |


#### SC-02: Do I need page images in the classification prompt?

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


#### SC-03: Which classification model should I use?

**Answer:** Not yet measured.

| | |
|---|---|
| **Changes** | Classification model |
| **Everything else** | Run at both granularities: page by page and holistic; the rest as each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq) |
| **Runs** | 3 per document, per value |

| Dataset | Classification model | Page accuracy | Section accuracy | Grouping score | Boundary accuracy | Label accuracy | Classification tokens per page | Total tokens per page | Median seconds per document |
|---|---|---|---|---|---|---|---|---|---|
| DocSplit | Amazon Nova 2 Lite (default) | — | — | — | — | — | — | — | — |
| DocSplit | Amazon Nova Pro | — | — | — | — | — | — | — | — |
| DocSplit | Claude Haiku 5.5 | — | — | — | — | — | — | — | — |
| DocSplit | Claude Sonnet 5 | — | — | — | — | — | — | — | — |


#### SC-04: How long a packet can holistic classification handle?

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


#### SC-05: Does neighboring-page context help page-by-page classification?

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


#### SC-06: Do few-shot examples help classification?

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


#### SC-07: How much do class descriptions matter?

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


#### SC-08: Does accuracy drop as I add document classes?

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


#### SC-09: How small can classification images be?

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


#### SC-10: If every file is one document, should I turn splitting off?

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
