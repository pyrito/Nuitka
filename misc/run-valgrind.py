#!/usr/bin/env python
#     Copyright 2012, Kay Hayen, mailto:kayhayen@gmx.de
#
#     Part of "Nuitka", an optimizing Python compiler that is compatible and
#     integrates with CPython, but also works on its own.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#

import os, sys, subprocess, shutil, tempfile

input_file = sys.argv[1]
nuitka_binary = os.environ.get( "NUITKA_BINARY", "nuitka" )

basename = os.path.basename( input_file )

tempdir = tempfile.mkdtemp(
    prefix = basename + "-",
    dir    = None if not os.path.exists( "/var/tmp" ) else "/var/tmp"
)

output_binary = os.path.join(
    tempdir,
    ( basename[:-3] if input_file.endswith( ".py" ) else basename ) + ".exe"
)

os.system(
    "%s --exe --output-dir=%s --remove-output --unstriped %s %s" % (
        nuitka_binary,
        tempdir,
        os.environ.get( "NUITKA_EXTRA_OPTIONS", "" ),
        input_file
    )
)

if not os.path.exists( output_binary ):
    print "Seeming failure of Nuitka to compile."

log_file = ( basename[:-3] if input_file.endswith( ".py" ) else basename ) + ".log"

sys.stdout.flush()

valgrind_options = "-q --tool=callgrind --callgrind-out-file=%s --zero-before=init__main__" % log_file

subprocess.check_call( [ "valgrind" ] + valgrind_options.split() + [ output_binary ] )

if "number" in sys.argv:
    for line in open( log_file ):
        if line.startswith( "summary:" ):
            print "SIZE=%d" % os.stat( output_binary ).st_size
            print "TICKS=%s" % line.split()[1]
            break
    else:
        assert False

    shutil.rmtree( tempdir )
else:
    os.system( "kcachegrind 2>/dev/null 1>/dev/null %s &" % log_file )