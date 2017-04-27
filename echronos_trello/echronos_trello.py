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

    high_complexity_threshold = sum(task.complexity for task in tasks) / len(tasks)
    low_mid_complexity_tasks = [task for task in tasks if task.complexity < high_complexity_threshold]
    medium_complexity_threshold = sum(task.complexity for task in low_mid_complexity_tasks) / len(low_mid_complexity_tasks)

    for task in tasks:
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

    for card in trello.cards.values():
        if card.name not in task_branch_names:
            card.delete()
            print("{}: deleted".format(card.name))

    return 0


def _update_labels(trello, card, task, medium_complexity_threshold, high_complexity_threshold):
    if task.complexity < medium_complexity_threshold:
        color = "green"
    elif task.complexity < high_complexity_threshold:
        color = "yellow"
    else:
        color = "red"
    if len(card.labels) > 1 or (len(card.labels) == 1 and card.labels[0].id != trello.labels[color].id):
        for label in card.labels:
            card.remove_label(label)
        card.fetch()
    if not card.labels:
        card.add_label(trello.labels[color])


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
            if "Rework" in self.reviews.values():
                return "Needs Rework"
            accepts = len([c for c in self.reviews.values() if c == "Accepted"])
            if accepts < 2:
                return "Needs More Reviews"
            return "Ready for Integration"
        else:
            return "In Progress"

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

        section_testing = "# Testing\n\n* core repository on Linux: ![test status core Linux](https://travis-ci.org/echronos/echronos.svg?branch={0})\n* client repository on Linux: ![test status client Linux](https://travis-ci.org/echronos/test-client-repo.svg?branch={0})\n\n".format(self.name)

        section_github = "# Github\n\n* [Branch on github](https://github.com/echronos/echronos/tree/{0})\n* [Diff on github](https://github.com/echronos/echronos/compare/{0})\n\n".format(self.name)

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

        description = section_name + section_reviews + section_testing + section_github + section_task
        return description.strip()

    @property
    def reviews(self):
        if self._reviews is None:
            self._reviews = self._get_reviews()
        return self._reviews

    def _get_reviews(self):
        author = None
        conclusion = None
        authors_to_conclusions = {}
        for revid in reversed(self._get_revids_of_review_changes()):
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
        return authors_to_conclusions

    def _get_revids_of_review_changes(self):
        merge_base = git.git(["merge-base", "origin/" + self.name, "origin/master"]).strip()
        revids = git.git(["log", "--pretty=format:%H", "{}..origin/{}".format(merge_base, self.name), "--", "pm/reviews/" + self.name], as_lines=True)
        return revids

    @property
    def complexity(self):
        if self._complexity is None:
            self._complexity = self._get_complexity()
        return self._complexity

    def _get_complexity(self):
        paths = [name for name in os.listdir(".") if not name.startswith("external_tools") and not name.startswith("tools")]
        merge_base = git.git(["merge-base", "origin/" + self.name, "origin/master"]).strip()
        stats = git.git(["diff", "--stat", "--diff-filter=MA", "-M", "{}..origin/{}".format(merge_base, self.name)] + paths, as_lines=True)[-1].strip()
        if " files changed" in stats:
            changed_files_str, stats = stats.split(" files changed")
            changed_files = int(changed_files_str.strip())
            stats = stats.strip(", ")
        else:
            changed_files = 0
        if " insertions" in stats:
            insertions_str, stats = stats.split(" insertions(+)")
            insertions = int(insertions_str.strip())
            stats = stats.strip(", ")
        else:
            insertions = 0
        if " deletions" in stats:
            deletions = int(stats.split(" deletions")[0].strip())
        else:
            deletions = 0

        modifications = insertions + deletions

        return changed_files * 2 + modifications
