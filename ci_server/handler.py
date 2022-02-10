import sys
from io import StringIO
import subprocess
import hmac
import hashlib
import time
import os
import json
from http.server import BaseHTTPRequestHandler
import pytest

# macros used for error status
NO_ERROR = 0
ERROR = 1

PATH_TO_CLONED_BRANCHES = "branches"


class CIServerHandler(BaseHTTPRequestHandler):

    """
    Custom HTTP handler that handles post request from webhook on Github.
    """

    def __init__(self, update_commit_status_fn, *args):
        # We assign the function that updates the commit statuses to a class member.
        self.update_commit_status = update_commit_status_fn
        super().__init__(*args)

    # GET/POST handler

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
        content_length = int(
            self.headers["Content-Length"]
        )  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        data = json.loads(post_data)

        # verify signature
        if self.verify_signature(post_data):
            print("--------------------------------------------------")
            print("WRONG SIGNATURE")
            self.send_custom_response(401, "Wrong signature")
            return
        else:
            print("--------------------------------------------------")
            print("SIGNATURE VERIFIED")
            print("--------------------------------------------------")

        # handle push event
        if self.headers["X-GitHub-Event"] == "push":
            if self.push_handler(data):
                return

        # send success message
        self.send_custom_response(200, "SUCCESS")

    # HELPER LOGIC

    # REQUEST HELPERS

    # Verify that it is the webhook that is talking to us.
    def verify_signature(self, post_data):
        sha_name, signature = self.headers["X-Hub-Signature-256"].split("=")
        if sha_name != "sha256":
            return ERROR
        # TODO define a secret token when creating the webhooks
        local_signature = hmac.new(
            os.getenv("secretToken").encode(), msg=post_data, digestmod=hashlib.sha256
        ).hexdigest()
        return not hmac.compare_digest(local_signature, signature)

    # handle push event
    def push_handler(self, data):
        # clone specific branch
        print("--------------------------------------------------")
        print("CLONING BRANCH")
        print("--------------------------------------------------")
        if self.clone_branch(data):
            print("--------------------------------------------------")
            print("COULDN'T CLONE THE BRANCH")
            self.send_custom_response(500, "Couldn't clone the branch")
            return ERROR
        else:
            print("--------------------------------------------------")
            print("BRANCH SUCCESSFULLY CLONED")
            print("--------------------------------------------------")
        # retrieve the commit id
        commit_id = data["commits"][0]["id"]
        # start running the lint on the branch
        print("--------------------------------------------------")
        print("RUNNING LINT")
        print("--------------------------------------------------")
        lint_result = self.run_lint(commit_id)
        print(lint_result)
        print("--------------------------------------------------")
        print("END OF LINT")
        print("--------------------------------------------------")
        # start running the tests on the branch
        print("--------------------------------------------------")
        print("RUNNING TESTS")
        print("--------------------------------------------------")
        tests_result = self.run_tests(commit_id)
        print(tests_result)
        print("--------------------------------------------------")
        print("END OF TESTS")
        print("--------------------------------------------------")
        # create the log file
        print("--------------------------------------------------")
        print("CREATING LOG")
        print("--------------------------------------------------")
        self.make_log(lint_result, tests_result)
        # delete the branch since it is not used anymore
        print("--------------------------------------------------")
        print("DELETING THE BRANCH")
        print("--------------------------------------------------")
        self.remove_cloned_branch(commit_id)
        return NO_ERROR



    # send a custom response given a HTTP code and a specific message
    def send_custom_response(self, code, msg):
        print("--------------------------------------------------")
        print("SENDING RESPONSE")
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(msg)))
        self.end_headers()
        self.wfile.write(msg.encode("utf-8"))
        print("--------------------------------------------------")
        print("\n")

    # CLONING

    # clone the branch related to the push event
    def clone_branch(self, data):
        # retrieve clone url and branch name
        clone_url = data["repository"]["clone_url"]
        branch = data["ref"].split("/")[-1]
        commit_id = data["commits"][0]["id"]
        return os.system(
            f"git clone --single-branch --depth 1 -b {branch} {clone_url} {PATH_TO_CLONED_BRANCHES}/{commit_id}"
        )

    # remove the cloned branch of the given commit id
    def remove_cloned_branch(self, commit_id):
        return os.system(f"rm -rf {PATH_TO_CLONED_BRANCHES}/{commit_id}")

    # LINTING

    # The purpose of this function is to trigger a shell script that lints the
    # code in the project.
    # Note: This should be update so that it runs the linting process on the
    # correct code. As it is it will lint all py files.

    # A shellscript must be explicitly set to executable using the chmod command.
    # Example: chmod +x ./runLint.sh
    def run_lint(self, path):
        runLintPath = "shellscripts/runLint.sh"
        return os.popen(f"{runLintPath} {path}").read()

    # EXECUTING TESTS

    # The purpose of this function is execute all tests in /test/ci_server.
    def run_tests(self, commit_id):
        # In order to get the test results as a string, the output stream is
        # temporarily redirected.
        out = sys.stdout # Save original output stream
        sys.stdout = StringIO()
        path = PATH_TO_CLONED_BRANCHES + "/" + commit_id + "/tests/ci_server"
        pytest.main([path]) # Run tests
        results = sys.stdout.getvalue() # Store the output in variable 'results'
        sys.stdout.close()
        sys.stdout = out # Restore original output stream
        return results

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
