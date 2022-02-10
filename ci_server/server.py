import json
import os
from http.server import HTTPServer
from dotenv import load_dotenv
import requests
from .handler import CIServerHandler


class CIServer:
    """
    CIServer

    Attributes:
        handler: A function that                                                                                     returns a CIServerHandler.
        address: The address that the server runs on.
        port:  The port that the server runs on.
    """

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

    def update_commit_status(self, repo, sha, status):
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
