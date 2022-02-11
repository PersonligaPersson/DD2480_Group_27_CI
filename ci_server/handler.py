import sys
from io import StringIO
import hmac
import hashlib
import time
import os
import json
from http.server import BaseHTTPRequestHandler
import pytest
from pprint import pprint

# macros used for error status
NO_ERROR = 0
ERROR = 1

PATH_TO_CLONED_BRANCHES = "branches"


class CIServerHandler(BaseHTTPRequestHandler):

    """
    Custom HTTP handler that handles post request from webhook on Github.
    """

    def __init__(self, update_commit_status_fn, make_log_title_fn, make_log_fn, *args):
        # We assign the function that updates the commit statuses to a class member.
        self.update_commit_status = update_commit_status_fn
        self.make_log_title = make_log_title_fn
        self.make_log = make_log_fn

        super().__init__(*args)

    """Handles GET requests.
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

    """Handles POST requests.
    """
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

    """Verifies the signature of the webhook.
    :param post_data: used to sign the message.
    :returns: True if wrong signature. False otherwise.
    """
    def verify_signature(self, post_data):
        sha_name, signature = self.headers["X-Hub-Signature-256"].split("=")
        if sha_name != "sha256":
            return ERROR
        local_signature = hmac.new(
            os.getenv("secretToken").encode(), msg=post_data, digestmod=hashlib.sha256
        ).hexdigest()
        return not hmac.compare_digest(local_signature, signature)

    """Handles push events in the git repo.
    :param data: POST data.
    :returns: True if an error is encountered. False otherwise. 
    """
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
        success = True
        # start running the lint on the branch
        print("--------------------------------------------------")
        print("RUNNING LINT")
        print("--------------------------------------------------")
        lint_result = self.run_lint(commit_id)
        lint_result_json = open("lint_result.json")
        # check if it there war errors
        if len(json.load(lint_result_json)) != 0:
            success = False
        lint_result_json.close()
        os.system("rm lint_result.json")
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
        print("--------------------------------------------------")
        print("UPDATING COMMIT STATUS")
        print("--------------------------------------------------")  
        statuses_url = data["repository"]["statuses_url"].replace("{sha}", "")  
        self.update_commit_status(statuses_url, commit_id, success)
        return NO_ERROR

    """Sends a custom response. 
    :param code: HTTP code.
    :param msg: message in the response.
    """
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

    """Clones the branch related to the push event.
    :param data: POST data.
    :returns: 0 if success.
    """
    def clone_branch(self, data):
        # retrieve clone url and branch name
        clone_url = data["repository"]["clone_url"]
        branch = data["ref"].split("/")[-1]
        commit_id = data["commits"][0]["id"]
        return os.system(
            f"git clone --single-branch --depth 1 -b {branch} {clone_url} {PATH_TO_CLONED_BRANCHES}/{commit_id}"
        )

    """Removes the cloned branch of a given commit.
    :param commit_id: identifier of commit.
    :returns: 0 if success.
    """
    def remove_cloned_branch(self, commit_id):
        return os.system(f"rm -rf {PATH_TO_CLONED_BRANCHES}/{commit_id}")

    # LINTING

    
    """Run lint on the cloned code using a shellscript.
    :param path: path to the shellscript.
    :returns: string with the lint results.
    """
    # Note: This should be update so that it runs the linting process on the
    # correct code. As it is it will lint all py files.

    # A shellscript must be explicitly set to executable using the chmod command.
    # Example: chmod +x ./runLint.sh
    def run_lint(self, path):
        runLintPath = "shellscripts/runLint.sh"
        return os.popen(f"{runLintPath} {path}").read()

    # EXECUTING TESTS

    """Run the tests of the cloned code.
    :param commit_id: id of a commit used to identify the location of the cloned repo.
    :returns: string with the test results.
    """
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

    