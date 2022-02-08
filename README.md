# Continuous Integration

A project repository for group 27 for lab 2 of the course DD2480 at KTH. The task is to implement a _continuous integration_ (CI) server.

The CI server works for Python projects and performs the following tasks every time the project is updated:

- Does a static syntax check on the Python code
- Executes automated tests on the Python program
- Informs the project members on the build results by updating commit statuses in the repo
- Saves the history of past builds, where each build history can be accessed through a separate URL

The flow chart below illustrates the interaction between Github and the CI server:

[insert flow chart]

# Getting Started

## Virtual environment
Create a virtual environment that the application can be run inside using the command,

```bash
$ python -m venv venv
```

## Install Dependencies

To install dependencies run,
```bash
$ pip install -r requirements.txt
```

## Adding a dependency

If you add a dependency while developing then you need to issue the command,

```bash
$ pip freeze > requirements.txt
```
to add it to the manifest file.

## Running the application

To run the application simply issue the command,

```bash
$ python run.py
```
And the server will start up on `localhost:8080`

# Contributions

TODO

## Contributors

- Arvid Gotthard (gotthard@kth.se)
- Max Persson (maxper@kth.se)
- Bastien Faivre (faivre@kth.se)
- Amanda Strömdahl (astromd@kth.se)