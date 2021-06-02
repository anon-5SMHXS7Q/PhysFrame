# PhysFrame

Artifact for "PHYSFRAME: Type Checking Physical Frames of Reference for Robotic Systems".


### Summary


PHYSFRAME is a static analysis tool for detecting reference frame inconsistencies and violations of common practices (i.e., implicit frame conventions) in C/C++ projects that build against the [Robot Operating System](http://www.ros.org/). It requires nothing from the developers running the tool on their project. The tool automatically models the project, and checks for problems.


### Contents

This repository contains the following files and folders:

* README.md : This file. 
* LICENSE.txt : BSD-2-Clause license. **TODO**
* STATUS.txt : Describes the ACM artifact badges sought for this artifact.
* REQUIREMENTS.txt : Describes the hardware and software requirements.
* INSTALL.txt : Describes how to install PHYSFRAME using Docker and a minimal working example.
* Dockerfile : a Docker install file for PHYSFRAME.
* requirements.txt : List of python dependencies required by PHYSFRAME. Referenced by the Dockerfile.
* src/ : The python source code for PHYSFRAME, files containing implicit frame conventions, and the binary file of CPPCheck 1.80.
* data/ : C/C++ projects used to evaluate PHYSFRAME.


### Credits

* [CPPCheck](http://cppcheck.sourceforge.net/)
* [NetworkX](https://networkx.github.io/)
* [SciPy](https://www.scipy.org/)
* [lxml](https://lxml.de/)
* [Phys](https://github.com/unl-nimbus-lab/phys)


