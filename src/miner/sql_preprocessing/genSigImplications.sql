use transforms;

drop table sig_dual_freq, sig_dual_freq2, sig_dual_freq3;

CREATE TABLE IF NOT EXISTS sig_dual_freq AS
SELECT first_parent,first_child, second_parent,second_child, COUNT(DISTINCT file_id) AS both_count 
FROM dualTransform_M
GROUP BY first_parent,first_child, second_parent,second_child;

CREATE TABLE IF NOT EXISTS sig_dual_freq2 AS 
SELECT  A.first_parent,A.first_child, A.second_parent, A.second_child, A.both_count, B.count AS left_count
FROM sig_dual_freq A
LEFT JOIN pairCts_M B
ON BINARY A.first_parent=B.parent AND BINARY A.first_child=B.child
ORDER BY A.both_count DESC;

CREATE TABLE IF NOT EXISTS sig_dual_freq3 AS 
SELECT  A.first_parent,A.first_child, A.second_parent, A.second_child, A.both_count,A.left_count, B.count AS right_count
FROM sig_dual_freq2 A
LEFT JOIN pairCts_M B
ON BINARY A.second_parent=B.parent AND BINARY A.second_child=B.child
ORDER BY A.both_count DESC;

ALTER TABLE sig_dual_freq3
ADD COLUMN zScore FLOAT(20,10);

UPDATE sig_dual_freq3 SET zScore = ( ((both_count)/left_count) -  0.85 )/(SQRT( 0.85*(1- 0.85)/left_count));
ALTER TABLE sig_dual_freq3 ORDER BY zScore DESC;