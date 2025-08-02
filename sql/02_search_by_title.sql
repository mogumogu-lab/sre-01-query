-- 2. 영화 제목으로 검색 (ILIKE)
\set alpha_id random(65, 90)
SELECT * FROM film WHERE title ILIKE '%' || chr(:alpha_id) || '%';