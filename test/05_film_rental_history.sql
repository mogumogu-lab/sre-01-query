-- 5. 특정 영화의 대여 이력 (JOIN)
\set random_film_id random(1, 1000)
SELECT f.title, r.rental_date, c.first_name, c.last_name
FROM rental r
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
JOIN customer c ON r.customer_id = c.customer_id
WHERE f.film_id = :random_film_id
ORDER BY r.rental_date DESC
LIMIT 10;
