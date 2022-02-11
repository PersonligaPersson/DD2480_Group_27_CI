import json
import os
from http.server import HTTPServer
from dotenv import load_dotenv
import requests
from .handler import CIServerHandler
import time


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
            return CIServerHandler(self.update_commit_status, self.make_log_title, self.make_log, *args)

        self.handler = handler_fn
        self.address = address
        self.port = port

    """Runs the server.
    """
    def run(self):
        httpd = HTTPServer((self.address, self.port), self.handler)
        try:
            print("serving CI server at %s:%d..." % (self.address, self.port))
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nclosing server...")
            httpd.server_close()


    """Updates the commit status of a given commit.
    :param url: github url to the status of a commit in a repo
    :param sha: identifier of commit
    :param status: status to assign to the commit
    """
    def update_commit_status(self, url, sha, status):
        TOKEN = os.getenv("GITHUB_TOKEN")
        HEADERS = {"Authorization": "token " + TOKEN}
        URL = url + sha

        statusString = "success"
        if not status:
            statusString = "failure"

        DATA = {"state": statusString}
        response = requests.post(url=URL, data=json.dumps(DATA), headers=HEADERS)
        print(response)

        # LOGGING

    """Generates a unique title for a build log file.
    :returns: title of a build log file
    """
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

    """Logs output of tests and lint in a build log file.
    """
    def make_log(self, lint_output, pytest_output):
        with open(f"logfiles/{self.make_log_title()}", "w") as f:
            f.write(
                f"=== LINT OUTPUT ===\n{lint_output}\n\n=== PYTEST OUTPUT ===\n{pytest_output}\n"
            )

