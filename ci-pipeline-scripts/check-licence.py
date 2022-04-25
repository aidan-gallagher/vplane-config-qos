#!/usr/bin/env python3

# Copyright (c) 2022 Ciena Corporation. All rights reserved.
# SPDX-License-Identifier: LGPL-2.1-only

import sys
from typing import List
import datetime
import re


def licence(source_files: List[str]) -> bool:
    """ Check source code files contains an up to date Ciena licence and spdx licence. """

    curr_year = datetime.datetime.now().year
    ciena_pattern = rf"Copyright \(c\) .*{curr_year}.* Ciena Corporation. All rights reserved."
    spdx_pattern = r"SPDX-License-Identifier:"
    check_failed = False

    for file in source_files:
        ciena_file_error = spdx_file_error = False
        with open(file) as f:
            error_msg = f"File Failed: {file}\n"
            file_content = f.read()
            if not re.search(ciena_pattern, file_content):
                error_msg += f"             Fails regex: {ciena_pattern}\n"
                ciena_file_error = True
            if not re.search(ciena_pattern, file_content):
                error_msg += f"             Fails regex: {spdx_pattern}\n"
                spdx_file_error = True
            if ciena_file_error or spdx_file_error:
                print(error_msg)
                check_failed = True

    return check_failed


if __name__ == "__main__":
    extensions = [".py", ".yang", ".pl", ".sh"]
    source_files = []
    for file in sys.argv[1:]:
        if any(extension in file for extension in extensions):
            source_files.append(file)
    print(f"Checking source files {source_files}")

    if licence(source_files):
        sys.exit(1)