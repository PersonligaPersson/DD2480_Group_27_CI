import sys
from pytest_httpserver import HTTPServer
import pytest
from ci_server.server import CIServer

# FIXTURES
# fixture that creates a new CIServer
@pytest.fixture(scope="session")
def ci_server():
    return CIServer("localhost", 8080)


# fixture that allows us to capture stdout
@pytest.fixture
def capture_stdout(monkeypatch):
    buffer = {"stdout": "", "write_calls": 0}

    def fake_write(s):
        buffer["stdout"] += s
        buffer["write_calls"] += 1

    monkeypatch.setattr(sys.stdout, "write", fake_write)
    return buffer


# TESTS

# Test that we update the commit status to success correctly
def test_sucess_update(ci_server, httpserver, capture_stdout):
    httpserver.expect_request(
        "/repos/user/repo/statuses/12345", json={"state": "success"}
    ).respond_with_json({"state": "success"})

    ci_server.update_commit_status(
        httpserver.url_for("/repos/user/repo/statuses/"), "12345", True, "cooltoken"
    )
    assert "state" in capture_stdout["stdout"]
    assert "success" in capture_stdout["stdout"]


# Test that we update the commit status to failure correctly
def test_failure_update(ci_server, httpserver, capture_stdout):
    httpserver.expect_request(
        "/repos/user/repo/statuses/12345", json={"state": "failure"}
    ).respond_with_json({"state": "failure"})

    ci_server.update_commit_status(
        httpserver.url_for("/repos/user/repo/statuses/"), "12345", False, "cooltoken"
    )
    assert "state" in capture_stdout["stdout"]
    assert "failure" in capture_stdout["stdout"]
