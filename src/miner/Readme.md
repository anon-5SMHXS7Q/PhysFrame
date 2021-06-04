# Miner
The convention miner has two primary components:
  1. SQL Preprocessor
  2. Convention Generator  

## SQL Preprocessor:
The SQL Preprocessor is provided with a SQL table (called `transforms`) which represents a corpus of static transforms collected from the launch files of a set of ROS repositories. Each row in the table represents a single static transform and contains the following fields:
```
1. file_id: A unique identifier for the file the transform was taken from
2. repo_name: The name of the respository the transform was taken from
3. name: The name of the transform
4. parent: The name of the parent frame of the transform
5. child: The name of the child frame of the transform
6. dx: The x displacement of the transform
7. dy: The y displacement of the transform
8. dz: The z displacement of the transform
9. isQuat: A boolean value which is true if the transform specified rotation as a quaternion and false if the rotation is specified as roll, pitch, yaw.
10. r: The roll rotation of a transform which uses roll, pitch, yaw
11. p: The pitch rotation of a transform which uses roll, pitch, yaw
12. y: The yaw rotation of a transform which uses roll, pitch, yaw
13. qx: The x value of the rotation quaternion if that is the form of the rotation
14. qy: The y value of the rotation quaternion if that is the form of the rotation
15. qz: The z value of the rotation quaternion if that is the form of the rotation
16. qw: The w value of the rotation quaternion if that is the form of the rotation
17. isMature: A boolean flag for if the repository which the transform came from is mature i.e. has at least 30 commits.
```

To make use of the SQL preprocessor, within a SQL process with access to the `transforms` table, execute the `generate.sql` script.

This will create several SQL tables:
  1. `name_dual_freq_3`: Each row contains a pair of transform names which were both present in at least a single file together. There is a `z_score` field which may be used to determine the strength of the implication that the existence of a transform named `first_name` implies the existence of a transform named `second_name` in the file.
  2. `sig_dual_freq3`: Each row contains a pair of transforms (represented by the ordered pair (parent_name, child_name)) which were both present in at least a single file together. There is a `z_score` field which may be used to determine the strength of the implication that the existence of a transform (`first_parent`, `first_child`) implies the existence of a transform (`second_parent`, `second_child`) in the file.
  3. `zero_names_scored`: Each row contains a transform (represented by its name) which was present at least once in a file with a zero displacement. There is a `z_score` field which may be used to determine the strength of the implication that the given transform has zero displacement.
  4. `zero_pairs_scored`: Each row contains a transform (represented by the ordered pair (parent_name, child_name)) which was present at least once in a file with a zero displacement. There is a `z_score` field which may be used to determine the strength of the implication that the given pair of (`parent`, `child`) has zero displacement.
  5. `zeroRotNamesScored_m`: Each row contains a transform (represented by its name) which was present at least once in a file with a zero rotation. There is a `z_score` field which may be used to determine the strength of the implication that the given transform has zero rotation.
  6. `zeroRotPairsScored_m`: Each row contains a transform (represented by the ordered pair (parent_name, child_name)) which was present at least once in a file with a zero rotation. There is a `z_score` field which may be used to determine the strength of the implication that the given pair of (`parent`, `child`) has zero rotation.

## Convention Generator
The Convention Generator is a Python script (`linterGenerator.py`) which uses the aforementioned SQL tables containing the scored conventions in conjunction with a Jinja template to create a new Python script which can be programmatically used to reference the convention list given a `z_score` threshold.

To make use of `linterGenerator.py`, simply execute the script, which will print the linting script to the console and use a default `z_score` threshold of `1.0` to determine which mined implications are strong enough to support linting for them. The script also takes two optional positional command line args. The first is a path which the linting script will be written to instead of to the console, and the second is a floating point threshold to use for the `z_score` instead of the default. `linter_rules_1.0.py` is provided as an example. It was generated with the following:
```
python .\linterGenerator.py linter_rules_1.0.py 1.0
```
