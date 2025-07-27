-- 1. 고객 정보 랜덤 조회 (PK 접근)
\set random_id random(1, 599)
SELECT * FROM customer WHERE customer_id = :random_id;