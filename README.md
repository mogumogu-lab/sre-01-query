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
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    *
FROM
    title_basics
WHERE
    tconst = 'tt1234567';
```

#### Result

```plaintext
Index Scan using title_basics_pkey on title_basics  (cost=0.43..8.45 rows=1 width=84) (actual time=0.032..0.033 rows=1 loops=1)
  Index Cond: (tconst = 'tt1234567'::text)
  Buffers: shared hit=4
Planning:
  Buffers: shared hit=11
Planning Time: 0.091 ms
Execution Time: 0.045 ms
```

There is a default index on the `title_basics` table because PostgreSQL automatically creates a primary key index when a primary key constraint is defined. This index allows the query to efficiently locate the row with `tconst = 'tt1234567'` without performing a full table scan.

### 02. Pattern Matching (ILIKE)

#### Query

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX idx_primarytitle_trgm ON title_basics USING gin (primarytitle gin_trgm_ops);

DROP INDEX IF EXISTS idx_primarytitle_trgm;

EXPLAIN (ANALYZE, BUFFERS)
SELECT
    *
FROM
    title_basics
WHERE
    primaryTitle ILIKE '%naruto%'
LIMIT
    100;
```

#### Result

```plaintext
Limit  (cost=1000.00..23498.14 rows=100 width=84) (actual time=26.547..2415.560 rows=100 loops=1)
  Buffers: shared hit=4721 read=102868
  ->  Gather  (cost=1000.00..237680.47 rows=1052 width=84) (actual time=26.546..2415.541 rows=100 loops=1)
        Workers Planned: 2
        Workers Launched: 2
        Buffers: shared hit=4721 read=102868
        ->  Parallel Seq Scan on title_basics  (cost=0.00..236575.27 rows=438 width=84) (actual time=24.626..2387.549 rows=88 loops=3)
              Filter: (primarytitle ~~* '%naruto%'::text)
              Rows Removed by Filter: 2436625
              Buffers: shared hit=4721 read=102868
Planning Time: 0.256 ms
Execution Time: 2415.612 ms
```

#### Result (with Index)

```plaintext
Limit  (cost=77.97..454.93 rows=100 width=84) (actual time=2.748..3.281 rows=100 loops=1)
  Buffers: shared hit=26 read=118
  ->  Bitmap Heap Scan on title_basics  (cost=77.97..4039.81 rows=1051 width=84) (actual time=2.747..3.268 rows=100 loops=1)
        Recheck Cond: (primarytitle ~~* '%naruto%'::text)
        Heap Blocks: exact=90
        Buffers: shared hit=26 read=118
        ->  Bitmap Index Scan on idx_primarytitle_trgm  (cost=0.00..77.71 rows=1051 width=0) (actual time=2.701..2.701 rows=419 loops=1)
              Index Cond: (primarytitle ~~* '%naruto%'::text)
              Buffers: shared hit=26 read=28
Planning:
  Buffers: shared hit=42 read=27 dirtied=3
Planning Time: 1.402 ms
Execution Time: 3.303 ms
```

When using `ILIKE '%keyword%'` in PostgreSQL, the query is normally very slow because it requires a **full table scan**—the database must check every row to see if the pattern matches anywhere in the text. This is inherently inefficient for large tables.

However, by creating a **GIN index with the `gin_trgm_ops` operator** (which comes from the `pg_trgm` extension), the database pre-processes each string into **trigrams (three-character chunks)** and builds an index based on these. When you run the same ILIKE query, PostgreSQL can quickly narrow down candidate rows using the trigram index, making the search dramatically faster—sometimes by hundreds or thousands of times.

For example, without the index, the query took about **2,400 ms**, but with the GIN trigram index, it dropped to just **3 ms**.
This is a massive improvement.

**Downsides:**

* Building the GIN trigram index itself can take a long time—especially on large tables. In my case, it took over a minute to create the index.
* While the index speeds up read/search queries, it introduces overhead for write operations (INSERT/UPDATE/DELETE), as the index must be updated for each change.
* Also, if your connection pool is small, building the index can block other queries, as it may use significant resources.

