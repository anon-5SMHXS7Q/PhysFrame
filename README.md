# PhysFrame

Artifact for "PHYSFRAME: Type Checking Physical Frames of Reference for Robotic Systems".


### Summary


PHYSFRAME is a static analysis tool for detecting reference frame inconsistencies and violations of common practices (i.e., implicit frame conventions) in C/C++ projects that build against the [Robot Operating System](http://www.ros.org/). It requires nothing from the developers running the tool on their project. The tool automatically models the project, and checks for problems.


### Contents

This repository contains the following files and folders:

* README.md : This file. 
* LICENSE.txt : BSD 2-Clause license.
* STATUS.txt : Describes the ACM artifact badges sought for this artifact.
* REQUIREMENTS.md : Describes the hardware and software requirements.
* INSTALL.txt : Describes how to install PHYSFRAME using Docker and a minimal working example.
* HOWTO.txt: Describes how to use PHYSFRAME with the provided data.
* Dockerfile : a Docker install file for PHYSFRAME.
* requirements.txt : List of python dependencies required by PHYSFRAME. Referenced by the Dockerfile.
* src/ : The python source code for PHYSFRAME, files containing implicit frame conventions.
* data/ : C/C++ projects used to evaluate PHYSFRAME.


### Credits

* [CPPCheck](https://github.com/danmar/cppcheck)
* [NetworkX](https://networkx.github.io/)
* [SciPy](https://www.scipy.org/)
* [lxml](https://lxml.de/)
* [cmakelists_parsing](https://github.com/ijt/cmakelists_parsing)
* [Phys](https://github.com/unl-nimbus-lab/phys)


