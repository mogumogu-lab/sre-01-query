-- 3. 고객별 마지막 주문 내역
SELECT * FROM rental WHERE customer_id = :random_id ORDER BY rental_date DESC LIMIT 1;