**Conclusion:**

* GIN trigram indexes are very effective for accelerating ILIKE pattern searches,
* But you should be careful when creating or rebuilding the index on large tables, especially in environments with limited resources or heavy write loads.

### 03. Join: Top Rated Movies

#### Query

```sql
CREATE INDEX idx_ratings_averagerating_desc ON title_ratings (averageRating DESC);

DROP INDEX IF EXISTS idx_ratings_averagerating_desc;

EXPLAIN (ANALYZE, BUFFERS)
SELECT
    b.tconst,
    b.primaryTitle,
    r.averageRating
FROM
    title_basics b
    JOIN title_ratings r ON b.tconst = r.tconst
WHERE
    b.titleType = 'movie'
ORDER BY
    r.averageRating DESC
LIMIT
    100;
```

#### Result

```plaintext
Limit  (cost=93613.45..95465.71 rows=100 width=36) (actual time=219.952..302.437 rows=100 loops=1)
  Buffers: shared hit=33429 read=19143, temp read=1409 written=5320
  ->  Nested Loop  (cost=93613.45..1888186.13 rows=96886 width=36) (actual time=219.951..302.425 rows=100 loops=1)
        Buffers: shared hit=33429 read=19143, temp read=1409 written=5320
        ->  Gather Merge  (cost=93613.02..279612.66 rows=1597023 width=16) (actual time=215.231..224.589 rows=10559 loops=1)
              Workers Planned: 2
              Workers Launched: 2
              Buffers: shared hit=112 read=10224, temp read=1409 written=5320
              ->  Sort  (cost=92612.99..94276.56 rows=665426 width=16) (actual time=203.418..204.289 rows=4275 loops=3)
                    Sort Key: r.averagerating DESC
                    Sort Method: external merge  Disk: 13576kB
                    Buffers: shared hit=112 read=10224, temp read=1409 written=5320
                    Worker 0:  Sort Method: external merge  Disk: 14160kB
                    Worker 1:  Sort Method: external merge  Disk: 14632kB
                    ->  Parallel Seq Scan on title_ratings r  (cost=0.00..16878.26 rows=665426 width=16) (actual time=0.021..57.761 rows=532341 loops=3)
                          Buffers: shared read=10224
        ->  Index Scan using title_basics_pkey on title_basics b  (cost=0.43..1.01 rows=1 width=30) (actual time=0.007..0.007 rows=0 loops=10559)
              Index Cond: (tconst = r.tconst)
              Filter: (titletype = 'movie'::text)
              Rows Removed by Filter: 1
              Buffers: shared hit=33317 read=8919
Planning:
  Buffers: shared hit=8 read=8
Planning Time: 2.485 ms
Execution Time: 304.313 ms
```

#### Result (with Index)

```plaintext
Limit  (cost=0.86..1745.17 rows=100 width=36) (actual time=13.405..112.282 rows=100 loops=1)
  Buffers: shared hit=43211 read=3682 written=1
  ->  Nested Loop  (cost=0.86..1689992.00 rows=96886 width=36) (actual time=13.404..112.268 rows=100 loops=1)
        Buffers: shared hit=43211 read=3682 written=1
        ->  Index Scan using idx_ratings_averagerating_desc on title_ratings r  (cost=0.43..81418.53 rows=1597023 width=16) (actual time=0.040..22.990 rows=10508 loops=1)
              Buffers: shared hit=1302 read=3559 written=1
        ->  Index Scan using title_basics_pkey on title_basics b  (cost=0.43..1.01 rows=1 width=30) (actual time=0.008..0.008 rows=0 loops=10508)
              Index Cond: (tconst = r.tconst)
              Filter: (titletype = 'movie'::text)
              Rows Removed by Filter: 1
              Buffers: shared hit=41909 read=123
Planning:
  Buffers: shared hit=237 read=6
Planning Time: 1.616 ms
Execution Time: 112.311 ms
```

### 04. Multi-condition & Group By: Movie Count by Genre and Year

