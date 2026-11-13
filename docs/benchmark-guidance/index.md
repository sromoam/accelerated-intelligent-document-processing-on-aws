---
title: "How We Benchmark Configurations"
---

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

# How We Benchmark Configurations

These pages answer the questions customers ask when they configure the accelerator, such as
"When is agentic extraction worth it?" and "Help me choose a mechanism for packet
splitting", with measured results. There is one page per problem set from
[How Document Processing Works](../idp-fundamentals/index.md), and one page on token use:

| Page | Questions it answers |
|---|---|
| [Digitization (OCR)](digitization.md) | Which OCR reader, at what resolution, for which documents |
| [Splitting and Section Classification](splitting-and-classification.md) | Which splitting mechanism, whether to send page images, which classification model |
| [Key Information Extraction](extraction.md) | When to use agentic extraction, which extraction model, what improves accuracy |
| [Confidence Assessment](confidence-assessment.md) | Whether confidence can route review, which scoring model, which threshold |
| [Rule Validation](rule-validation.md) | Which rule engine, which model, how accurate the verdicts are |
| [Token Use and Cost](token-use.md) | What drives the number of tokens each step uses, and how to reduce it |

## How to read an answer

Every question on these pages is answered by an **ablation**: a set of runs that changes one
setting and holds everything else at the baseline below. Each answer has the same parts:

1. **The question**, in the words a customer asks it.
2. **The verdict**: what to configure, in one or two sentences, or *Not yet measured*.
3. **The ablation**: what changes, what stays fixed, which datasets, and how many runs.
4. **The results table**: one row per setting value, one column per metric.
5. **How far this carries**: the documents and conditions the result applies to.

Each ablation has a stable ID, such as `EX-01`. The benchmark scripts use the ID to fill in
the results table, so a table changes only when the measurement changes.

Each results table has a status:

| Status | Meaning |
|---|---|
| **Not yet measured** | The ablation is defined and the table is empty |
| **Measured on release X** | Every cell comes from runs on release X, cited by source path |
| **Superseded** | A later release changed the behavior; the table shows the newer measurement |

## The baseline every ablation starts from

Every ablation changes one setting and holds the rest at the accelerator's shipped defaults
for Pipeline mode:

| Step | Shipped default |
|---|---|
| Digitization | Amazon Textract with the `TABLES`, `LAYOUT` and `SIGNATURES` features, pages rendered at 300 DPI |
| Splitting and section classification | *Split and classify together (one call)*, granularity *page*, page text and images, classification model Amazon Nova 2 Lite |
| Extraction | Single pass (*Simple*), extraction model Claude Sonnet 5, reasoning effort *low* |
| Confidence assessment | Separate pass, scoring model Amazon Nova Lite, confidence threshold 0.8 |
| Rule validation | Off; when turned on, the language-model engine |

When an ablation needs a different starting point, for example iterative extraction to study
shard size, the ablation states it.

## Why you can trust the results

- **Known right answers.** Every dataset has ground truth: exact answers generated with
  synthetic documents, or answers checked by people on public documents. See
  [Benchmark Datasets](../idp-fundamentals/benchmark-datasets.md).
- **One change at a time.** Each ablation changes one setting on one deployed stack, so a
  difference comes from that setting and not from anything else.
- **Same documents, compared document by document.** Every value of a setting runs on the
  same documents, and differences are reported with their standard error.
- **Repeated runs.** Model output varies from run to run on the same input, so every value
  runs at least three times, and the table reports the spread.
- **A verdict needs a real difference.** A verdict names a winner only when the difference
  is larger than twice its standard error. Otherwise the verdict says there is no measurable
  difference, and the choice can be made on tokens or speed.
- **Pinned to a release.** Every number names the release, the month and the region it was
  measured on, and the path of the committed results file it comes from.
- **Tokens, not prices.** The tables report tokens, which do not change when prices do. To
  estimate cost, multiply by your current model prices.
- **Reproducible in your account.** Most datasets come with every stack as Test Studio test
  sets, so you can run the same comparison on your own stack, and then on your own documents.

## What these results do not cover

- **Your documents.** These datasets stand in for common document types. Confirm a choice on
  a test set built from your own documents; see
  [Measure with ground truth](../idp-fundamentals/index.md#4-measure-with-ground-truth).
- **BDA mode.** These pages cover Pipeline mode only.
- **Datasets we do not have yet.** Several ablations need a dataset that does not exist yet.
  Each ablation that needs one says so:
  - long packets of 30 to 60 pages, with section ground truth;
  - packets that hold several documents of the same class back to back;
  - packets with both section and field ground truth, to measure splitting and extraction
    together;
  - handwritten forms with field ground truth;
  - documents paired with expert rule verdicts.

## Ablations that apply to every problem set

<!-- BEGIN GENERATED ABLATIONS -->

### TR-01: How much do results vary between identical runs?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | Nothing: the baseline, run repeatedly |
| **Held fixed** | Everything else at the [baseline](#the-baseline-every-ablation-starts-from) |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [DocSplit-Poly-Seq (20 packets)](../idp-fundamentals/benchmark-datasets.md#docsplit-poly-seq); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 10 per document per value |

| Dataset | Nothing: the baseline, run repeatedly | Weighted accuracy | Total tokens per page |
|---|---|---|---|
| RealKIE | Baseline | — | — |

| Dataset | Nothing: the baseline, run repeatedly | Boundary accuracy | Total tokens per page |
|---|---|---|---|
| DocSplit | Baseline | — | — |

| Dataset | Nothing: the baseline, run repeatedly | Completeness | Total tokens per page |
|---|---|---|---|
| Statement, 400 rows | Baseline | — | — |


### TR-02: How long does a document take, and how many documents an hour?

**Verdict:** Not yet measured.

| | |
|---|---|
| **Changes** | Documents submitted at once |
| **Held fixed** | Everything else at the [baseline](#the-baseline-every-ablation-starts-from) |
| **Datasets** | [RealKIE-FCC-Verified (20 invoices)](../idp-fundamentals/benchmark-datasets.md#realkie-fcc-verified); [Synthetic statement, 400 rows (9 pages)](../idp-fundamentals/benchmark-datasets.md#synthetic-bank-statements) |
| **Runs** | 3 per document per value |

| Dataset | Documents submitted at once | Median seconds per document |
|---|---|---|
| RealKIE | 1 | — |
| RealKIE | 10 | — |
| RealKIE | 50 | — |

| Dataset | Documents submitted at once | Median seconds per document |
|---|---|---|
| Statement, 400 rows | 1 | — |
| Statement, 400 rows | 10 | — |
| Statement, 400 rows | 50 | — |

<!-- END GENERATED ABLATIONS -->
