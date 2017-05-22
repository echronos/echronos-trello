#!/bin/sh
# echronos-trello: publish task branches of the eChronos RTOS source repository on Trello
# Copyright (C) 2017 Breakaway Consulting Pty. Ltd.
#
# echronosrtos@breakawayconsulting.com.au
# P.O. Box 732, Newtown, NSW 2042, Australia
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

date

set -e
set -u

TRELLO_CREDENTIALS_FILE="${1}"

if [ ! -d x.py ]; then
    echo "This script needs to be run from a local clone of https://github.com/echronos/echronos.git as the current working directory."
    exit 1
fi

python3 "$(dirname "${0}")"/run.py "${TRELLO_CREDENTIALS_FILE}"
