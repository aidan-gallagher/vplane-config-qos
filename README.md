# Overview

This package has the Vyatta configuration and operational templates and scripts for dataplane Qos.

# Environment
## Dependencies
This repository contains 3 types of dependencies.
#### **Debian build packaging dependencies**
Needed on the host machine to package the scripts into .deb files.
Located in the [debian control file](debian/control) under the `Build-Depends:` section.
#### **Developer dependencies**
Needed on the host machine to run quality checks on the source code.
Located in the [requirements file](dev-requirements.txt).
#### **Debian deployed dependencies**
Needed on the target machine.
Located in the [debian control file](debian/control) under the packages `Depends:` section.

## Container
A containerized environment is provided with all the host dependencies installed.

The docker build and run commands are wrapped in the makefile for ease.


1. Build the image
```
make build-container
```
2. Run the container
```
make run-container
```

# Code Checks
This project uses a makefile as a task runner. To see the full list of tasks, from the project root directory, type `make` `[space]` `[tab]`.

When opening a pull request you should ensure all stages are successful. To do this run
```
make all
```


