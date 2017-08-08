"""
 * PyAzBlob 1.0.0 Python Azure Blob Service Bulk Uploader
 * https://github.com/RobertoPrevato/PyAzBlob
 *
 * Copyright 2017, Roberto Prevato
 * https://robertoprevato.github.io
 *
 * Licensed under the MIT license:
 * http://www.opensource.org/licenses/MIT
"""
import sys
is_less_than_34 = sys.version_info <= (3, 4)

separator = "===========================================================\n"

banner = """
===========================================================
  _____                     ____  _       _                
 |  __ \         /\        |  _ \| |     | |               
 | |__) |   _   /  \    ___| |_) | | ___ | |__             
 |  ___/ | | | / /\ \  |_  /  _ <| |/ _ \| '_ \            
 | |   | |_| |/ ____ \  / /| |_) | | (_) | |_) |           
 |_|    \__, /_/    \_\/___|____/|_|\___/|_.__/            
         __/ |                                             
        |___/                                              
                                                           
  PyAzBlob | Azure Blob Service Bulk Uploader.             
  Written by Roberto Prevato <roberto.prevato@gmail.com>   
                                                           
==========================================================="""


def sep_print(message):
    print("[*]")
    print("[*] " + message)
    print("[*]")

if is_less_than_34:
    print(banner)
    sep_print("PyAzBlob requires Python 3.4 or greater")
    sys.exit(1)

import argparse
from core.exceptions import ArgumentNullException, InvalidArgument, MissingDependency, ConfigurationError


parser = argparse.ArgumentParser(description="PyAzBlob | Azure Blob Service Bulk Uploader",
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog="{}\n{}".format("author: Roberto Prevato roberto.prevato@gmail.com", separator))

parser.add_argument("-p", "--path", dest="root_path", required=True,
                    help="path from which to start uploading files")

parser.add_argument("-c", "--cut", dest="cut_path", required=False,
                    help="portion of root path to cut from uploaded blobs")

parser.add_argument("-i", "--ignore", dest="ignoredpath", required=False, nargs="+",
                    help="ignored paths (Unix style, globs)", default=[])

parser.add_argument("-r", "--recurse", dest="recurse", required=False, action="store_true", default=False,
                    help="whether to do recursive upload of subfolders and files.")

parser.add_argument("-f", "--force", dest="force", required=False, action="store_true", default=False,
                    help="whether to force re-upload of files that were uploaded in a previous run (from files.log).")

parser.add_argument("-s", "--sleep", dest="sleep", required=False, default=-1,
                    help="sleep time in milliseconds, between uploads (default no sleep)")

parser.add_argument("--nobanner", dest="nobanner", required=False, action="store_true", default=False,
                    help="whether to disable the banner with ascii art.")

options = parser.parse_args()


if __name__ == "__main__":
    if not options.nobanner:
        print(banner)
    try:
        from core.pyazblobcore import pyazupload_entry

        pyazupload_entry(options.root_path,
                         options.cut_path,
                         options.ignoredpath,
                         options.recurse,
                         options.force,
                         options.sleep)

    except MissingDependency as mde:
        sep_print(str(mde))
        sys.exit(1)

    except ConfigurationError as ce:
        sep_print("Configuration Error: " + str(ce))
        sys.exit(1)

    except (ArgumentNullException, InvalidArgument) as handled_exception:
        sep_print("Error: " + str(handled_exception))

    except RuntimeError as re:
        sep_print("Runtime Error: " + str(re))

    except KeyboardInterrupt:
        sep_print("User interrupted...")
