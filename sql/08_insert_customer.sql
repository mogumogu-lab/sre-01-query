-- 9. 신규 고객 등록 (INSERT)
\set random_id random(1, 1000000)
\set store_id random(1, 2)
INSERT INTO customer (store_id, first_name, last_name, email, address_id, active)
VALUES (
  :store_id,
  'first_' || :random_id,
  'last_'  || :random_id,
  'test'   || :random_id || '@example.com',
  (SELECT address_id FROM address OFFSET floor(random() * (SELECT count(*) FROM address)) LIMIT 1),
  1
);