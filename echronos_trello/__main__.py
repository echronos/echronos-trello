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

import argparse
import sys

from .echronos_trello import update_trello_on_changes


def main():
    options = _get_options()
    return update_trello_on_changes(options)


def _get_options():
    parser = argparse.ArgumentParser()
    parser.add_argument("credentials_path", help='Path to json file containing Trello API credentials in the format {"api_key": "", "api_secret": "", "token": "", "token_secret": ""}')
    return parser.parse_args()

if __name__ == "__main__":
    sys.exit(main())
