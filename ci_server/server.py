from http.server import BaseHTTPRequestHandler
import subprocess # subprocess

import time

# The purpose of this function is to generate a unique identifier that serves
# as the build log name.
# Note: This would fail if the number of total builds would reach maxint.
def make_log_title():
    tob = time.localtime()
    bString = "X"
    bDatPath = "../logfiles/buildData.dat"
    newBuildNum = -1

    # Format the new build number.
    with open(bDatPath) as f:
        newBuildNum = int(f.read()[:-1])+1

    # Generate a build log string.
    bString = f"Build_{newBuildNum}_{tob.tm_year}_{tob.tm_mon}_{tob.tm_mday}_{tob.tm_hour}.txt"

    with open(bDatPath, "w") as f:
        f.truncate(0)
        f.write(str(newBuildNum)+'\n')

    return bString

# The purpose of this function is to log the output of the tests and the linting.
# Creates a new .txt file with the output of the linter and the tests.
def make_log(lint_output, pytest_output):
    with open(f"../logfiles/{make_log_title()}", "w") as f:
        f.write(f"=== LINT OUTPUT ===\n{lint_output}\n\n=== PYTEST OUTPUT ===\n{pytest_output}\n")

# The purpose of this function is to trigger a shell script that lints the
# code in the project.
# Note: This should be update so that it runs the linting process on the
# correct code. As it is it will lint all py files.

# A shellscript must be explicitly set to executable using the chmod command.
# Example: chmod +x ./runLint.sh
def run_lint():
    runLintPath = "../shellscripts/runLint.sh"
    proc = subprocess.run([runLintPath, ""], shell=True, check=True)
    return proc.stdout

class CIServer(BaseHTTPRequestHandler):
    """
    TODO: implement the CI server, this is just a placeholder.
    """
    def do_GET(self):
        if self.path == "/":
            self.path = "../static/ci_server/index.html"
        try:
            file = open(self.path[1:]).read()
            self.send_response(200)
        except FileNotFoundError:
            file = "File not found"
            self.send_response(404)

        self.end_headers()
        self.wfile.write(bytes(file, "utf8"))
        # TODO: implement logic for serving files here

    def do_POST(self):
        # TODO: implement CI logic here
        self.send_response(404)
        self.end_headers()
