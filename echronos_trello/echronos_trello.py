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

import os
import re
import subprocess

from . import git
from .trll import Trello


def update_trello_on_changes(options):
    if git.fetch():
        result = update_trello(options)
    else:
        print("No updates in remote repository")
        result = 0
    return result


def update_trello(options):
    trello = Trello(options.credentials_path)
    all_branch_names = git.git_remote_branches()
    task_branch_names = [b for b in all_branch_names if "/" not in b and b not in ("master", "lca2016")]
    tasks = [Task(n) for n in task_branch_names]

    if tasks:
        medium_complexity_threshold, high_complexity_threshold = _get_complexity_thresholds(tasks)

    for task in tasks:
        _update_card(trello, task, medium_complexity_threshold, high_complexity_threshold)

    _delete_obsolete_cards(trello.cards.values(), task_branch_names)

    return 0


def _get_complexity_thresholds(tasks):
    high_complexity_threshold = sum(task.complexity for task in tasks if task.complexity) / len(tasks)
    low_mid_complexity_tasks = [task for task in tasks if task.complexity and task.complexity < high_complexity_threshold]
    if low_mid_complexity_tasks:
        medium_complexity_threshold = sum(task.complexity for task in low_mid_complexity_tasks if task.complexity) / len(low_mid_complexity_tasks)
    else:
        medium_complexity_threshold = high_complexity_threshold / 2
    return medium_complexity_threshold, high_complexity_threshold


def _update_card(trello, task, medium_complexity_threshold, high_complexity_threshold):
    lst = trello.lists[task.get_state()]
    if task.name not in trello.cards:
        card = lst.add_card(task.name, task.description)
        trello.cards[task.name] = card
        print("{}: created card".format(task.name))
    else:
        card = trello.cards[task.name]
        if card.list_id != lst.id:
            card.change_list(lst.id)
            print("{}: moved to list '{}'".format(task.name, lst.name))
        if card.description != task.description:
            print("{}: updated description from '{}' to '{}'".format(task.name, card.description, task.description))
            card.set_description(task.description)
        _update_labels(trello, card, task, medium_complexity_threshold, high_complexity_threshold)


def _update_labels(trello, card, task, medium_complexity_threshold, high_complexity_threshold):
    color = _get_color_from_task_complexity(task.complexity, medium_complexity_threshold, high_complexity_threshold)
    _delete_incorrect_labels_on_card(card, color)
    if color and not card.labels:
        card.add_label(trello.labels[color])


def _get_color_from_task_complexity(complexity, medium_complexity_threshold, high_complexity_threshold):
    if complexity:
        if complexity < medium_complexity_threshold:
            return "green"
        elif complexity < high_complexity_threshold:
            return "yellow"
        return "red"
    return None


def _delete_incorrect_labels_on_card(card, color):
    for label in card.labels:
        if label.color != color:
            card.remove_label(label)
    card.fetch()


def _delete_obsolete_cards(cards, task_branch_names):
    for card in cards:
        if card.name not in task_branch_names:
            card.delete()
            print("{}: deleted".format(card.name))


