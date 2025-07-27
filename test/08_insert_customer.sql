-- 9. 신규 고객 등록 (INSERT)
INSERT INTO customer (store_id, first_name, last_name, email, address_id, active, create_date)
VALUES (:store_id, :first_name, :last_name, :email, :address_id, 1, now());