#### Query

```sql
CREATE INDEX idx_basics_type_year_tconst ON title_basics (titleType, startYear, tconst);

DROP INDEX IF EXISTS idx_basics_type_year_tconst;

EXPLAIN (ANALYZE, BUFFERS)
SELECT
    b.genres,
    b.startYear,
    COUNT(*) AS movie_count,
    AVG(r.averageRating) AS avg_rating
FROM
    title_basics b
    JOIN title_ratings r ON b.tconst = r.tconst
WHERE
    b.titleType = 'movie'
    AND b.startYear BETWEEN 2010
    AND 2020
GROUP BY
    b.genres,
    b.startYear
ORDER BY
    movie_count DESC;
```

#### Result

```plaintext
Sort  (cost=290571.38..290660.75 rows=35748 width=56) (actual time=822.184..826.879 rows=5559 loops=1)
  Sort Key: (count(*)) DESC
  Sort Method: quicksort  Memory: 535kB
  Buffers: shared hit=9148 read=176234
  ->  Finalize GroupAggregate  (cost=283237.73..287867.83 rows=35748 width=56) (actual time=774.977..795.262 rows=5559 loops=1)
        Group Key: b.genres, b.startyear
        Buffers: shared hit=9148 read=176234
        ->  Gather Merge  (cost=283237.73..287048.61 rows=29790 width=56) (actual time=774.957..789.936 rows=11240 loops=1)
              Workers Planned: 2
              Workers Launched: 2
              Buffers: shared hit=9148 read=176234
              ->  Partial GroupAggregate  (cost=282237.70..282610.08 rows=14895 width=56) (actual time=760.452..768.208 rows=3747 loops=3)
                    Group Key: b.genres, b.startyear
                    Buffers: shared hit=9148 read=176234
                    ->  Sort  (cost=282237.70..282274.94 rows=14895 width=22) (actual time=760.409..761.879 rows=34494 loops=3)
                          Sort Key: b.genres, b.startyear
                          Sort Method: quicksort  Memory: 2995kB
                          Buffers: shared hit=9148 read=176234
                          Worker 0:  Sort Method: quicksort  Memory: 3015kB
                          Worker 1:  Sort Method: quicksort  Memory: 2191kB
                          ->  Parallel Hash Join  (cost=262580.28..281205.29 rows=14895 width=22) (actual time=602.471..728.550 rows=34494 loops=3)
                                Hash Cond: (r.tconst = b.tconst)
                                Buffers: shared hit=9020 read=176234
                                ->  Parallel Seq Scan on title_ratings r  (cost=0.00..16878.26 rows=665426 width=16) (actual time=0.027..40.325 rows=532341 loops=3)
                                      Buffers: shared hit=97 read=10127
                                ->  Parallel Hash  (cost=261202.17..261202.17 rows=110249 width=26) (actual time=596.000..596.001 rows=61761 loops=3)
                                      Buckets: 524288  Batches: 1  Memory Usage: 15616kB
                                      Buffers: shared hit=8902 read=166106
                                      ->  Parallel Seq Scan on title_basics b  (cost=0.00..261202.17 rows=110249 width=26) (actual time=9.305..544.996 rows=61761 loops=3)
                                            Filter: ((startyear >= 2010) AND (startyear <= 2020) AND (titletype = 'movie'::text))
                                            Rows Removed by Filter: 3874969
                                            Buffers: shared hit=8902 read=166106
Planning:
  Buffers: shared hit=31 read=5
Planning Time: 0.707 ms
JIT:
  Functions: 57
  Options: Inlining false, Optimization false, Expressions true, Deforming true
  Timing: Generation 2.462 ms (Deform 1.139 ms), Inlining 0.000 ms, Optimization 1.249 ms, Emission 26.613 ms, Total 30.324 ms
Execution Time: 828.021 ms
```

#### Result (with Index)

