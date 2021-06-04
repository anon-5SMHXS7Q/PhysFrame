drop table nameCounts_M, pairCts_M, parentFreq_M, childFreq_M, dualTransform_M;

CREATE TABLE IF NOT EXISTS nameCounts_M AS SELECT name, COUNT(DISTINCT file_id) AS count FROM transforms WHERE isMature GROUP BY name ORDER BY count DESC;
CREATE TABLE IF NOT EXISTS pairCts_M AS SELECT parent, child, COUNT(DISTINCT file_id) AS count FROM transforms WHERE isMature GROUP BY parent, child ORDER BY count DESC;

CREATE TABLE IF NOT EXISTS parentFreq_M AS SELECT parent, COUNT(DISTINCT file_id) AS count FROM transforms WHERE isMature GROUP BY parent ORDER BY COUNT(*) DESC;

CREATE TABLE IF NOT EXISTS childFreq_M AS SELECT child, COUNT(DISTINCT file_id) AS count FROM transforms WHERE isMature GROUP BY child ORDER BY count DESC;

CREATE TABLE IF NOT EXISTS dualTransform_M AS 
SELECT A.name AS first_name, A.parent AS first_parent, A.child AS first_child, B.name AS second_name, B.parent AS second_parent, B.child AS second_child, A.file_id, A.isOld, A.isMature
FROM transforms A
INNER JOIN transforms B
ON A.file_id = B.file_id AND A.isOld = B.isOld AND (A.parent<>B.parent OR A.child<>B.child)
WHERE A.isMature
ORDER BY A.file_id;