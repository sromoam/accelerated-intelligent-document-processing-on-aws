---
title: "Rule Validation Benchmarks"
---

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

# Rule Validation Benchmarks

- How accurate are rule verdicts?
- Language model or Z3 for exact rules?
- Are rules drafted by Policy Discovery as good as hand-written rules?

[Rule Validation](../idp-fundamentals/rule-validation.md) explains how the accelerator
checks rules. These benchmarks need documents with an expert's verdict on each rule, and we
haven't built that dataset yet.

**Metrics**

- *Verdict agreement:* the share of verdicts that match the expert's.
- *Wrong passes:* rules the accelerator passed and the expert failed.
- *Wrong fails:* rules the accelerator failed and the expert passed.
- *Information not found:* rules the accelerator could not decide.

## Benchmarks

<!-- BEGIN GENERATED ABLATIONS -->

### RV-01: How accurate are rule verdicts?

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


### RV-02: Language model or Z3 for exact rules?

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


### RV-03: Are rules drafted by Policy Discovery as good as hand-written rules?

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


### RV-04: How large should rule-validation chunks be?

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
