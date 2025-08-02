# Query Test

This repository contains scripts and configurations for benchmarking PostgreSQL database performance using pgbench. The primary objective is to conduct individual query performance testing to measure efficiency differences between various SQL queries under identical hardware specifications.

## DataSet

The testing environment utilizes real-world data to ensure meaningful performance measurements:

1. **Data Source**: TSV files from the [IMDB dataset](https://datasets.imdbws.com/) are used to populate the PostgreSQL database
2. **Schema Reference**: Table structures and relationships follow the specifications defined in [IMDB Non-Commercial Datasets](https://developer.imdb.com/non-commercial-datasets/)
3. **Data Characteristics**: 
   - Large-scale production dataset with millions of records
   - Complex relational structure with multiple interconnected tables
   - Real-world data distribution patterns and constraints
   - Provides realistic testing scenarios for query performance evaluation

## Command

### Restore Database

```bash
psql -U postgres -d imdb -f /data/imdb_schema.sql
```

### Running Tests

```bash
pgbench -h postgres-test -p 5432 -U postgres -d imdb -c 1 -T 10 -f query/test.sql --no-vacuum
```

## Threshold

### 01. Simple Select (PK Access)

#### Query

```sql
SELECT * FROM title_basics WHERE tconst = 'tt1234567';
```


### 02. Pattern Matching (ILIKE)

#### Query

```sql
SELECT * FROM title_basics WHERE primaryTitle ILIKE '%star wars%';
```


### 03. Join: Top Rated Movies

#### Query

```sql
-- 평점이 높은 상위 영화 10개
SELECT b.tconst, b.primaryTitle, r.averageRating
FROM title_basics b
JOIN title_ratings r ON b.tconst = r.tconst
WHERE b.titleType = 'movie'
ORDER BY r.averageRating DESC
LIMIT 10;
```

### 04. Multi-condition & Group By: Movie Count by Genre and Year

#### Query

```sql
SELECT genres, startYear, COUNT(*) AS movie_count
FROM title_basics
WHERE titleType = 'movie'
  AND startYear BETWEEN 2010 AND 2020
GROUP BY genres, startYear
ORDER BY movie_count DESC;
```

### 05. Multi-table Join: Movie Count by Director

#### Query

```sql
SELECT c.directors, COUNT(*) AS film_count
FROM title_crew c
JOIN title_basics b ON c.tconst = b.tconst
WHERE b.titleType = 'movie'
GROUP BY c.directors
ORDER BY film_count DESC
LIMIT 10;
```


### 06. Subquery: Filmography of a Specific Actor

#### Query

```sql
SELECT b.primaryTitle
FROM title_basics b
WHERE b.tconst IN (
    SELECT p.tconst
    FROM title_principals p
    WHERE p.nconst = (
        SELECT n.nconst
        FROM name_basics n
        WHERE n.primaryName = 'Tom Hanks'
        LIMIT 1
    )
);
```


### 07. CTE: Yearly Movie Counts

#### Query

```sql
WITH yearly_counts AS (
    SELECT startYear, COUNT(*) AS cnt
    FROM title_basics
    WHERE titleType = 'movie'
    GROUP BY startYear
)
SELECT * FROM yearly_counts WHERE startYear >= 2000 ORDER BY cnt DESC;
```

### 08. Window Function: Top Rated Movie by Year

#### Query

```sql
SELECT *
FROM (
    SELECT
        b.startYear,
        b.primaryTitle,
        r.averageRating,
        ROW_NUMBER() OVER (PARTITION BY b.startYear ORDER BY r.averageRating DESC) AS rn
    FROM title_basics b
    JOIN title_ratings r ON b.tconst = r.tconst
    WHERE b.titleType = 'movie' AND b.startYear IS NOT NULL
) sub
WHERE rn = 1
ORDER BY startYear;
```