```plaintext
Sort  (cost=290028.97..290118.34 rows=35748 width=56) (actual time=630.234..636.853 rows=5559 loops=1)
  Sort Key: (count(*)) DESC
  Sort Method: quicksort  Memory: 535kB
  Buffers: shared hit=442 read=92737 written=13
  ->  Finalize GroupAggregate  (cost=282695.32..287325.43 rows=35748 width=56) (actual time=613.095..635.708 rows=5559 loops=1)
        Group Key: b.genres, b.startyear
        Buffers: shared hit=439 read=92737 written=13
        ->  Gather Merge  (cost=282695.32..286506.20 rows=29790 width=56) (actual time=613.075..630.379 rows=11167 loops=1)
              Workers Planned: 2
              Workers Launched: 2
              Buffers: shared hit=439 read=92737 written=13
              ->  Partial GroupAggregate  (cost=281695.30..282067.67 rows=14895 width=56) (actual time=598.840..606.992 rows=3722 loops=3)
                    Group Key: b.genres, b.startyear
                    Buffers: shared hit=439 read=92737 written=13
                    ->  Sort  (cost=281695.30..281732.54 rows=14895 width=22) (actual time=598.793..600.313 rows=34494 loops=3)
                          Sort Key: b.genres, b.startyear
                          Sort Method: quicksort  Memory: 3044kB
                          Buffers: shared hit=439 read=92737 written=13
                          Worker 0:  Sort Method: quicksort  Memory: 2177kB
                          Worker 1:  Sort Method: quicksort  Memory: 2980kB
                          ->  Parallel Hash Join  (cost=262037.88..280662.89 rows=14895 width=22) (actual time=405.851..532.884 rows=34494 loops=3)
                                Hash Cond: (r.tconst = b.tconst)
                                Buffers: shared hit=409 read=92737 written=13
                                ->  Parallel Seq Scan on title_ratings r  (cost=0.00..16878.26 rows=665426 width=16) (actual time=0.038..40.404 rows=532341 loops=3)
                                      Buffers: shared read=10224
                                ->  Parallel Hash  (cost=260661.02..260661.02 rows=110149 width=26) (actual time=399.951..399.952 rows=61761 loops=3)
                                      Buckets: 524288  Batches: 1  Memory Usage: 15584kB
                                      Buffers: shared hit=385 read=82513 written=13
                                      ->  Parallel Bitmap Heap Scan on title_basics b  (cost=9575.12..260661.02 rows=110149 width=26) (actual time=38.978..381.595 rows=61761 loops=3)
                                            Recheck Cond: ((titletype = 'movie'::text) AND (startyear >= 2010) AND (startyear <= 2020))
                                            Rows Removed by Index Recheck: 720621
                                            Heap Blocks: exact=14586 lossy=9850
                                            Buffers: shared hit=385 read=82513 written=13
                                            ->  Bitmap Index Scan on idx_basics_type_year_tconst  (cost=0.00..9509.03 rows=264358 width=0) (actual time=29.221..29.221 rows=185282 loops=1)
                                                  Index Cond: ((titletype = 'movie'::text) AND (startyear >= 2010) AND (startyear <= 2020))
                                                  Buffers: shared read=916
Planning:
  Buffers: shared hit=112 read=11
Planning Time: 1.364 ms
JIT:
  Functions: 57
  Options: Inlining false, Optimization false, Expressions true, Deforming true
  Timing: Generation 2.501 ms (Deform 1.175 ms), Inlining 0.000 ms, Optimization 1.899 ms, Emission 27.589 ms, Total 31.989 ms
Execution Time: 654.906 ms
```

### 05. Multi-table Join: Movie Count by Director

