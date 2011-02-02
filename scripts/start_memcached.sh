#!/bin/bash
#
# Thanks Peteris Krumins (peter@catonmat.net)
#
# This script launches memcached with the right parameters.
#
# Code is licensed under GNU GPL license.
#

PATH_TO_MEMCACHED=/home/gmccollam/installs/memcached-1.4.4/bin
PATH=$PATH_TO_MEMCACHED:$PATH

echo "Starting memcached."
memcached -l 127.0.0.1 -d -m 256
echo "Done."
