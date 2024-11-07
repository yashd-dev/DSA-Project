from typing import Any, List, Optional, Dict, Union
from dataclasses import dataclass
import json
import os
import pickle

# Defines a node in the B+Tree
@dataclass
class Node:
    leaf: bool  # Indicates if the node is a leaf node
    keys: List[Any]  # Stores the keys in the node
    children: List['Node']  # Stores the child nodes (for non-leaf nodes)
    values: List[Dict[str, Any]]  # Stores the values associated with the keys (for leaf nodes)
    next_leaf: Optional['Node'] = None  # Stores the next leaf node (for linked list of leaf nodes)

# Implements a B+Tree
class BPlusTree:
    def __init__(self, order: int):
        self.root = Node(leaf=True, keys=[], children=[], values=[])
        self.order = order  # The order of the B+Tree (determines the minimum/maximum number of children per node)

    # Inserts a key-value pair into the B+Tree
    def insert(self, key: Any, value: Dict[str, Any]):
        # If the root is full, create a new root
        if len(self.root.keys) == (2 * self.order) - 1:
            old_root = self.root
            self.root = Node(leaf=False, keys=[], children=[old_root], values=[])
            self._split_child(self.root, 0)
        self._insert_non_full(self.root, key, value)

    # Splits a full child node into two nodes
    def _split_child(self, parent: Node, child_index: int):
        order = self.order
        child = parent.children[child_index]
        new_node = Node(leaf=child.leaf, keys=[], children=[], values=[])

        # Move half the keys to the new node
        mid = order - 1
        parent.keys.insert(child_index, child.keys[mid])
        new_node.keys = child.keys[mid + 1:]
        child.keys = child.keys[:mid]

        if not child.leaf:
            new_node.children = child.children[mid + 1:]
            child.children = child.children[:mid + 1]
        else:
            new_node.values = child.values[mid:]
            child.values = child.values[:mid]

        parent.children.insert(child_index + 1, new_node)

    # Recursively inserts a key-value pair into a non-full node
    def _insert_non_full(self, node: Node, key: Any, value: Dict[str, Any]):
        i = len(node.keys) - 1

        if node.leaf:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            node.keys.insert(i + 1, key)
            node.values.insert(i + 1, value)
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1

            if len(node.children[i].keys) == (2 * self.order) - 1:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key, value)

    # Searches for a key and returns its associated value (if found)
    def search(self, key: Any) -> Optional[Dict[str, Any]]:
        node = self.root
        while not node.leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]

        for i, k in enumerate(node.keys):
            if k == key:
                return node.values[i]
        return None

    # Updates the value associated with a key
    def update(self, key: Any, value: Dict[str, Any]) -> bool:
        node = self.root
        while not node.leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]

        for i, k in enumerate(node.keys):
            if k == key:
                node.values[i] = value
                return True
        return False

    # Deletes a key-value pair from the tree
    def delete(self, key: Any) -> bool:
        if not self.root.keys:
            return False

        self._delete(self.root, key)

        # If the root has no keys and is not a leaf, make its first child the new root
        if not self.root.leaf and not self.root.keys:
            self.root = self.root.children[0]
        return True

    # Reads a key-value pair from the tree
    def read(self, key: Any) -> Optional[Dict[str, Any]]:
        def find_key(node: Node, key: Any) -> int:
            return next((i for i, k in enumerate(node.keys) if k == key), -1)

        if not self.root.keys:
            return None

        i = find_key(self.root, key)
        if i == -1:
            return None

        node = self.root
        while not node.leaf:
            node = node.children[i]
            i = find_key(node, key)

# Implements a simple database using the B+Tree
class SimpleDB:
    def __init__(self, db_name: str, order: int = 3):
        self.db_name = db_name
        self.tables: Dict[str, BPlusTree] = {}
        self.order = order
        self.db_dir = f"{db_name}_data"
        self.load_db()

    # Creates a new table
    def create_table(self, table_name: str):
        if table_name not in self.tables:
            self.tables[table_name] = BPlusTree(self.order)
            return f"Table '{table_name}' created successfully"
        return f"Error: Table '{table_name}' already exists"

    # Inserts a record into a table
    def insert(self, table_name: str, key: Any, data: Dict[str, Any]):
        if table_name not in self.tables:
            return f"Error: Table '{table_name}' does not exist"

        if self.tables[table_name].search(key) is not None:
            return f"Error: Key '{key}' already exists in table '{table_name}'"

        self.tables[table_name].insert(key, data)
        return f"Record inserted successfully"

    # Updates a record in a table
    def update(self, table_name: str, key: Any, data: Dict[str, Any]):
        if table_name not in self.tables:
            return f"Error: Table '{table_name}' does not exist"

        if self.tables[table_name].update(key, data):
            return f"Record updated successfully"
        return f"Error: Record with key '{key}' not found"

    # Reads a record from a table
    def read(self, table_name: str, key: Any):
        if table_name not in self.tables:
            return f"Error: Table '{table_name}' does not exist"

        record = self.tables[table_name].search(key)
        if record is None:
            return f"Error: Record with key '{key}' not found"
        return record

    # Deletes a record from a table
    def delete(self, table_name: str, key: Any):
        if table_name not in self.tables:
            return f"Error: Table '{table_name}' does not exist"

        if not self.tables[table_name].delete(key):
            return f"Error: Record with key '{key}' not found"
        return f"Record deleted successfully"

    # Saves the database to disk
    def save_db(self):
        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)

        for table_name, tree in self.tables.items():
            file_path = os.path.join(self.db_dir, f"{table_name}.db")
            with open(file_path, 'wb') as f:
                pickle.dump(tree, f)

    # Loads the database from disk
    def load_db(self):
        if not os.path.exists(self.db_dir):
            return

        for file_name in os.listdir(self.db_dir):
            if file_name.endswith('.db'):
                table_name = file_name[:-3]
                file_path = os.path.join(self.db_dir, file_name)
                with open(file_path, 'rb') as f:
                    self.tables[table_name] = pickle.load(f)