#### Query

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT c.directors, COUNT(*) AS film_count
FROM title_crew c
JOIN title_basics b ON c.tconst = b.tconst
WHERE b.titleType = 'movie'
GROUP BY c.directors
ORDER BY film_count DESC
LIMIT 10;
```

#### Result

```plaintext
Limit  (cost=469022.94..469022.97 rows=10 width=21) (actual time=4290.647..4361.172 rows=10 loops=1)
  Buffers: shared hit=9014 read=256106, temp read=59699 written=60432
  ->  Sort  (cost=469022.94..469115.61 rows=37069 width=21) (actual time=4282.684..4353.206 rows=10 loops=1)
        Sort Key: (count(*)) DESC
        Sort Method: top-N heapsort  Memory: 26kB
        Buffers: shared hit=9014 read=256106, temp read=59699 written=60432
        ->  Finalize GroupAggregate  (cost=458830.48..468221.89 rows=37069 width=21) (actual time=4011.786..4320.336 rows=264002 loops=1)
              Group Key: c.directors
              Buffers: shared hit=9014 read=256106, temp read=59699 written=60432
              ->  Gather Merge  (cost=458830.48..467480.51 rows=74138 width=21) (actual time=4011.737..4254.070 rows=365841 loops=1)
                    Workers Planned: 2
                    Workers Launched: 2
                    Buffers: shared hit=9014 read=256106, temp read=59699 written=60432
                    ->  Sort  (cost=457830.45..457923.13 rows=37069 width=21) (actual time=3986.498..4042.498 rows=121947 loops=3)
                          Sort Key: c.directors
                          Sort Method: external merge  Disk: 4064kB
                          Buffers: shared hit=9014 read=256106, temp read=59699 written=60432
                          Worker 0:  Sort Method: external merge  Disk: 4208kB
                          Worker 1:  Sort Method: external merge  Disk: 4568kB
                          ->  Partial HashAggregate  (cost=454646.61..455017.30 rows=37069 width=21) (actual time=3390.560..3470.682 rows=121947 loops=3)
                                Group Key: c.directors
                                Batches: 5  Memory Usage: 8241kB  Disk Usage: 1728kB
                                Buffers: shared hit=8998 read=256106, temp read=58094 written=58823
                                Worker 0:  Batches: 5  Memory Usage: 8241kB  Disk Usage: 1760kB
                                Worker 1:  Batches: 5  Memory Usage: 8241kB  Disk Usage: 3400kB
                                ->  Parallel Hash Join  (cost=241770.34..453153.54 rows=298615 width=13) (actual time=2562.174..3279.311 rows=240605 loops=3)
                                      Hash Cond: (c.tconst = b.tconst)
                                      Buffers: shared hit=8998 read=256106, temp read=57425 written=57476
                                      ->  Parallel Seq Scan on title_crew c  (cost=0.00..139318.33 rows=4922233 width=23) (actual time=0.234..1200.797 rows=3936730 loops=3)
                                            Buffers: shared read=90096
                                      ->  Parallel Hash  (cost=236575.27..236575.27 rows=298806 width=10) (actual time=493.987..493.988 rows=240605 loops=3)
                                            Buckets: 262144  Batches: 8  Memory Usage: 6368kB
                                            Buffers: shared hit=8998 read=166010, temp written=2372
                                            ->  Parallel Seq Scan on title_basics b  (cost=0.00..236575.27 rows=298806 width=10) (actual time=3.048..420.809 rows=240605 loops=3)
                                                  Filter: (titletype = 'movie'::text)
                                                  Rows Removed by Filter: 3696125
                                                  Buffers: shared hit=8998 read=166010
Planning:
  Buffers: shared hit=24 read=16 dirtied=1
Planning Time: 3.723 ms
JIT:
  Functions: 55
  Options: Inlining false, Optimization false, Expressions true, Deforming true
  Timing: Generation 2.207 ms (Deform 0.417 ms), Inlining 0.000 ms, Optimization 1.446 ms, Emission 22.621 ms, Total 26.275 ms
Execution Time: 4363.620 ms
```

### 06. Subquery: Filmography of a Specific Actor

#### Query

```sql
EXPLAIN (ANALYZE, BUFFERS)
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

#### Result

