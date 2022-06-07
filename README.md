# GF2 - Software

This repository contains files produced by team 19 for the Cambridge University 
Engineering Tripos Part IIA Software project.

## Setup

To setup and run the project, first create a virtual environment and install all the 
packages that are required.

```bash
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ python3 -m pip install -r requirements.txt
(venv) $ python3 logsim.py <filepath>.txt
```

## Code Style

All of the codebase is automatically formatted using [*Black*]
(https://github.com/psf/black). This is an opinionated formatter, which ensures that 
all of our code obeys the same formatting rules. *Black* is largely PEP-8 compliant, 
with some additional PEP-8 violations being caught with flake8 and pydocstyle.

Pre-commits have been used to ensure that, as code is being commited to the main 
branch, it is being automatically formatted.

The *Black* line length is set to 88 characters. In some cases, line length was 
exceeded, as breaking a string into multiple lines did not increase readability. This 
is especially true in `parse.py`, where the conditional logic is highly nested such 
that a strict line length limit would overly constrain the string formatting.