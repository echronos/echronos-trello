[![Codacy Badge](https://api.codacy.com/project/badge/Grade/72880fd2c1dc4f87ae4b7496c79573ec)](https://www.codacy.com/app/stefangotz/echronos-trello?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=echronos/echronos-trello&amp;utm_campaign=Badge_Grade)
[![Code Issues](https://www.quantifiedcode.com/api/v1/project/5b06ae32cd264bdea665df93d1723f51/badge.svg)](https://www.quantifiedcode.com/app/project/5b06ae32cd264bdea665df93d1723f51)

# Overview

echronos-trello helps eChronos developers to stay on top task branches on review or in progress.
It publishes those tasks as Trello cards on https://trello.com/b/LU7D8Upa/echronos-rtos-tasks .
It continually keeps Trello up-to-date as tasks are being worked on, reviewed, and integrated.


# Usage

1. Create a local clone of this repository: `git clone https://github.com/echronos/echronos-trello.git`
2. Create the file `trello_credentials.json` with the contents `{"api_key": "", "api_secret": "", "token": "", "token_secret": ""}` and fill in each field with credentials obtained according to https://github.com/sarumont/py-trello#usage
3. Create a local clone of the [eChronos RTOS git repository](https://github.com/echronos/echronos): `git clone https://github.com/echronos/echronos.git`
4. Switch to the directory containing that local clone: `cd echronos`
5. Run the update script: `../echronos-trello/run.py ../trello_credentials.json`

## Prerequisites

The update script depends on a Python 3 interpreter, the Python package `py-trello`, and a `git` executable.


# Contact

You can reach us

- through GitHub issues
- via the GitHub accounts of contributors to this project
- [@echronosrtos](https://twitter.com/echronosrtos) on Twitter
- echronosrtos@breakawayconsulting.com.au


# License

This program is free software:
you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
