# SQL Query Optimization

This document explains the core patterns for writing fast analytical SQL, especially for dashboards and reports.

## Key Principles

- Avoid `SELECT *`.
- Filter as early as possible before joins.
- Use CTEs to structure complex logic.
- Keep queries explicit and readable.

## Common Antipatterns

### SELECT *

`SELECT *` returns every column from every table in the query. If the analysis needs only a few columns, this wastes I/O, memory, and network bandwidth. Always name the columns you need.

### Joining before filtering

Joining large tables before applying filters creates oversized intermediate results. Filter the driving table first, then join the reduced dataset.

### Deep nested subqueries

Many nested subqueries are hard to read and maintain. Replace them with a series of named CTEs.

## Checklist

- [ ] No `SELECT *`
- [ ] Filters applied before joins when possible
- [ ] Complex logic broken into CTEs
- [ ] Explicit column aliases and table aliases used consistently
- [ ] Query reviewed on production-scale data
- [ ] Execution plan validated with `EXPLAIN` or `EXPLAIN ANALYZE`

## Example

```
WITH filtered_transactions AS (
  SELECT transaction_id, customer_id, amount
  FROM transactions
  WHERE transaction_year = 2024
)
SELECT
  t.transaction_id,
  t.customer_id,
  t.amount,
  c.customer_name
FROM filtered_transactions t
JOIN customers c ON t.customer_id = c.id;
```

This pattern is faster and easier to maintain than querying all rows and columns first, then filtering.
