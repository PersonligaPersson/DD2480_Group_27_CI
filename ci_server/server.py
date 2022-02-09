from http.server import BaseHTTPRequestHandler
from github import Github

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

    def update_commit_status(self, branch_name, build_result):
            github = Github("dummyContributor", "dd2480dd2480") # Dummy Github user
            repo = github.get_repo("PersonligaPersson/DD2480_Group_27_CI")
            branch = repo.get_branch(branch=branch_name)        
            head_commit = branch.commit
            if (build_result):
                head_commit.state = "sucess"
            else:
                head_commit.state = "failure"
            return branch.commit.state # For debugging