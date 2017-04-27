#!/usr/bin/env python3
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

import os.path
import sys
from pylint.lint import Run
sys.path.insert(0, os.path.dirname(__file__))
from echronos_trello.__main__ import main  # pylint: disable=wrong-import-position

if __name__ == "__main__":
    RC_FILE_PATH = os.path.join(os.path.dirname(__file__), '.pylintrc')
    PYLINT_RUNNER = Run(['--rcfile', RC_FILE_PATH, __file__, os.path.join(os.path.dirname(__file__), 'echronos_trello')], exit=False)
    if PYLINT_RUNNER.linter.msg_status == 0:
        sys.exit(main())
    else:
        sys.exit(1)
