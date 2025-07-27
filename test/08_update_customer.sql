-- 8. 고객 정보 주소 변경 (UPDATE)
UPDATE customer SET address_id = :new_address_id WHERE customer_id = :random_id;