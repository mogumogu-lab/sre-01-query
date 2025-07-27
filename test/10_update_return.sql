-- 10. 대여 반납 처리 (UPDATE)
UPDATE rental SET return_date = now() WHERE rental_id = :random_rental_id;
