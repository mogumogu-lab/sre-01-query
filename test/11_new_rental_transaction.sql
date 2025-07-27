-- 11. 신규 대여 트랜잭션
BEGIN;

INSERT INTO rental (rental_date, inventory_id, customer_id, staff_id)
VALUES (now(), :inventory_id, :customer_id, :staff_id);

UPDATE inventory SET last_update = now() WHERE inventory_id = :inventory_id;

COMMIT;