---
title: "Processing a Batch of Documents"
---

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

# Processing a Batch of Documents and Getting the Results

You have **many** documents and you want their structured results back out as a set.
The accelerator supports this today — but the exact steps depend on how you access the
system. Pick the row that matches you:

| You are… | Submit a set | Get all results out |
|---|---|---|
| **Web UI user** (browser login only) | Upload panel — multi-select, under a shared **folder prefix** | Filter the document list by that prefix → select all → **Download → All data (ZIP)** |
| **CLI user** (`idp-cli`, AWS credentials) | `idp-cli process --dir … --batch-id …` | `idp-cli download-results --batch-id …` |
| **S3 user** (AWS console / `aws` CLI) | Copy files into the **InputBucket** | `aws s3 sync` the **OutputBucket** |

All three paths run the *same* processing pipeline. The difference is only how documents
go in and how results come out.

## Prerequisites (all paths)

- A deployed IDP stack — see [Deployment](./deployment.md).
- Amazon Bedrock model access granted for the models your configuration uses — see the
  [Quick Start in the README](../README.md#quick-start).
- **CLI / S3 paths only:** AWS credentials configured in your environment
  (`aws configure` or `aws sso login`).

---

## Path A — Web UI only

If you only have a browser login to the web app (no AWS credentials, no S3 console),
you can still process a set and export it in bulk. The key idea is to give the whole
set a **shared folder prefix** at upload time and use that prefix as the set's handle
everywhere afterward — it is the UI equivalent of the CLI's `--batch-id`.

### 1. Upload the set under a shared prefix

1. Open **Upload Documents**.
2. Set **Document source** to *From my computer* and pick (or drag-and-drop) all the
   files in your set. You can also choose a bundled **Sample documents** batch.
3. Set the **Optional folder prefix** to a name for this cohort, for example
   `invoices/2024`. Every file is uploaded under that prefix
   (`invoices/2024/<filename>`).
4. Pick the **Configuration Profile** to process the set with, then upload.

### 2. Let the set process

Watch the document list; each document advances to **COMPLETE**. Because the prefix is
preserved into the OutputBucket, the entire cohort stays namespaced under
`invoices/2024/…` on the output side too — it does not get mixed in with other work.

### 3. Isolate the set and export it in bulk

1. In the document list, type your prefix (e.g. `invoices/2024`) in the **filter box**.
   Only that cohort remains.
2. Tick the header checkbox to select all filtered rows.
3. **Download → Selected documents (N) → All data** (or **Predictions** / **Baselines**).

You get **one ZIP with one folder per document** (named after its object key), each laid
out as `output/`, `baseline/`, `input/`, plus a root `manifest.json` indexing every
document. See [Bulk download from the document list](./web-ui.md#bulk-download-from-the-document-list)
for the full option set.

> **Browser-built archive — mind the size.** The bulk ZIP is assembled in your browser
> tab. Selections **above 25 documents** raise a warning; large exports take minutes and
> hold the whole archive in memory. Leave **Include page images** off unless you need
> them, and prefer several smaller batches. For unattended or very large sets, use the
> CLI (Path B) instead.

---

## Path B — CLI / programmatic

If you have AWS credentials and want automation, scripting, or evaluation workflows, use
the `idp-cli`. Here `--batch-id` is a name **you choose** to group and later retrieve the
run — it is not a value the system hands back.

```bash
# Install the CLI (once)
cd lib/idp_cli_pkg && pip install -e .

# 1. Submit a local directory as a batch and watch it complete
idp-cli process \
    --stack-name <your-stack-name> \
    --dir ./my-docs/ \
    --batch-id my-run \
    --monitor

# 2. Download the whole batch's results
idp-cli download-results \
    --stack-name <your-stack-name> \
    --batch-id my-run \
    --output-dir ./results/
```

**Where results land and their shape:**

```
results/my-run/<document>/sections/<n>/result.json   ← extracted fields for each section
```

Inspect one:

```bash
cat ./results/my-run/<document>/sections/1/result.json | jq .
```

Check status separately at any time:

```bash
idp-cli status --stack-name <your-stack-name> --batch-id my-run
```

See the [IDP CLI guide](./idp-cli.md) for the full command reference, evaluation
workflows with baselines, and analytics integration.

---

## Path C — S3 direct

If you already work in the AWS console or with the `aws` CLI, submit and retrieve
straight from the buckets. Find the exact bucket names in your stack's **CloudFormation
Outputs** (`InputBucket`, `OutputBucket`).

```bash
# Submit: copy the set into the InputBucket (a shared prefix keeps it isolated)
aws s3 cp ./my-docs/ s3://<InputBucket>/invoices/2024/ --recursive

# Retrieve: results mirror the input key, so the same prefix isolates the outputs
aws s3 sync s3://<OutputBucket>/invoices/2024/ ./results/
```

Output artifacts live at deterministic keys under `<input-key>/` in the OutputBucket, so
the input prefix you chose is exactly the prefix your results appear under.

---

## Which path should I use?

- **A handful of documents, browser access only** → **Web UI** (Path A). Prefix +
  filter + bulk ZIP.
- **Hundreds of documents, automation, CI, or evaluation** → **CLI** (Path B). The
  browser archive is not built for large exports.
- **Documents already in S3, or a data pipeline** → **S3 direct** (Path C).

The **prefix** (Web UI / S3) and the **`--batch-id`** (CLI) are the same idea: a handle
that keeps one set of documents — and its results — isolated from everything else.
