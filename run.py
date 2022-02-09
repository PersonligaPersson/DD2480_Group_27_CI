from ci_server.server import CIServer


def main():
    """
    Entrypoint to out program.
    """
    server = CIServer("localhost", 8080)
    server.run()


if __name__ == "__main__":
    main()
