> ⚙️ **Optional Enrichment:** This challenge extends your Greenweez pipeline to use community packages and Jinja macros. Complete it if you have time or are interested in how production dbt projects manage reusable code.

## Context

In the marketing campaign challenge you wrote `int_marketing_campaigns.sql` with two division-by-zero guards:

```sql
case when ads_impressions > 0 then ads_clicks * 1.0 / ads_impressions else 0 end as click_through_rate,
case when ads_clicks > 0     then ads_cost / ads_clicks                else 0 end as cost_per_click
```

These are the same pattern twice. If you add a third metric you will write it a third time. This is the kind of repetition that dbt's **macro system** is designed to eliminate.

You have been using macros throughout this unit without realising it: `{{ ref() }}`, `{{ source() }}`, and `{{ config() }}` are all macros — Jinja functions that compile to SQL at runtime. In this challenge you will install `dbt_utils`, a community package that provides `dbt_utils.safe_divide()`, and use it to replace both guards. You will use `dbt compile` to verify the expanded SQL.

You will not write any macro code. Using library functions is the analyst's role; writing and maintaining a macro library is the engineer's.

## Objective

Install `dbt_utils` and refactor `int_marketing_campaigns.sql` to use `dbt_utils.safe_divide()`.

**By the end of this challenge, you will be able to:**

- Explain what a macro is and how dbt Jinja expressions compile to SQL
- Install a dbt package using `packages.yml` and `dbt deps`
- Call a package macro in an existing model
- Use `dbt compile` to inspect what a macro expands to

---

## Prerequisites

- Completed Unit 10 Challenges 01–04
- `int_marketing_campaigns.sql` with the manual `CASE WHEN` guards from Ch04

---

## Section 0: Copy Your Project

> **Working directory convention:** `dbt` commands run from **inside** `greenweez_dbt/`. `git` commands run from the **challenge directory** (one level up).

**📍 In your terminal (challenge directory):**

```bash
# Check the name of your previous challenge directory
ls ..

cp -rP ../../../{{ local_path_to("03-Data-Transformation/10-DBT-Advanced/06-Dev-Vs-Production") }}/greenweez_dbt .
```

<details>
<summary markdown="span">**Skipped Challenge 05? Copy from Challenge 04 instead**</summary>

```bash
cp -r ../../../{{ local_path_to("03-Data-Transformation/10-DBT-Advanced/05-Marketing-Campaign-Data") }}/greenweez_dbt .
```

</details>

**📍 In your terminal (inside greenweez_dbt/):**

```bash
cd greenweez_dbt
dbt debug
```

You should see `Connection test: OK`.

**📍 In your terminal (challenge directory):**

```bash
git add greenweez_dbt/
git commit -m "Copy Greenweez pipeline from previous challenge"
git push origin master
```

---

## Section 1: What Is a Macro?

A macro is a Jinja function that dbt compiles to plain SQL before running anything. You have already been using them:

- `{{ ref('stg_sales') }}` → `"main_staging"."stg_sales"` (the actual schema-qualified table name)
- `{{ source('raw', 'raw_gz_sales') }}` → `"raw"."raw_gz_sales"`
- `{{ config(materialized='table') }}` → Removed — used to configure the model, not output SQL

A package macro like `{{ dbt_utils.safe_divide(numerator, denominator) }}` works the same way — it compiles to a `CASE WHEN` expression before any SQL runs. The database never sees `dbt_utils.safe_divide`; it only sees the expanded SQL.

**`dbt compile` shows you exactly what gets sent to the database.** This is how you debug macros: check the compiled output in `target/compiled/`, not the source template.

---

## Section 2: Install dbt_utils

### 2.1 Create packages.yml

**📝 In VS Code**, create `greenweez_dbt/packages.yml`:

```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: 1.1.1
```

### 2.2 Install the package

**📍 In your terminal (inside greenweez_dbt/):**

```bash
dbt deps
```

You should see `Installing dbt-labs/dbt_utils`. The package installs to `dbt_packages/` — this directory is git-ignored, like `node_modules` in a Node project. The `packages.yml` file is the source of truth; never commit `dbt_packages/`.

### 2.3 Explore what you installed (optional)

Take a look at what `dbt_utils` actually contains:

```bash
ls dbt_packages/dbt_utils/macros/
```

These are just SQL and Jinja files — the same kind of code you write in `models/`. Packages are not compiled binaries; they are readable source files. Open any one to see how a macro is written.

---

## Section 3: Use dbt_utils.safe_divide

### 3.1 Understand the macro signature

`dbt_utils.safe_divide(numerator, denominator)` compiles to:

```sql
case
    when (denominator) = 0 then null
    else (numerator) / (denominator)
end
```

It returns `NULL` when the denominator is zero. Your existing guards return `0` — this is a design choice. Either is valid; `NULL` is often more analytically correct (0 sessions did not produce a 0% CTR; it produced no CTR at all). You can use either approach — use `dbt_utils.safe_divide` for now and note the difference.

### 3.2 Refactor int_marketing_campaigns.sql

**📝 In VS Code**, open `models/intermediate/int_marketing_campaigns.sql`.

Replace the two manual `CASE WHEN` guards:

```sql
-- Before (manual guards):
case when ads_impressions > 0 then ads_clicks * 1.0 / ads_impressions else 0 end as click_through_rate,
case when ads_clicks > 0     then ads_cost / ads_clicks                else 0 end as cost_per_click
```

With macro calls:

```sql
-- After (using dbt_utils):
{{ dbt_utils.safe_divide('ads_clicks * 1.0', 'ads_impressions') }} as click_through_rate,
{{ dbt_utils.safe_divide('ads_cost', 'ads_clicks') }}              as cost_per_click
```

### 3.3 Compile and inspect

**📍 In your terminal (inside greenweez_dbt/):**

```bash
dbt compile --select int_marketing_campaigns
```

**📝 In VS Code**, open `target/compiled/greenweez_dbt/models/intermediate/int_marketing_campaigns.sql`.

You should see the `{{ dbt_utils.safe_divide(...) }}` calls expanded to `CASE WHEN` expressions. The compiled SQL is what dbt actually runs. If the compiled SQL looks correct, run it.

### 3.4 Build and verify

**📍 In your terminal (inside greenweez_dbt/):**

```bash
dbt build --select int_marketing_campaigns
```

Expected: `PASS=1 WARN=0 ERROR=0`.

**🗄️ In DBeaver**, query the result to confirm the metric columns still exist and have values:

```sql
SELECT
    campaign_name,
    platform,
    click_through_rate,
    cost_per_click
FROM main_intermediate.int_marketing_campaigns
LIMIT 10;
```

---

### Checkpoint: Packages Config

**📍 In your terminal (challenge directory):**

```bash
pytest tests/ -v
```

**Expected:** 8 passed

**If tests pass**, commit and push:

```bash
git add greenweez_dbt/packages.yml
git add greenweez_dbt/models/intermediate/int_marketing_campaigns.sql
git commit -m "Install dbt_utils and use safe_divide in int_marketing_campaigns"
git push origin master
```

---

## 🎉 Challenge Complete

### Key takeaways

- **Macros compile away** — the database only ever sees plain SQL; use `dbt compile` to verify what a macro produces
- **`packages.yml` + `dbt deps`** — declare what you need, run `dbt deps`, done; never commit `dbt_packages/`
- Calling a package macro is the same as calling `COALESCE()` — you don't need to understand the implementation to use it
