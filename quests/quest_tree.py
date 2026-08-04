from __future__ import annotations

# This file builds the hierarchical quest structure for Apex Ghost.
# The goal is to organize long-term goals into smaller actionable steps.
#
# Example hierarchy:
# - Annual goal
#   - Monthly theme
#     - Weekly sprint
#       - Daily quest

from dataclasses import dataclass, field
from typing import Optional

from quests.models import Quest, QuestLevel, QuestNode


@dataclass
class QuestTree:
    """
    A quest tree represents the full hierarchy of goals.

    It usually starts from one top-level annual quest,
    then branches into monthly, weekly, and daily quests.
    """
    root: Optional[QuestNode] = None

    def set_root(self, quest: Quest) -> QuestNode:
        """
        Set the root quest of the tree.

        This should usually be the annual goal.
        """
        self.root = QuestNode(quest=quest)
        return self.root

    def get_root(self) -> Optional[QuestNode]:
        """
        Return the root node if one exists.
        """
        return self.root

    def add_child(self, parent: QuestNode, child_quest: Quest) -> QuestNode:
        """
        Add a child quest beneath a parent quest node.
        """
        child_node = QuestNode(quest=child_quest)
        parent.add_child(child_node)
        return child_node

    def find_by_level(self, level: QuestLevel) -> list[QuestNode]:
        """
        Find all quests in the tree that match a given level.
        """
        results: list[QuestNode] = []

        def traverse(node: QuestNode) -> None:
            if node.quest.level == level:
                results.append(node)

            for child in node.children:
                traverse(child)

        if self.root is not None:
            traverse(self.root)

        return results

    def walk(self) -> list[QuestNode]:
        """
        Return all nodes in the tree in depth-first order.
        """
        nodes: list[QuestNode] = []

        def traverse(node: QuestNode) -> None:
            nodes.append(node)
            for child in node.children:
                traverse(child)

        if self.root is not None:
            traverse(self.root)

        return nodes

    def print_tree(self) -> None:
        """
        Print the quest tree in a readable indented format.

        This is useful for debugging and quick visual checks.
        """
        if self.root is None:
            print("Quest tree is empty.")
            return

        def print_node(node: QuestNode, indent: int = 0) -> None:
            prefix = "  " * indent
            print(f"{prefix}- [{node.quest.level.value}] {node.quest.title}")

            for child in node.children:
                print_node(child, indent + 1)

        print_node(self.root)