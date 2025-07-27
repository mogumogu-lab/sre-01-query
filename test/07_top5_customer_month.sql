-- 7. 한 달 동안 대여 건수가 많은 고객 Top 5
SELECT c.customer_id, c.first_name, c.last_name, COUNT(*) AS rental_count
FROM rental r
JOIN customer c ON r.customer_id = c.customer_id
WHERE r.rental_date >= now() - INTERVAL '1 month'
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY rental_count DESC
LIMIT 5;