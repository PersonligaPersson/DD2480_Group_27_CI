from http.server import HTTPServer
from ci_server import CIServer


def main():
    """
    Entrypoint to out program.
    """
    httpd = HTTPServer(("localhost", 8080), CIServer)
    try:
        print("serving CI server at localhost:8080...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nclosing server...")
        httpd.server_close()


if __name__ == "__main__":
    main()
