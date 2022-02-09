from http.server import BaseHTTPRequestHandler
import subprocess # subprocess

"""
The purpose of this function is to trigger a shell script that lints the
code in the project.
Note: This should be update so that it runs the linting process on the
correct code. As it is it will lint all py files.

A shellscript must be explicitly set to executable using the chmod command.
Example: chmod +x ./runLint.sh
"""
def run_lint():
    runLintPath = "../shellscripts/runLint.sh"
    subprocess.run([runLintPath, ""], shell=True)

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