class Task:
    def __init__(self, name):
        self.name = name
        self._is_integrated = None
        self._complexity = None
        self._is_on_review = None
        self._description = None
        self._reviews = None

    def get_state(self):
        if self.is_on_review:
            return self._get_review_state()
        return "In Progress"

    def _get_review_state(self):
        if "Rework" in self.reviews.values():
            return "Needs Rework"
        accepts = len([c for c in self.reviews.values() if c == "Accepted"])
        if accepts < 2:
            return "Needs More Reviews"
        return "Ready for Integration"

    @property
    def is_on_review(self):
        if self._is_on_review is None:
            self._is_on_review = self._get_on_review()
        return self._is_on_review

    def _get_on_review(self):
        try:
            git.git(["show", "origin/{0}:pm/reviews/{0}".format(self.name)])
        except subprocess.CalledProcessError:
            return False
        return True

    @property
    def description(self):
        if self._description is None:
            self._description = self._get_description()
        return self._description

    def _get_description(self):
        section_name = "# Task Name\n\n{}\n\n".format(self.name)

        if self.is_on_review and self.reviews:
            section_reviews = "# Reviews\n\n" + "\n".join(sorted(["* {}: {}".format(author, conclusion) for author, conclusion in self.reviews.items() if conclusion != "Open"])).strip() + "\n\n"
        else:
            section_reviews = ""

        section_testing = "# Testing\n\n* core repository: ![](https://travis-ci.org/echronos/echronos.svg?branch={0}) [![](https://ci.appveyor.com/api/projects/status/u0l9tcx3r8x9fwj0/branch/{0}?svg=true)](https://ci.appveyor.com/project/stefangotz/echronos/branch/{0})\n* client repository: ![](https://travis-ci.org/echronos/test-client-repo.svg?branch={0}) [![](https://ci.appveyor.com/api/projects/status/wbyntsf0a5crcl62/branch/{0}?svg=true)](https://ci.appveyor.com/project/stefangotz/test-client-repo/branch/{0})\n\n".format(self.name)

        section_github = "# Github\n\n* [Branch on github](https://github.com/echronos/echronos/tree/{0})\n* [Diff on github](https://github.com/echronos/echronos/compare/{0})\n\n".format(self.name)

        description = section_name + section_reviews + section_testing + section_github + self._get_task_section()
        return description.strip()

    @property
    def reviews(self):
        if self._reviews is None:
            self._reviews = self._get_reviews()
        return self._reviews

    def _get_reviews(self):
        authors_to_conclusions = {}
        for revid in reversed(self._get_revids_of_review_changes()):
            _update_review_conclusions_from_revid(authors_to_conclusions, revid)
        return authors_to_conclusions

    def _get_revids_of_review_changes(self):
        merge_base = git.git(["merge-base", "origin/" + self.name, "origin/master"]).strip()
        revids = git.git(["log", "--pretty=format:%H", "{}..origin/{}".format(merge_base, self.name), "--", "pm/reviews/" + self.name], as_lines=True)
        return revids

    def _get_task_section(self):
        try:
            task_file_contents = git.git(["show", "origin/{0}:pm/tasks/{0}".format(self.name)])
            end_of_comment_index = task_file_contents.find("-->")
            if end_of_comment_index == -1:
                task_description = task_file_contents
            else:
                task_description = task_file_contents[end_of_comment_index+3:].lstrip()
            section_task = task_description + "\n\n"
        except subprocess.CalledProcessError:
            section_task = ""
        return section_task

    @property
    def complexity(self):
        if self._complexity is None:
            self._complexity = self._get_complexity()
        return self._complexity

    def _get_complexity(self):
        try:
            paths = [name for name in os.listdir(".") if not name.startswith("external_tools") and not name.startswith("tools")]
            merge_base = git.git(["merge-base", "origin/" + self.name, "origin/master"]).strip()
            diff = git.git(["diff", "--stat", "--diff-filter=MA", "-M", "{}..origin/{}".format(merge_base, self.name)] + paths, as_lines=True)
            if not diff:
                return 0

            stats = diff[-1].strip()

            changed_files, insertions, deletions = _parse_stats(stats)

            modifications = insertions + deletions

            return changed_files * 2 + modifications
        except (ValueError, KeyError, IndexError) as err:
            print("Exception '{}' occurred while attempting to parse '{}'".format(err, stats))
            return 0


def _parse_stats(stats):
    match = re.search(r"(\d+) file", stats)
    if match:
        changed_files = int(match.group(1))
    else:
        changed_files = 0
    match = re.search(r"(\d+) insertion", stats)
    if match:
        insertions = int(match.group(1))
    else:
        insertions = 0
    match = re.search(r"(\d+) deletion", stats)
    if match:
        deletions = int(match.group(1))
    else:
        deletions = 0

    return changed_files, insertions, deletions


def _update_review_conclusions_from_revid(authors_to_conclusions, revid):
    author = None
    conclusion = None
    output_lines = git.git(["show", revid], as_lines=True)
    for line in output_lines:
        line = line.strip()
        if line.startswith("diff "):
            author = None
            conclusion = None
        elif "Reviewer: " in line:
            author_and_email = line[10:].strip()
            author = author_and_email.split("(")[0].strip()
        elif line.lower().startswith("+conclusion:"):
            if line.lower() == "+conclusion: accepted":
                conclusion = "Accepted"
            elif line.lower() == "+conclusion: rework":
                conclusion = "Rework"
            elif line.lower() == "+conclusion: accepted/rework":
                conclusion = "Open"
            else:
                print("Cannot handle conclusion '{}'".format(line))
        if author and conclusion:
            if conclusion == "Open":
                prev = authors_to_conclusions.get(author, None)
                if prev == "Accepted":
                    conclusion = "Accepted"
            authors_to_conclusions[author] = conclusion
            author = None
            conclusion = None
