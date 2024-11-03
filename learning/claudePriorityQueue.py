# First, let's fix some issues in the original code
class PriorityNode:
    def __init__(self, val, n=None, p=None):
        self.next = n
        self.previous = p
        self.value = val  # Changed from val to value for consistency

class PriorityQueue:
    def __init__(self):
        self.head = None  # Changed from 0 to None
        self.len = 0
    
    def pop(self):
        if self.head is None:
            raise IndexError("Pop from empty queue")
        i = self.head
        self.head = self.head.next
        if self.head is not None:
            self.head.previous = None
        self.len -= 1
        return i.value  # Return value instead of node
    
    def push(self, val):
        self.len += 1
        new_node = PriorityNode(val)
        
        # If queue is empty
        if self.head is None:
            self.head = new_node
            return
            
        # If new value is smaller than head
        if val <= self.head.value:
            new_node.next = self.head
            self.head.previous = new_node
            self.head = new_node
            return
            
        # Find position to insert
        current = self.head
        while current.next and current.next.value < val:
            current = current.next
            
        # Insert after current
        new_node.next = current.next
        new_node.previous = current
        if current.next:
            current.next.previous = new_node
        current.next = new_node
    
    def conv_array(self):
        return [node.value for node in self]
    
    def __repr__(self):
        return repr(self.conv_array())
    
    def __iter__(self):
        self.current = self.head
        return self
    
    def __next__(self):
        if self.current is None:
            raise StopIteration
        node = self.current
        self.current = self.current.next
        return node

# Test cases
import unittest

class TestPriorityQueue(unittest.TestCase):
    def setUp(self):
        self.pq = PriorityQueue()
    
    def test_empty_queue(self):
        """Test operations on empty queue"""
        self.assertEqual(self.pq.len, 0)
        self.assertEqual(self.pq.conv_array(), [])
        with self.assertRaises(IndexError):
            self.pq.pop()
    
    def test_single_element(self):
        """Test operations with single element"""
        self.pq.push(5)
        self.assertEqual(self.pq.len, 1)
        self.assertEqual(self.pq.conv_array(), [5])
        self.assertEqual(self.pq.pop(), 5)
        self.assertEqual(self.pq.len, 0)
    
    def test_multiple_elements_ordered(self):
        """Test pushing elements in ascending order"""
        values = [1, 2, 3, 4, 5]
        for val in values:
            self.pq.push(val)
        self.assertEqual(self.pq.conv_array(), values)
    
    def test_multiple_elements_reversed(self):
        """Test pushing elements in descending order"""
        values = [5, 4, 3, 2, 1]
        for val in values:
            self.pq.push(val)
        self.assertEqual(self.pq.conv_array(), sorted(values))
    
    def test_duplicate_elements(self):
        """Test handling of duplicate values"""
        values = [3, 3, 1, 4, 1, 5]
        for val in values:
            self.pq.push(val)
        self.assertEqual(self.pq.conv_array(), sorted(values))
    
    def test_pop_order(self):
        """Test that elements are popped in correct order"""
        values = [3, 1, 4, 1, 5, 9]
        for val in values:
            self.pq.push(val)
        
        sorted_values = sorted(values)
        popped_values = []
        while self.pq.len > 0:
            popped_values.append(self.pq.pop())
        
        self.assertEqual(popped_values, sorted_values)
    
    def test_iteration(self):
        """Test iterator functionality"""
        values = [3, 1, 4, 1, 5, 9]
        for val in values:
            self.pq.push(val)
        
        iterated_values = [node.value for node in self.pq]
        self.assertEqual(iterated_values, sorted(values))

def run_tests():
    unittest.main(argv=[''], exit=False)
    
# Example usage
def demonstrate_usage():
    pq = PriorityQueue()
    
    print("Pushing values: 3, 1, 4, 1, 5, 9")
    for val in [3, 1, 4, 1, 5, 9]:
        pq.push(val)
        print(f"Queue after pushing {val}: {pq}")
    
    print("\nPopping all values:")
    while pq.len > 0:
        val = pq.pop()
        print(f"Popped: {val}, Remaining queue: {pq}")

if __name__ == "__main__":
    print("Running tests...")
    run_tests()
    print("\nDemonstrating usage:")
    demonstrate_usage()