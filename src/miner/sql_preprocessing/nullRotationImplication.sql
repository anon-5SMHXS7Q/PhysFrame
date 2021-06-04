use transforms;

drop table zeroRotNames_m;
drop table zeroRotNamesScored_m;
drop table zeroRotPairs_m;
drop table zeroRotPairsScored_m;

CREATE TABLE IF NOT EXISTS zeroRotNames_m AS SELECT name, COUNT(*) AS zCount FROM transforms WHERE ((r=0 AND p=0 and y=0 and isQuat=0) OR (qx=0 AND qy=0 AND qz=0 AND isQuat=1)) AND isMature GROUP BY name ORDER BY zCount DESC;
CREATE TABLE IF NOT EXISTS zeroRotPairs_m AS SELECT parent,child, COUNT(*) AS zCount FROM transforms WHERE ((r=0 AND p=0 and y=0 and isQuat=0) OR (qx=0 AND qy=0 AND qz=0 AND isQuat=1)) AND isMature GROUP BY child, parent ORDER BY zCount DESC;

CREATE TABLE IF NOT EXISTS zeroRotNamesScored_m AS 
SELECT A.*, B.count AS totalCount
FROM zeroRotNames_m A
LEFT JOIN nameCounts_m B
ON BINARY A.name=B.name
ORDER BY A.zCount DESC;
ALTER TABLE zeroRotNamesScored_m
ADD COLUMN zScore FLOAT(20,10);
UPDATE zeroRotNamesScored_m SET zScore = ( ((zCount)/totalCount) -  0.85 )/(SQRT( 0.85*(1- 0.85)/totalCount));
ALTER TABLE zeroRotNamesScored_m ORDER BY zScore DESC;

SELECT * FROM zeroRotNamesScored_m LIMIT 10;

CREATE TABLE IF NOT EXISTS zeroRotPairsScored_m AS 
SELECT A.*, B.count AS totalCount
FROM zeroRotPairs_m A
LEFT JOIN pairCts_m B
ON BINARY A.parent=B.parent AND BINARY A.child=B.child
ORDER BY A.zCount DESC;
ALTER TABLE zeroRotPairsScored_m
ADD COLUMN zScore FLOAT(20,10);
UPDATE zeroRotPairsScored_m SET zScore = ( ((zCount)/totalCount) -  0.85 )/(SQRT( 0.85*(1- 0.85)/totalCount));
ALTER TABLE zeroRotPairsScored_m ORDER BY zScore DESC;
SELECT * FROM zeroRotPairsScored_m LIMIT 10;