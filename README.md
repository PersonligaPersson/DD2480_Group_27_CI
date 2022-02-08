# DD2480_Group_27_CI
A repository for the continuous integration project for group 27 as part of the course DD2480 at KTH.

## Getting Started

### Virtual environment
Create a virtual environment that the application can be run inside using the command,

```bash
$ python -m venv venv
```

### Install Dependencies

To install dependencies run,
```bash
$ pip install -r requirements.txt
```

### Adding a dependency

If you add a dependency while developing then you need to issue the command,

```bash
$ pip freeze > requirements.txt
```
to add it to the manifest file.

### Running the application

To run the application simply issue the command,

```bash
$ python run.py
```
And the server will start up on `localhost:8080`
