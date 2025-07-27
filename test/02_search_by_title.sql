-- 2. 영화 제목으로 검색 (LIKE)
SELECT * FROM film WHERE title ILIKE '%' || :keyword || '%';