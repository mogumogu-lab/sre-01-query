# Load Test

This repository contains scripts and configurations for benchmarking a PostgreSQL database using `pgbench`. The focus is on testing various SQL queries to evaluate performance under different loads.

## Command

### Restore Database

```bash
pg_restore -U postgres -d dvdrental /data/dvdrental.tar
```

### Send SQL

```bash
pgbench -h postgres-test -p 5432 -U postgres -d dvdrental -c 60 -T 10 -f test/02_simple_select.sql --no-vacuum
```

## Threshold

### 01. Simple Select (PK Access)

#### Query

```
\set random_id random(1, 599)
SELECT * FROM customer WHERE customer_id = :random_id;
```

#### Result




### 02. Search by Title (ILIKE)

### 03. Customer Last Rental (Order By)

### 04. Count Rental per Customer (Group By)

### 05. Film Rental History (Join)

### 06. Top 10 Film (Join + Group By)

### 07.Top 5 Customer Month (Join + Group By)

### 08. Update Customer (Update)

### 09. Insert Customer (Insert)

### 10. Update Return (Update)

### 11. New Rental Transaction (Insert)
