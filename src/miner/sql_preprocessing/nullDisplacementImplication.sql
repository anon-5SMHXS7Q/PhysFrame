use transforms;

drop table zero_names;
drop table zero_names_scored;

drop table zero_pairs;
drop table zero_pairs_scored;

drop table full_name_counts, full_pair_counts;

CREATE TABLE IF NOT EXISTS full_name_counts
AS SELECT name, COUNT(*) AS count
FROM transforms
WHERE isMature
GROUP BY name
ORDER BY count DESC;

CREATE TABLE IF NOT EXISTS full_pair_counts
AS SELECT parent, child, COUNT(*) AS count
FROM transforms
WHERE isMature
GROUP BY parent, child
ORDER BY count DESC;

CREATE TABLE IF NOT EXISTS zero_names
AS SELECT name, COUNT(DISTINCT file_id) AS zCount
FROM transforms
WHERE (dx=0 AND dy=0 AND dz=0) AND isMature GROUP BY name ORDER BY zCount DESC;

CREATE TABLE IF NOT EXISTS zero_pairs
AS SELECT parent, child, COUNT(DISTINCT file_id) AS zCount
FROM transforms
WHERE (dx=0 AND dy=0 AND dz=0) AND isMature GROUP BY child, parent ORDER BY zCount DESC;

CREATE TABLE IF NOT EXISTS zero_names_scored AS 
SELECT A.*, B.count AS totalCount
FROM zero_names A
LEFT JOIN full_name_counts B
ON BINARY A.name=B.name
ORDER BY A.zCount DESC;
ALTER TABLE zero_names_scored
ADD COLUMN zScore FLOAT(20,10);
UPDATE zero_names_scored SET zScore = ( ((zCount)/totalCount) -  0.85 )/(SQRT( 0.85*(1- 0.85)/totalCount));
ALTER TABLE zero_names_scored ORDER BY zScore DESC;

CREATE TABLE IF NOT EXISTS zero_pairs_scored AS 
SELECT A.*, B.count AS totalCount
FROM zero_pairs A
LEFT JOIN full_pair_counts B
ON BINARY A.parent=B.parent AND BINARY A.child=B.child
ORDER BY A.zCount DESC;
ALTER TABLE zero_pairs_scored
ADD COLUMN zScore FLOAT(20,10);
UPDATE zero_pairs_scored SET zScore = ( ((zCount)/totalCount) -  0.85 )/(SQRT( 0.85*(1- 0.85)/totalCount));
ALTER TABLE zero_pairs_scored ORDER BY zScore DESC;
SELECT * FROM zero_pairs_scored LIMIT 10;