```plaintext
Nested Loop  (cost=1404429.52..1410053.57 rows=668 width=20) (actual time=15412.195..15510.131 rows=1013 loops=1)
  Buffers: shared hit=2482 read=1031237
  InitPlan 1
    ->  Limit  (cost=1000.00..39503.03 rows=1 width=10) (actual time=174.314..174.390 rows=1 loops=1)
          Buffers: shared read=154843
          ->  Gather  (cost=1000.00..232018.18 rows=6 width=10) (actual time=0.753..0.828 rows=1 loops=1)
                Workers Planned: 2
                Workers Launched: 2
                Buffers: shared read=154843
                ->  Parallel Seq Scan on name_basics n  (cost=0.00..231017.58 rows=2 width=10) (actual time=4284.692..4284.692 rows=0 loops=3)
                      Filter: (primaryname = 'Tom Hanks'::text)
                      Rows Removed by Filter: 4864846
                      Buffers: shared read=154843
  ->  HashAggregate  (cost=1364926.05..1364932.72 rows=667 width=10) (actual time=15412.032..15412.324 rows=1013 loops=1)
        Group Key: p.tconst
        Batches: 1  Memory Usage: 129kB
        Buffers: shared read=874827
        ->  Gather  (cost=1000.00..1364924.38 rows=668 width=10) (actual time=496.792..15411.017 rows=1114 loops=1)
              Workers Planned: 2
              Workers Launched: 2
              Buffers: shared read=874827
              ->  Parallel Seq Scan on title_principals p  (cost=0.00..1363857.58 rows=278 width=10) (actual time=306.602..15225.187 rows=371 loops=3)
                    Filter: (nconst = (InitPlan 1).col1)
                    Rows Removed by Filter: 31294650
                    Buffers: shared read=874824
  ->  Index Scan using title_basics_pkey on title_basics b  (cost=0.43..8.42 rows=1 width=30) (actual time=0.096..0.096 rows=1 loops=1013)
        Index Cond: (tconst = p.tconst)
        Buffers: shared hit=2482 read=1570
Planning:
  Buffers: shared hit=36 read=4 dirtied=2
Planning Time: 0.831 ms
JIT:
  Functions: 34
  Options: Inlining true, Optimization true, Expressions true, Deforming true
  Timing: Generation 1.261 ms (Deform 0.505 ms), Inlining 304.825 ms, Optimization 346.915 ms, Emission 83.742 ms, Total 736.744 ms
Execution Time: 15510.881 ms
```


### 07. CTE: Yearly Movie Counts

#### Query

```sql
EXPLAIN (ANALYZE, BUFFERS)
WITH yearly_counts AS (
    SELECT startYear, COUNT(*) AS cnt
    FROM title_basics
    WHERE titleType = 'movie'
    GROUP BY startYear
)
SELECT * FROM yearly_counts WHERE startYear >= 2000 ORDER BY cnt DESC;
```

#### Result

```plaintext
Sort  (cost=250951.76..250952.09 rows=132 width=12) (actual time=562.262..564.314 rows=33 loops=1)
  Sort Key: (count(*)) DESC
  Sort Method: quicksort  Memory: 26kB
  Buffers: shared hit=9937 read=165085
  ->  Finalize GroupAggregate  (cost=250913.67..250947.11 rows=132 width=12) (actual time=562.226..564.304 rows=33 loops=1)
        Group Key: title_basics.startyear
        Buffers: shared hit=9937 read=165085
        ->  Gather Merge  (cost=250913.67..250944.47 rows=264 width=12) (actual time=562.217..564.285 rows=94 loops=1)
              Workers Planned: 2
              Workers Launched: 2
              Buffers: shared hit=9937 read=165085
              ->  Sort  (cost=249913.65..249913.98 rows=132 width=12) (actual time=523.212..523.214 rows=31 loops=3)
                    Sort Key: title_basics.startyear
                    Sort Method: quicksort  Memory: 25kB
                    Buffers: shared hit=9937 read=165085
                    Worker 0:  Sort Method: quicksort  Memory: 25kB
                    Worker 1:  Sort Method: quicksort  Memory: 26kB
                    ->  Partial HashAggregate  (cost=249907.68..249909.00 rows=132 width=12) (actual time=523.189..523.194 rows=31 loops=3)
                          Group Key: title_basics.startyear
                          Batches: 1  Memory Usage: 40kB
                          Buffers: shared hit=9923 read=165085
                          Worker 0:  Batches: 1  Memory Usage: 40kB
                          Worker 1:  Batches: 1  Memory Usage: 40kB
                          ->  Parallel Seq Scan on title_basics  (cost=0.00..248888.72 rows=203792 width=4) (actual time=4.181..497.354 rows=119362 loops=3)
                                Filter: ((startyear >= 2000) AND (titletype = 'movie'::text))
                                Rows Removed by Filter: 3817368
                                Buffers: shared hit=9923 read=165085
Planning Time: 0.094 ms
JIT:
  Functions: 24
  Options: Inlining false, Optimization false, Expressions true, Deforming true
  Timing: Generation 1.287 ms (Deform 0.535 ms), Inlining 0.000 ms, Optimization 0.695 ms, Emission 11.857 ms, Total 13.838 ms
Execution Time: 564.843 ms
```

