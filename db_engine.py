from typing import Any, List, Optional, Dict, Union
from dataclasses import dataclass
import json
import os
import pickle

@dataclass
class Node:
    leaf: bool
    keys: List[Any]
    children: List['Node']
    values: List[Dict[str, Any]]  # Only used in leaf nodes
    next_leaf: Optional['Node'] = None  # For leaf node linking

class BPlusTree:
    def __init__(self, order: int):
        self.root = Node(leaf=True, keys=[], children=[], values=[])
        self.order = order
    def insert(self, key: Any, value: Dict[str, Any]):
        # If root is full, create new root
        if len(self.root.keys) == (2 * self.order) - 1:
            old_root = self.root
            self.root = Node(leaf=False, keys=[], children=[old_root], values=[])
            self._split_child(self.root, 0)
        self._insert_non_full(self.root, key, value)
    def _split_child(self, parent: Node, child_index: int):
        order = self.order
        child = parent.children[child_index]
        new_node = Node(leaf=child.leaf, keys=[], children=[], values=[])
        
        # Move half the keys to new node
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

    def search(self, key: Any) -> Optional[Dict[str, Any]]:
        """Search for a key and return its associated value"""
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

    def update(self, key: Any, value: Dict[str, Any]) -> bool:
        """Update the value associated with a key"""
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

    def delete(self, key: Any) -> bool:
        """Delete a key-value pair from the tree"""
        if not self.root.keys:
            return False

        self._delete(self.root, key)
        
        # If root has no keys and is not a leaf, make its first child the new root
        if not self.root.leaf and not self.root.keys:
            self.root = self.root.children[0]
        return True
    
    def read(self, key: Any) -> Optional[Dict[str, Any]]:
        """Read a key-value pair from the tree"""
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


    def _delete(self, node: Node, key: Any):
        def find_key(node: Node, key: Any) -> int:
            return next((i for i, k in enumerate(node.keys) if k == key), -1)

        def merge(left: Node, right: Node, parent: Node, index: int):
            """Merge two nodes"""
            if not node.leaf:
                left.keys.append(parent.keys.pop(index))
            left.keys.extend(right.keys)
            if not node.leaf:
                left.children.extend(right.children)
            else:
                left.values.extend(right.values)
                left.next_leaf = right.next_leaf
            parent.children.pop(index + 1)

        min_keys = (self.order - 1) // 2 if not node.leaf else (self.order // 2)
        key_index = find_key(node, key)

        # If we're at a leaf node
        if node.leaf:
            if key_index != -1:  # Key found in current node
                node.keys.pop(key_index)
                node.values.pop(key_index)
                return
            return  # Key not found

        # If we're at an internal node
        if key_index != -1:
            # Get predecessor or successor
            if len(node.children[key_index].keys) >= self.order:
                pred = self._get_predecessor(node, key_index)
                node.keys[key_index] = pred
                self._delete(node.children[key_index], pred)
            elif len(node.children[key_index + 1].keys) >= self.order:
                succ = self._get_successor(node, key_index)
                node.keys[key_index] = succ
                self._delete(node.children[key_index + 1], succ)
            else:
                merge(node.children[key_index], node.children[key_index + 1], node, key_index)
                self._delete(node.children[key_index], key)
        else:
            # Find the child which should contain the key
            child_index = len(node.keys)
            for i, k in enumerate(node.keys):
                if key < k:
                    child_index = i
                    break
            
            child = node.children[child_index]
            if len(child.keys) == min_keys:  # Child has minimum number of keys
                # Try to borrow from siblings
                if child_index > 0 and len(node.children[child_index - 1].keys) > min_keys:
                    self._borrow_from_prev(node, child_index)
                elif child_index < len(node.children) - 1 and len(node.children[child_index + 1].keys) > min_keys:
                    self._borrow_from_next(node, child_index)
                else:  # Merge with a sibling
                    if child_index > 0:
                        merge(node.children[child_index - 1], child, node, child_index - 1)
                        child = node.children[child_index - 1]
                    else:
                        merge(child, node.children[child_index + 1], node, child_index)
            
            self._delete(child, key)

    def _get_predecessor(self, node: Node, index: int) -> Any:
        """Get the predecessor of the key at the given index"""
        current = node.children[index]
        while not current.leaf:
            current = current.children[-1]
        return current.keys[-1]

    def _get_successor(self, node: Node, index: int) -> Any:
        """Get the successor of the key at the given index"""
        current = node.children[index + 1]
        while not current.leaf:
            current = current.children[0]
        return current.keys[0]

    def _borrow_from_prev(self, node: Node, index: int):
        """Borrow a key from the previous sibling"""
        child = node.children[index]
        sibling = node.children[index - 1]

        # Move all keys and children in child one step ahead
        if not child.leaf:
            child.keys.insert(0, node.keys[index - 1])
            node.keys[index - 1] = sibling.keys.pop()
            child.children.insert(0, sibling.children.pop())
        else:
            child.keys.insert(0, sibling.keys.pop())
            child.values.insert(0, sibling.values.pop())
            node.keys[index - 1] = child.keys[0]

    def _borrow_from_next(self, node: Node, index: int):
        """Borrow a key from the next sibling"""
        child = node.children[index]
        sibling = node.children[index + 1]

        if not child.leaf:
            child.keys.append(node.keys[index])
            node.keys[index] = sibling.keys.pop(0)
            child.children.append(sibling.children.pop(0))
        else:
            child.keys.append(sibling.keys.pop(0))
            child.values.append(sibling.values.pop(0))
            node.keys[index] = sibling.keys[0] if sibling.keys else child.keys[-1]

