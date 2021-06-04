use transforms;

drop table name_dual_freq, name_dual_freq_2, name_dual_freq_3;

CREATE TABLE IF NOT EXISTS name_dual_freq AS
SELECT first_name,second_name, COUNT(DISTINCT file_id) AS both_count 
FROM dualTransform_M
GROUP BY first_name,second_name;

CREATE TABLE IF NOT EXISTS name_dual_freq_2 AS 
SELECT  A.first_name, A.second_name, A.both_count, B.count AS left_count
FROM name_dual_freq A
LEFT JOIN nameCounts_M B
ON BINARY A.first_name=B.name
ORDER BY A.both_count DESC;

CREATE TABLE IF NOT EXISTS name_dual_freq_3 AS 
SELECT  A.first_name, A.second_name, A.both_count, A.left_count, B.count AS right_count
FROM name_dual_freq_2 A
LEFT JOIN nameCounts_M B
ON BINARY A.second_name=B.name
ORDER BY A.both_count DESC;

ALTER TABLE name_dual_freq_3
ADD COLUMN z_score FLOAT(20,10);
UPDATE name_dual_freq_3 SET z_score = ( ((both_count)/left_count) -  0.85 )/(SQRT( 0.85*(1- 0.85)/left_count));
ALTER TABLE name_dual_freq_3 ORDER BY z_score DESC;