### 08. Window Function: Top Rated Movie by Year

#### Query

```sql
EXPLAIN (ANALYZE, BUFFERS)
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

#### Result

```plaintext
Subquery Scan on sub  (cost=272754.08..285209.02 rows=425 width=38) (actual time=951.991..1065.882 rows=131 loops=1)
  Filter: (sub.rn = 1)
  Buffers: shared hit=10402 read=175022, temp read=12359 written=12439
  ->  WindowAgg  (cost=272754.08..284146.05 rows=85037 width=38) (actual time=951.988..1065.864 rows=131 loops=1)
        Run Condition: (row_number() OVER (?) <= 1)
        Buffers: shared hit=10402 read=175022, temp read=12359 written=12439
        ->  Gather Merge  (cost=272753.95..282657.91 rows=85037 width=30) (actual time=951.958..1052.392 rows=333293 loops=1)
              Workers Planned: 2
              Workers Launched: 2
              Buffers: shared hit=10402 read=175022, temp read=12359 written=12439
              ->  Sort  (cost=271753.92..271842.50 rows=35432 width=30) (actual time=939.214..957.083 rows=111098 loops=3)
                    Sort Key: b.startyear, r.averagerating DESC
                    Sort Method: external merge  Disk: 4112kB
                    Buffers: shared hit=10402 read=175022, temp read=12359 written=12439
                    Worker 0:  Sort Method: external merge  Disk: 4296kB
                    Worker 1:  Sort Method: external merge  Disk: 4328kB
                    ->  Parallel Hash Join  (cost=241902.54..269076.55 rows=35432 width=30) (actual time=748.478..864.025 rows=111098 loops=3)
                          Hash Cond: (r.tconst = b.tconst)
                          Buffers: shared hit=10278 read=175020, temp read=10767 written=10844
                          ->  Parallel Seq Scan on title_ratings r  (cost=0.00..16878.26 rows=665426 width=16) (actual time=0.047..51.108 rows=532341 loops=3)
                                Buffers: shared hit=193 read=10031
                          ->  Parallel Hash  (cost=236575.27..236575.27 rows=262262 width=34) (actual time=556.908..556.909 rows=205074 loops=3)
                                Buckets: 131072  Batches: 8  Memory Usage: 6240kB
                                Buffers: shared hit=10019 read=164989, temp written=3560
                                ->  Parallel Seq Scan on title_basics b  (cost=0.00..236575.27 rows=262262 width=34) (actual time=5.507..495.970 rows=205074 loops=3)
                                      Filter: ((startyear IS NOT NULL) AND (titletype = 'movie'::text))
                                      Rows Removed by Filter: 3731656
                                      Buffers: shared hit=10019 read=164989
Planning:
  Buffers: shared hit=27
Planning Time: 0.329 ms
JIT:
  Functions: 42
  Options: Inlining false, Optimization false, Expressions true, Deforming true
  Timing: Generation 1.721 ms (Deform 0.814 ms), Inlining 0.000 ms, Optimization 0.943 ms, Emission 15.630 ms, Total 18.294 ms
Execution Time: 1067.106 ms
```