class SimpleDB:
    def __init__(self, db_name: str, order: int = 3):
        self.db_name = db_name
        self.tables: Dict[str, BPlusTree] = {}
        self.order = order
        self.db_dir = f"{db_name}_data"
        self.load_db()

    def create_table(self, table_name: str):
        if table_name not in self.tables:
            self.tables[table_name] = BPlusTree(self.order)
            return f"Table '{table_name}' created successfully"
        return f"Error: Table '{table_name}' already exists"

    def insert(self, table_name: str, key: Any, data: Dict[str, Any]):
        if table_name not in self.tables:
            return f"Error: Table '{table_name}' does not exist"

        if self.tables[table_name].search(key) is not None:
            return f"Error: Key '{key}' already exists in table '{table_name}'"

        self.tables[table_name].insert(key, data)
        return f"Record inserted successfully"

    def update(self, table_name: str, key: Any, data: Dict[str, Any]):
        if table_name not in self.tables:
            return f"Error: Table '{table_name}' does not exist"

        if self.tables[table_name].update(key, data):
            return f"Record updated successfully"
        return f"Error: Record with key '{key}' not found"

    def read(self, table_name: str, key: Any):
        if table_name not in self.tables:
            return f"Error: Table '{table_name}' does not exist"

        record = self.tables[table_name].search(key)
        if record is None:
            return f"Error: Record with key '{key}' not found"
        return record

    def delete(self, table_name: str, key: Any):
        if table_name not in self.tables:
            return f"Error: Table '{table_name}' does not exist"

        if not self.tables[table_name].delete(key):
            return f"Error: Record with key '{key}' not found"
        return f"Record deleted successfully"

    def save_db(self):
        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)

        for table_name, tree in self.tables.items():
            file_path = os.path.join(self.db_dir, f"{table_name}.db")
            with open(file_path, 'wb') as f:
                pickle.dump(tree, f)

    def load_db(self):
        if not os.path.exists(self.db_dir):
            return

        for file_name in os.listdir(self.db_dir):
            if file_name.endswith('.db'):
                table_name = file_name[:-3]
                file_path = os.path.join(self.db_dir, file_name)
                with open(file_path, 'rb') as f:
                    self.tables[table_name] = pickle.load(f)

# Example usage
def demo_db():
    db = SimpleDB("mydb")
    
    while True:
        print("\n=== Database Menu ===")
        print("1. Create Table")
        print("2. Insert Record")
        print("3. Update Record")
        print("4. Delete Record")
        print("5. Read Records")
        print("6. Save Database")
        print("7. Exit")
        
        choice = input("Enter your choice (1-7): ")
        
        if choice == '1':
            table_name = input("Enter table name: ")
            print(db.create_table(table_name))
        
        elif choice == '2':
            table_name = input("Enter table name: ")
            key = input("Enter record key: ")
            data = {}
            while True:
                field = input("Enter field name (or 'done' to finish): ")
                if field.lower() == 'done':
                    break
                value = input(f"Enter value for '{field}': ")
                data[field] = value 
            print(db.insert(table_name, key, data))
        
        elif choice == '3':
            table_name = input("Enter table name: ")
            key = input("Enter record key to update: ")
            data = {}
            while True:
                field = input("Enter field name to update (or 'done' to finish): ")
                if field.lower() == 'done':
                    break
                value = input(f"Enter new value for '{field}': ")
                data[field] = value  # Update user-defined key-value pair
            print(db.update(table_name, key, data))
        
        elif choice == '4':
            table_name = input("Enter table name: ")
            key = input("Enter record key to delete: ")
            print(db.delete(table_name, key))
        
        elif choice == '5':
            table_name = input("Enter table name: ")
            tree = db.tables.get(table_name)
            if tree:
                print("\nStored Records:")
                node = tree.root
                # Traverse to leftmost leaf
                while not node.leaf:
                    node = node.children[0]
                
                # Print all values in leaf nodes
                while node:
                    for i, key in enumerate(node.keys):
                        print(f"Key: {key}, Value: {node.values[i]}")
                    node = node.next_leaf
            else:
                print("No data found in database")
        
        elif choice == '6':
            print("Saving database to disk...")
            db.save_db()
        
        elif choice == '7':
            print("Exiting the program.")
            break
        
        else:
            print("Invalid choice. Please try again.")





if __name__ == "__main__":
    db = demo_db()