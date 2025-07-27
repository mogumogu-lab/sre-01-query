-- 8. 고객 정보 주소 변경 (UPDATE)
\set random_id random(1, 599)
UPDATE customer SET address_id = (
    SELECT address_id FROM address
    OFFSET floor(random() * (SELECT count(*) FROM address))
    LIMIT 1
) WHERE customer_id = :random_id;