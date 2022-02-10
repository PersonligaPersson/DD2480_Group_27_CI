import json
import os
import subprocess
import hmac
import hashlib
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv
import requests


# macros used for error status
NO_ERROR = 0
ERROR = 1

PATH_TO_CLONED_BRANCHES = "branches"


class CIServer:
    # Constructor
    def __init__(self, address, port):
        # closure that will instantiate a instance a CIServerHandler for us.
        def handler_fn(*args):
            return CIServerHandler(self.update_commit_status, *args)

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

    def update_commit_status(repo, sha, status):
        load_dotenv()
        TOKEN = os.getenv("GITHUB_TOKEN")
        HEADERS = {"Authorization": "token " + TOKEN}
        URL = "https://api.github.com/repos/" + repo + "/statuses/" + sha

        statusString = "success"
        if not status:
            statusString = "failure"

        DATA = {"state": statusString}
        response = requests.post(url=URL, data=json.dumps(DATA), headers=HEADERS)
        print(response)


class CIServerHandler(BaseHTTPRequestHandler):
    def __init__(self, update_commit_status_fn, *args):
        # We assign the function that updates the commit statuses to a class member.
        self.update_commit_status = update_commit_status_fn
        super().__init__(*args)

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
        # verify the signature of the message

    def verify_signature(self, post_data):
        sha_name, signature = self.headers["X-Hub-Signature-256"].split("=")
        if sha_name != "sha256":
            return ERROR
        # TODO define a secret token when creating the webhooks
        local_signature = hmac.new(
            os.getenv("secretToken").encode(), msg=post_data, digestmod=hashlib.sha256
        ).hexdigest()
        return not hmac.compare_digest(local_signature, signature)

    # The purpose of this function is to generate a unique identifier that serves
    # as the build log name.
    # Note: This would fail if the number of total builds would reach maxint.
    def make_log_title(self):
        tob = time.localtime()
        bString = "X"
        bDatPath = "../logfiles/buildData.dat"
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
        with open(f"../logfiles/{self.make_log_title()}", "w") as f:
            f.write(
                f"=== LINT OUTPUT ===\n{lint_output}\n\n=== PYTEST OUTPUT ===\n{pytest_output}\n"
            )

    # clone the branch related to the push event
    def clone_branch(self, data):
        # retrieve clone url and branch name
        clone_url = data["repository"]["clone_url"]
        branch = data["ref"].split("/")[-1]
        commit_id = data["commits"][0]["id"]
        return os.system(
            f"git clone --single-branch --depth 1 -b {branch} {clone_url} {PATH_TO_CLONED_BRANCHES}/{commit_id}"
        )

    # send a custom response given a html code and a specific message
    def send_custom_response(self, code, msg):
        print("--------------------------------------------------")
        print("SENDING RESPONSE")
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(msg)))
        self.wfile.write(msg.encode("utf-8"))
        self.end_headers()
        print("--------------------------------------------------")
        print("\n")

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
            return NO_ERROR

    # remove the cloned branch of the given commit id
    def remove_cloned_branch(self, commit_id):
        return os.system(f"rm -rf {PATH_TO_CLONED_BRANCHES}/{commit_id}")

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
