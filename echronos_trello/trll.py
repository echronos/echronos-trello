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

import json
from trello import TrelloClient


class Trello:
    def __init__(self, credentials_path):
        with open(credentials_path, "r") as file_obj:
            credentials = json.load(file_obj)
        client = TrelloClient(**credentials)
        board = client.list_boards()[0]

        self.cards = {}
        for card in board.open_cards():
            self.cards[card.name] = card

        self.lists = {}
        for lst in board.open_lists():
            self.lists[lst.name] = lst

        self.labels = {lbl.color: lbl for lbl in board.get_labels()}
