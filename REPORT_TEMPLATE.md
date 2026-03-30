
**Student Name:** Kittakan Phungsuriya
**Student ID:** 660610859
**Date:** 30 Mar 2026

---

## Part 1: Data Exploration Answers  

> How many total transactions are there?

72,586,000 transactions

> How many unique family members, merchants, and categories?

4 family members, 48 merchants, and 18 categories

> How many rows have null or empty `amount` values?

1,450,421 rows

> What is the date range of the transactions?

From 2010-01-01 to 2025-12-31

---

## Part 4: Join Analysis

> What join type did you use for enriching transactions, and why?

I used a left join to preserve all transactions, even if some do not have matching merchants.

> How many transactions have no matching merchant in the merchants table?

212,089 transactions

> What would happen if you used an inner join instead?

Transactions without matching merchants would be dropped, resulting in data loss.

---

## Part 5: Analytics Insights

> Look at the average transaction amount per year table. Do you notice a trend? Calculate the approximate year-over-year percentage change. What might explain this?

The average transaction amount increased steadily from 55.98 in 2016 to 66.94 in 2025, about a 19.6% increase over 10 years, with an average growth of around 2% per year, close to inflation, indicating that spending hasn’t increased but prices have risen.

| Year | Avg Amount| YoY Change (%) |
|------|-----------|----------------|
| 2016 | 55.98     | —              |
| 2017 | 57.12     | 2.04%          |
| 2018 | 58.33     | 2.12%          |
| 2019 | 59.47     | 1.95%          |
| 2020 | 60.59     | 1.88%          |
| 2021 | 61.87     | 2.11%          |
| 2022 | 63.08     | 1.96%          |
| 2023 | 64.41     | 2.11%          |
| 2024 | 65.54     | 1.75%          |
| 2025 | 66.94     | 2.14%          |

The trend is consistent, increasing about 2% per year with no sharp spikes, indicating inflation rather than a change in spending behavior. In 2024 it dipped slightly by 1.75% and in 2025 rose slightly by 2.14%, reflecting normal fluctuations.

> Which category has the highest total spending? Which has grown the fastest over 10 years?

Groceries has the highest total spending. Electronics is the fastest-growing category, around 20%.

> Compare spending between family members. Who spends the most? On what?

MEM01 spends the most, about 1.96B, followed by MEM02, about 1.66B, MEM03, about 482M, and MEM04, about 241M. MEM03 and MEM04 spend less, likely younger members. All members spend the most on Groceries, followed by Electronics and Education, showing shared household needs rather than personal preferences.

> What percentage of transactions fall in each spending tier? Has this distribution changed over the years?

Most transactions 49.53% are in the small tier, followed by medium 31.31%, micro 14.0%, and large 5.16%. Over 10 years, micro decreased while medium and large grew, reflecting inflation moving prices into higher tiers.

---

## Section A: Data Architecture Questions

_The family has some questions about how the system works._

### Q1. Merchant Name Change

> "We just found out one of the merchants changed their name last year. Where in the pipeline do we update this, and what layers need to be reprocessed?"

The merchant name is stored in merchants.csv and used in the raw and analytics layers. To update it, edit the file and rerun the pipeline from the raw layer, regenerating raw merchants, rebuilding enriched transactions, and all aggregation tables. The staged layer does not need changes because it only stores the merchant id.

---

### Q2. New Family Member

> "Our daughter started college and has her own credit card now. How do we add a new family member to the system without breaking existing data?"

No code changes are needed because member_id is flexible. Just add the new member in the CSV and the pipeline will include it automatically. Existing data remains unchanged, and a members table can be added to use names instead of IDs.
---

### Q3. Average Monthly Grocery Spending

> "We want to know our average monthly grocery spending. Walk us through exactly which transformations and joins produce this number."

This value comes from the monthly_by_category table by filtering valid data, joining with categories to get the category name, grouping by month and category and summing the amount, then filtering for Groceries and calculating the average per month.

---

### Q4. Duplicate Transactions

> "Last month's bank export had 500 duplicate transactions. How does your pipeline handle this? If it doesn't yet, what would you add?"

The pipeline does not remove duplicates, so duplicate transaction_id values are counted twice. A deduplication step using df.dropDuplicates should be added in the staged layer, along with a check and warning if duplicates are found.

---

### Q5. Data Backup & Recovery

> "We're worried about losing our data. What's your backup strategy? What's the most data we could lose if something crashes?"

_Hint: Think about RPO (Recovery Point Objective) and RTO (Recovery Time Objective)._

The raw Parquet layer should be used as the single source of truth and backed up to the cloud monthly with versioning. Staged and analytics can be rebuilt anytime by rerunning the pipeline. RPO is up to one month of data loss, and RTO is under 30 minutes.

---

## Section B: Engineering Questions

_The family's developer friend has some technical questions._

### Q6. CI/CD Pipeline

> "If we set up CI/CD for this project, what would the pipeline look like? What gets tested automatically, and what triggers the tests?"

The CI/CD pipeline runs on GitHub Actions on every push and pull request, with three steps: lint, tests with pytest, and a build check. If any step fails, the PR cannot be merged, preventing broken code from reaching production.
---

### Q7. Monthly Automation with Orchestration

> "We want this pipeline to run automatically every month when the bank exports new transactions. How would you set this up? Draw the DAG."

Airflow DAG on cron 0 0 1 * *. Any failure triggers an alert and halts downstream tasks.

_Draw your DAG below (text-based diagram):_

```
┌──────────────────┐
│   ingest_csv     │  ← Copy new bank export into data/folder
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   write_raw      │  ← CSV → Parquet(no changes)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  write_staged    │  ← filter_valid_transactions()
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ write_analytics  │  ← enrich + categorize + 4 aggregations
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ notify_success   │  ← Send email/Slack to family
└──────────────────┘

```

---

## Section C: Analytics Insights

_The family wants your professional opinion._

### Q8. Price Trend Analysis

> "We looked at your yearly average transaction table and prices seem to go up. Can you calculate the exact rate? Is it consistent across all categories?"

Increased from 55.98 to 66.94 over 9 years, a total increase of +19.58%, with a compound annual growth rate (CAGR) of about 2.0% per year. All major categories show roughly 19–20% total growth, indicating broad-based inflation rather than a change in spending behavior.

---

### Q9. Spending Recommendations

> "Based on your summary tables, give us 3 actionable recommendations for how we can reduce spending next year."

1. Cap Electronics spending since it is high and growing fast; reduce subscriptions and set an annual budget.
2. Reduce dining out for MEM01 and MEM02 since they spend the most; set a restaurant budget or cook more at home.
3. Add a waiting rule for large purchases; for items over 200, wait 48 hours to reduce impulse buying, especially in Wants.

---

### Q10. Needs vs Wants

> "Which spending categories are 'needs' vs 'wants'? What percentage of our total spending goes to each?"

The pipeline uses the budget_type field from categories.csv to classify transactions into needs, wants, and savings.
The family’s spending is close to the 50/30/20 guideline for needs and wants, but savings is only 6.42%, which is below the recommended 20%, so they should reduce wants and increase savings or investments.

| Budget Type | Total Spending   | Percentage |
|-------------|------------------|------------|
| Needs       | 2,160,425,364.33 | 49.77%     |
| Wants       | 1,902,196,973.51 | 43.82%     |
| Savings     | 278,489,059.80   | 6.42%      |
