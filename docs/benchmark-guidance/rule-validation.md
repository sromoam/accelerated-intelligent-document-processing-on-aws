---
title: "Rule Validation Benchmarks"
tableOfContents:
  maxHeadingLevel: 3
---

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

# Rule Validation Benchmarks

Rule validation checks each file against your business rules and returns a verdict for every
rule, with the evidence behind it.
[Rule Validation](../idp-fundamentals/rule-validation.md) explains how it works.

## How to improve rule verdicts on your documents

**Your definitions.** Put one criterion in each rule, state the threshold, and define any
term your industry uses loosely. Add the facts your rules depend on as extraction fields, so
you can measure and correct them. See
[Improving rule verdicts](../idp-fundamentals/rule-validation.md#improving-rule-verdicts-once-your-pipeline-is-running).

**Data quality.** A verdict is only as good as the facts behind it. When extraction misses a
fact, the rule comes back *Information Not Found*.

**Settings.**

| Setting | What it changes | Questions |
|---|---|---|
| Engine | A language model for rules that need judgment, or the Z3 solver for exact rules | [RV-02](#language-model-or-z3-for-exact-rules) |
| Policy Discovery | Drafts rules from a policy document | [RV-03](#are-rules-drafted-by-policy-discovery-as-good-as-hand-written-rules) |
| Chunk size | How much text the accelerator sends with each rule | [RV-04](#how-large-should-rule-validation-chunks-be) |

We haven't built the dataset these benchmarks need yet: documents with an expert's verdict
on each rule.

## Benchmark datasets and metrics

<!-- BEGIN GENERATED DATASETS -->

| Dataset | Preset |
|---|---|
| Documents with expert rule verdicts (to be built) | — |

<!-- END GENERATED DATASETS -->

**Metrics**

- *Verdict agreement:* the share of verdicts that match the expert's.
- *Wrong passes:* rules the accelerator passed and the expert failed.
- *Wrong fails:* rules the accelerator failed and the expert passed.
- *Information not found:* rules the accelerator could not decide.

## Questions

<!-- BEGIN GENERATED FAQ -->

### How accurate are rule verdicts?

**Answer:** Not yet measured. [Details: RV-01](#rv-01-how-accurate-are-rule-verdicts)

### Language model or Z3 for exact rules?

**Answer:** Not yet measured. [Details: RV-02](#rv-02-language-model-or-z3-for-exact-rules)

### Are rules drafted by Policy Discovery as good as hand-written rules?

**Answer:** Not yet measured. [Details: RV-03](#rv-03-are-rules-drafted-by-policy-discovery-as-good-as-hand-written-rules)

### How large should rule-validation chunks be?

**Answer:** Not yet measured. [Details: RV-04](#rv-04-how-large-should-rule-validation-chunks-be)

<!-- END GENERATED FAQ -->

## Benchmark details

<!-- BEGIN GENERATED ABLATIONS -->

#### RV-01: How accurate are rule verdicts?

**Answer:** Not yet measured.

Needs a dataset we haven't built yet: Documents with expert rule verdicts (to be built).

| | |
|---|---|
| **Changes** | Rule validation model |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | Documents with expert rule verdicts (to be built) |
| **Runs** | 3 per document, per value |

| Dataset | Rule validation model | Verdict agreement | Wrong passes | Wrong fails | Information not found | Rule validation tokens per document |
|---|---|---|---|---|---|---|
| Rule-verdict set | Default model | — | — | — | — | — |
| Rule-verdict set | Claude Haiku 5.5 | — | — | — | — | — |
| Rule-verdict set | Claude Sonnet 5 | — | — | — | — | — |


#### RV-02: Language model or Z3 for exact rules?

**Answer:** Not yet measured.

Needs a dataset we haven't built yet: Documents with expert rule verdicts (to be built).

| | |
|---|---|
| **Changes** | Rule engine (`x-aws-idp-validation-engine`) |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | Documents with expert rule verdicts (to be built) |
| **Runs** | 3 per document, per value |

| Dataset | Rule engine (`x-aws-idp-validation-engine`) | Verdict agreement | Wrong passes | Wrong fails | Rule validation tokens per document |
|---|---|---|---|---|---|
| Rule-verdict set | Language model (default) | — | — | — | — |
| Rule-verdict set | Z3 solver | — | — | — | — |


#### RV-03: Are rules drafted by Policy Discovery as good as hand-written rules?

**Answer:** Not yet measured.

Needs a dataset we haven't built yet: Documents with expert rule verdicts (to be built).

| | |
|---|---|
| **Changes** | Rule source |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | Documents with expert rule verdicts (to be built) |
| **Runs** | 3 per document, per value |

| Dataset | Rule source | Verdict agreement | Wrong passes | Wrong fails |
|---|---|---|---|---|
| Rule-verdict set | Hand-written | — | — | — |
| Rule-verdict set | Drafted by Policy Discovery | — | — | — |
| Rule-verdict set | Drafted, then reviewed by hand | — | — | — |


#### RV-04: How large should rule-validation chunks be?

**Answer:** Not yet measured.

Needs a dataset we haven't built yet: Documents with expert rule verdicts (to be built).

| | |
|---|---|
| **Changes** | `max_chunk_size` |
| **Everything else** | As each dataset's [preset](index.md#how-we-run-a-benchmark) sets it |
| **Datasets** | Documents with expert rule verdicts (to be built) |
| **Runs** | 3 per document, per value |

| Dataset | `max_chunk_size` | Verdict agreement | Information not found | Rule validation tokens per document |
|---|---|---|---|---|
| Rule-verdict set | 8,000 (default) | — | — | — |
| Rule-verdict set | 4,000 | — | — | — |
| Rule-verdict set | 16,000 | — | — | — |

<!-- END GENERATED ABLATIONS -->
