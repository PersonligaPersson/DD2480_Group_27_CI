from http.server import BaseHTTPRequestHandler


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
