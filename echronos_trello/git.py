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

import subprocess


def git_remote_branches(remote='origin'):
    remote_branches = [x[2:].strip() for x in git(['branch', '-r', '--no-merged', 'origin/master'], as_lines=True)]
    return [x[len(remote) + 1:] for x in remote_branches if x.startswith(remote + '/')]


def fetch():
    output = git(['fetch', '--prune', 'origin'], as_lines=False)
    return not output


def git(parameters, as_lines=False):
    assert isinstance(parameters, (list, tuple))
    raw_data = subprocess.check_output(['git'] + list(parameters)).decode()
    if as_lines:
        return raw_data.splitlines()
    return raw_data
