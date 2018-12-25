#!/usr/bin/python
#
#  Fix the filesystem detection in the Linux Dropbox client
#  Copyright (C) 2018  Marco Leogrande
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# This code is loosely based on:
# dropbox
# Dropbox frontend script
# This file is part of nautilus-dropbox 2.10.0

import os
import subprocess
import sys
import time

# Python 3 compatibility on xrange
# Ref: https://stackoverflow.com/a/31136897/1259696
try:
    xrange
except NameError:
    xrange = range


def is_dropbox_running():
    pidfile = os.path.expanduser("/dbox/.dropbox/dropbox.pid")
    try:
        with open(pidfile, "r") as f:
            pid = int(f.read())
        with open("/proc/%d/cmdline" % pid, "r") as f:
            cmdline = f.read().lower()
    except Exception as e:
        print(e)
        cmdline = ""

    return "dropbox" in cmdline


def start_dropbox():
    lib_dir = os.path.dirname(os.path.realpath(__file__))
    lib_path = os.path.join(lib_dir, "libdropbox_fs_fix.so")
    if not os.access(lib_path, os.X_OK):
        print(">>> Library '%s' is not available!" % lib_path)
        return False
    os.environ["LD_PRELOAD"] = lib_path

    db_path = os.path.expanduser(u"/opt/dropbox/dropboxd").encode(
        sys.getfilesystemencoding())

    if os.access(db_path, os.X_OK):
        # process is spawned as user 'dropbox'
        a = subprocess.Popen(
            [db_path],
            cwd=os.path.expanduser("/opt"),
            stderr=sys.stderr,
            stdout=sys.stdout,
            close_fds=True,
        )

        # minimum start time
        time.sleep(20)

        # in seconds
        interval = 1
        wait_for = 40
        for i in xrange(int(wait_for / interval)):
            if is_dropbox_running():
                return True
            # back off from connect for a while
            time.sleep(interval)
            print("Checking if dropbox is running PID")

        return False
    else:
        return False


def main():
    if is_dropbox_running():
        print(">>> Dropbox is already running")
        return 0

    if start_dropbox():
        print(">>> Dropbox started successfully")

        # We spawned the dropbox daemon, but if we return docker will die and kill dropbox.
        while True:
            pass

    print(">>> Dropbox failed to start!")
    return 1


if __name__ == "__main__":
    sys.exit(main())
