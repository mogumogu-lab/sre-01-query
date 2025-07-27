-- 4. 고객별 전체 대여 건수
SELECT customer_id, COUNT(*) AS rental_count FROM rental GROUP BY customer_id;
