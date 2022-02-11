# import os
# from ci_server.server import CIServer

# server = CIServer("localhost", 8081)

# # ------------------------------------
# # Tests for make_log_title()
# # ------------------------------------

# # This test checks that the build nr in the log title is the same as the nr
# # in buildData.dat.
# def test_log_title_build_num():
#     title = server.make_log_title()
#     file = open("logfiles/buildData.dat", "r+")
#     counter = file.read()
#     assert title.split("_")[1] == counter.replace('\n', '')

# # This test checks that the content of every log file follows a certain format.
# def test_log_format():
#     server.make_log("line_output", "pytest_output")
#     folder = os.listdir("logfiles")
#     for file_name in folder:
#         if (file_name.split(".")[1] != "dat"):
#             file = open("logfiles/" + file_name, "r+")
#             file_content = file.read()
#             assert file_content.__contains__("=== LINT OUTPUT ===")
#             assert file_content.__contains__("=== PYTEST OUTPUT ===")
