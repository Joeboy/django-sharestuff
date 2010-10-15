-- DROP FUNCTION IF EXISTS sort_distance;
-- DELIMITER //
-- CREATE FUNCTION sort_distance (lat1 DOUBLE, lon1 DOUBLE, lat2 DOUBLE, lon2 DOUBLE)
-- RETURNS DOUBLE
-- DETERMINISTIC
-- BEGIN
-- -- The idea here was to come up with something computationally cheap that
-- -- would work well enough for sorting. Unfortunately I ran out of time to get it
-- -- working properly.
-- DECLARE a DOUBLE;
-- DECLARE b DOUBLE;
-- SET a = 0.603 * (lat2 - lat1);
-- SET b = 0.603 * (lon2 - lon1) * cos(lat1/0.5);
-- RETURN sqrt(a * a + b * b);
-- END//
-- 
DELIMITER //
DROP FUNCTION IF EXISTS distance//
CREATE FUNCTION distance (lon1 DOUBLE, lat1 DOUBLE, lon2 DOUBLE, lat2 DOUBLE)
RETURNS DOUBLE
DETERMINISTIC
BEGIN
-- Return a fairly accurate distance calculation using the haversine formula
DECLARE dlat DOUBLE;
DECLARE dlon DOUBLE;
SET dlat = lat2 - lat1;
SET dlon = lon2 - lon1;
RETURN 6371 * 2 * ASIN(SQRT(POWER(SIN(dlat/2),2) + COS(lat1) * COS(lat2) * power(SIN(dlon/2), 2)));
END//
DELIMITER ;//
-- There's a potential optimization by only calculating accurate distances for questas within a sensible area:
-- DROP PROCEDURE IF EXISTS fetch_nearby_results;
-- CREATE PROCEDURE fetch_nearby_results (IN mylon DOUBLE, IN mylat DOUBLE, IN dist INT, IN orderclause VARCHAR(100), IN whereclause VARCHAR(1024), IN maxresults INT)
-- BEGIN 
-- declare lon1 float;  declare lon2 float;
-- declare lat1 float; declare lat2 float;
-- 
-- -- calculate a sensible rectangle to limit the number of hard calculations we have to do
-- set lon1 = mylon-dist/abs(cos(mylat)*69);
-- set lon2 = mylon+dist/abs(cos(mylat)*69);
-- set lat1 = mylat-(dist/69);
-- set lat2 = mylat+(dist/69);
-- 
-- -- evil query of doom
-- SET @stmt_text=CONCAT("SELECT *, 3956 * 2 * ASIN(SQRT(POWER(SIN((", mylat, "-lat)*pi()/180/2),2) + COS(lat*pi()/180)*COS(", mylat, "*pi()/180)*POWER(SIN((", mylon, "-lon)*pi()/180/2), 2) )) AS distance FROM tbl_request WHERE tbl_request.lon between ",lon1," and ",lon2," AND tbl_request.lat between ",lat1," AND ",lat2, " AND ", whereclause, " HAVING distance < ",dist," ORDER BY ", orderclause, " LIMIT ", maxresults, ";");
-- 
-- PREPARE stmt FROM @stmt_text;
-- EXECUTE stmt;
-- DEALLOCATE PREPARE stmt; 
-- 
-- END
-- DELIMITER ;//
-- -- call fetch_nearby_results(-1.5127, 0.6304, 25, "distance", 10);
