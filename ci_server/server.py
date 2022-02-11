from http.server import HTTPServer
import json
import time
import requests
from .handler import CIServerHandler


class CIServer:
    """
    CIServer

    Attributes:
        handler: A function that returns a CIServerHandler.
        address: The address that the server runs on.
        port:  The port that the server runs on.
    """

    def __init__(self, address, port):
        # closure that will instantiate a instance a CIServerHandler for us.
        def handler_fn(*args):
            return CIServerHandler(
                self.update_commit_status, self.make_log_title, self.make_log, *args
            )

        self.handler = handler_fn
        self.address = address
        self.port = port

    # run server
    def run(self):
        httpd = HTTPServer((self.address, self.port), self.handler)
        try:
            print("serving CI server at %s:%d..." % (self.address, self.port))
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nclosing server...")
            httpd.server_close()

    def update_commit_status(self, url, sha, status, TOKEN):
        HEADERS = {"Authorization": "token " + TOKEN}
        URL = url + sha

        statusString = "success"
        if not status:
            statusString = "failure"

        DATA = {"state": statusString}
        response = requests.post(url=URL, data=json.dumps(DATA), headers=HEADERS)
        print(response.json())

        # LOGGING

    # The purpose of this function is to generate a unique identifier that serves
    # as the build log name.
    # Note: This would fail if the number of total builds would reach maxint.
    def make_log_title(self):
        tob = time.localtime()
        bString = "X"
        bDatPath = "logfiles/buildData.dat"
        newBuildNum = -1

        # Format the new build number.
        with open(bDatPath) as f:
            newBuildNum = int(f.read()[:-1]) + 1

        # Generate a build log string.
        bString = f"Build_{newBuildNum}_{tob.tm_year}_{tob.tm_mon}_{tob.tm_mday}_{tob.tm_hour}.txt"

        with open(bDatPath, "w") as f:
            f.truncate(0)
            f.write(str(newBuildNum) + "\n")

        return bString

    # The purpose of this function is to log the output of the tests and the linting.
    # Creates a new .txt file with the output of the linter and the tests.
    def make_log(self, lint_output, pytest_output):
        with open(f"logfiles/{self.make_log_title()}", "w") as f:
            f.write(
                f"=== LINT OUTPUT ===\n{lint_output}\n\n=== PYTEST OUTPUT ===\n{pytest_output}\n"
            )
