---
title: "Rule Validation Benchmarks"
---

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

# Rule Validation Benchmarks

These ablations answer how accurate rule verdicts are, which engine to use for which rules,
and whether rules drafted by Policy Discovery are good enough. For how rule validation
works, see [Rule Validation](../idp-fundamentals/rule-validation.md).

Every ablation on this page needs a dataset of documents paired with an expert's verdict on
each rule, and that dataset does not exist yet.

**Metrics on this page:**

- *Verdict agreement:* the share of verdicts that match the expert's.
- *Wrong passes:* rules the accelerator passed that the expert failed.
- *Wrong fails:* rules the accelerator failed that the expert passed.
- *Information not found:* rules the accelerator could not decide.

Every ablation holds everything except the setting it changes at the
[baseline](index.md#the-baseline-every-ablation-starts-from).

<!-- BEGIN GENERATED ABLATIONS -->

### RV-01: How accurate are rule verdicts?

**Verdict:** Not yet measured.

Needs a dataset that does not exist yet: Documents with expert rule verdicts (to be built).

| | |
|---|---|
| **Changes** | Rule validation model |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | Documents with expert rule verdicts (to be built) |
| **Runs** | 3 per document per value |

| Dataset | Rule validation model | Verdict agreement | Wrong passes | Wrong fails | Information not found | Rule validation tokens per document |
|---|---|---|---|---|---|---|
| Rule-verdict set | Default model | — | — | — | — | — |
| Rule-verdict set | Claude Haiku 5.5 | — | — | — | — | — |
| Rule-verdict set | Claude Sonnet 5 | — | — | — | — | — |


### RV-02: Language model or Z3 for exact rules?

**Verdict:** Not yet measured.

Needs a dataset that does not exist yet: Documents with expert rule verdicts (to be built).

| | |
|---|---|
| **Changes** | Rule engine (`x-aws-idp-validation-engine`) |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | Documents with expert rule verdicts (to be built) |
| **Runs** | 3 per document per value |

| Dataset | Rule engine (`x-aws-idp-validation-engine`) | Verdict agreement | Wrong passes | Wrong fails | Rule validation tokens per document |
|---|---|---|---|---|---|
| Rule-verdict set | Language model (default) | — | — | — | — |
| Rule-verdict set | Z3 solver | — | — | — | — |


### RV-03: Are rules drafted by Policy Discovery as good as hand-written rules?

**Verdict:** Not yet measured.

Needs a dataset that does not exist yet: Documents with expert rule verdicts (to be built).

| | |
|---|---|
| **Changes** | Rule source |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | Documents with expert rule verdicts (to be built) |
| **Runs** | 3 per document per value |

| Dataset | Rule source | Verdict agreement | Wrong passes | Wrong fails |
|---|---|---|---|---|
| Rule-verdict set | Hand-written | — | — | — |
| Rule-verdict set | Drafted by Policy Discovery | — | — | — |
| Rule-verdict set | Drafted, then reviewed by hand | — | — | — |


### RV-04: How large should rule-validation chunks be?

**Verdict:** Not yet measured.

Needs a dataset that does not exist yet: Documents with expert rule verdicts (to be built).

| | |
|---|---|
| **Changes** | `max_chunk_size` |
| **Held fixed** | Everything else at the [baseline](index.md#the-baseline-every-ablation-starts-from) |
| **Datasets** | Documents with expert rule verdicts (to be built) |
| **Runs** | 3 per document per value |

| Dataset | `max_chunk_size` | Verdict agreement | Information not found | Rule validation tokens per document |
|---|---|---|---|---|
| Rule-verdict set | 8,000 (default) | — | — | — |
| Rule-verdict set | 4,000 | — | — | — |
| Rule-verdict set | 16,000 | — | — | — |

<!-- END GENERATED ABLATIONS -->
