from http.server import BaseHTTPRequestHandler, HTTPServer
from github import Github


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

    # Method to update the commit status based on the result of the build
    def update_commit_status(self, branch_name, build_succeeded):
        github = Github("dummyContributor", "dd2480dd2480")  # Dummy Github user
        repo = github.get_repo("PersonligaPersson/DD2480_Group_27_CI")
        branch = repo.get_branch(branch=branch_name)
        head_commit = branch.commit
        if build_succeeded:
            head_commit.state = "sucess"
        else:
            head_commit.state = "failure"
        return branch.commit.state  # For debugging


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
        except:
            file = "File not found"
            self.send_response(404)
        self.end_headers()
        self.wfile.write(bytes(file, "utf8"))
        # TODO: implement logic for serving files here

    def do_POST(self):
        # TODO: implement CI logic here
        self.send_response(404)
        self.end_headers()

