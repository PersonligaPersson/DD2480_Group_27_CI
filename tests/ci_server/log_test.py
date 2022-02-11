import os
import pytest
from ci_server.server import CIServer
import re

server = CIServer("localhost", 8080)

# ------------------------------------
# Tests for make_log_title()
# ------------------------------------

"""A test that verifies that the build nr in a generated log title is the same as the build nr in builData.dat.
"""
def test_log_title_build_num():
    title = server.make_log_title()
    file = open("logfiles/buildData.dat", "r+")
    counter = file.read()
    assert title.split("_")[1] == counter.replace('\n', '')

"""A test that verifies that the content of every log file follows a certain format.
"""
def test_log_format():
    server.make_log("line_output", "pytest_output")
    folder = os.listdir("logfiles")
    
    for file_name in folder:
        if (file_name.split(".")[1] == "dat"):
            continue
        file = open("logfiles/" + file_name, "r+")
        file_content = file.read()
        assert file_content.__contains__("=== LINT OUTPUT ===")
        assert file_content.__contains__("=== PYTEST OUTPUT ===")
