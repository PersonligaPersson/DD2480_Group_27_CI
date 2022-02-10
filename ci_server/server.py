from http.server import BaseHTTPRequestHandler
import subprocess # subprocess
import hmac
import hashlib
import os
import json

# macros used for error status
NO_ERROR = 0
ERROR = 1

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

    # verify the signature of the message
    def verify_signature(self, post_data):
        sha_name, signature = self.headers['X-Hub-Signature-256'].split('=')
        if sha_name != 'sha256':
            return ERROR
        # TODO define a secret token when creating the webhooks
        local_signature = hmac.new(
            os.getenv("secretToken").encode(),
            msg=post_data,
            digestmod=hashlib.sha256
        ).hexdigest()
        return not hmac.compare_digest(local_signature, signature)

    # clone the branch related to the push event
    def clone_branch(data):
        # retrieve clone url and branch name
        clone_url = data["repository"]["clone_url"]
        branch = data["ref"].split("/")[-1]
        return os.system(
            f"cd branches; git clone --single-branch -b {branch} {clone_url}"
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

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
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
