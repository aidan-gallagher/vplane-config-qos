#!/usr/bin/env python3
# Copyright (c) 2021, AT&T Intellectual Property. All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only

import sys
import re
import subprocess
import datetime


def get_changed_source_files(source, destination):

    # Get all changes
    git_command = f"git diff --diff-filter=d --name-only --format=format:'' {destination}...{source}"
    result = subprocess.check_output(git_command, shell=True).decode("utf-8")
    all_files = result.splitlines()

    # Only keep source code files
    to_check = []
    for file in all_files:

        # Check if there is a file extension.
        # If there is then check if it is for a python, perl or yang file
        file_split = file.split('.')
        if len(file_split) > 1:
            file_extension = file.split('.').pop()
            if file_extension == 'py'   \
                    or file_extension == 'yang' \
                    or file_extension == 'pm':
                to_check.append(file)
        # Check if the file contains a shebang (!#)
        # to determine if it is a script
        else:
            with open(file) as f:
                first_line = f.readline()
                if '!#' in first_line:
                    to_check.append(file)
    return to_check


def check_att_licence(source_files):

    for file in source_files:
        year = datetime.datetime.now().year
        pattern = rf"Copyright \(c\) .*{year}.* AT&T Intellectual Property"

        with open(file) as f:
            for line in f:
                match = re.search(pattern, line)
                if match:
                    break
            else:
                print(f"Failed: File {file} does not contain AT&T licence")
                sys.exit(1)


def check_spdx_licence(source_files):
    for file in source_files:
        pattern = r"SPDX-License-Identifier:"
        with open(file) as f:
            if pattern not in f.read():
                print(f"Failed: File {file} does not contain SPDX licence")
                sys.exit(1)


def check_yang_address(source_files):
    yang_files = []

    for file in source_files:
        file_extension = file.split('.').pop()
        if file_extension == 'yang':
            yang_files.append(file)

    pattern = r"Postal: 208 S\. Akard Street\n\s*Dallas\, TX 75202, USA\n\s*Web: www.att.com"

    for file in yang_files:
        with open(file) as f:
            yang = f.read()
            match = re.search(pattern, yang)
            if not match:
                print(f"Failed: Yang file {file} does not contain correct address")
                sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        source = "HEAD"
        destination = "origin/master"
        print("No source and destintion reference provided.")
        print(f"Assuming source is {source} and destination is {destination}")
    else:
        source = sys.argv[1]
        destination = sys.argv[2]

    source_files = get_changed_source_files(source, destination)
    check_att_licence(source_files)
    check_spdx_licence(source_files)
    check_yang_address(source_files)
