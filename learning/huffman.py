from priorityQueue import PriorityQueue
import struct

def frequencies(text):
     freq={}
     for c in text:
          freq.setdefault(c,0)
          freq[c]+=1
     return freq


class HuffmanNode:

     def __init__(self,char_list,freq=0,left=None,right=None):
          self.char_list=char_list
          self.freq=freq
          self.left=left
          self.right=right
     
     def __repr__(self):
          return f"<HuffmanNode: char_list={self.char_list} , freq = {self.freq} , left= {self.left} , right = {self.right}"
     

     def __lt__(self,other):
          return self.freq < other.freq
     
     def __le__(self,other):
          return self.freq <= other.freq

     def __gt__(self,other):
          return self.freq > other.freq
     
     def __ge__(self,other):
          return self.freq >= other.freq
     

class HuffmanTree:

     def build_tree(self, text):
          if not text:
               raise ValueError
          
          self.input=text
          self.char_freq=frequencies(text)
          pqueue=PriorityQueue()
          for k,v in self.char_freq.items():
               pqueue.push(HuffmanNode([k],v,None,None))

          left=pqueue.pop()
          right=pqueue.pop()

          while left and right:
               pqueue.push(HuffmanNode(left.char_list + right.char_list, left.freq+right.freq,left,right))
               left=pqueue.pop()
               right=pqueue.pop()
          
          self.head=left

          self.code_dict={}
          for c in self.head.char_list:
               self.code_dict[c]=self.get_code(c)
     
     def get_code(self,char):
          if hasattr(self,'code_dict'):
               if char in self.code_dict:
                    return self.code_dict[char]

          n=self.head
          if not n.left and not n.right:
               length=1
               code=1
          else:
               length=0
               code=0
          while n.left or n.right:
               if n.left and char in n.left.char_list:
                    code = (code << 1) | 1
                    n = n.left
                    length += 1
               elif n.right and char in n.right.char_list:
                    code = (code << 1) | 0
                    length += 1
                    n = n.right

          return length, code
     # Add this method to your HuffmanTree class:
     def print_tree(self):
          if self.head:
               print("Huffman Tree:")
               print_tree(self.head)

     def encode_tree(self):
          if hasattr(self,'encoded_tree'):
               return self.encoded_tree
          else:
               out=struct.pack("H",len(self.head.char_list))
               for i in self.head.char_list:
                    length, code =self.get_code(i)
                    out+=struct.pack("B",ord(i))
                    out+=struct.pack("B",length)
                    out+=struct.pack("H",code)
               return out
     def encode(self,text):
          output=self.encode_tree()
          byte=0
          num_bits=0
          total_length=0

          for c in text:
               length, code = self.get_code(c)

               byte=(byte << length) | code
               num_bits+=length

               if num_bits >8:
                    overflow = num_bits-8

                    output+= struct.pack("B",byte >> overflow)
                    total_length+=1

                    byte=byte & ((1<<overflow)-1)
                    num_bits=overflow
               
          if num_bits !=0:
               padding = 8 - num_bits

               output+= struct.pack("B", byte << padding)
               total_length+=1
          return output
     
     def decode(self,buf):
          char_list=[]
          codes={}
          header_length=struct.unpack_from("H", buf)[0] * 4 + 2
          for i in range(2, header_length, 4):
            char, code_length, code = struct.unpack_from("BBH", buf, i)
            char_list.append(chr(char))
            codes[chr(char)] = (code_length, code)
          self.char_list = char_list
          self.code_dict = codes



def print_tree(node, prefix="", is_left=True):
    if node is None:
        return
    
    # Create the indentation string
    indent = prefix + ("└── " if is_left else "├── ")
    
    # Print the current node
    if node.left is None and node.right is None:  # leaf node
        # For leaf nodes, show char and frequency
        chars = ''.join(node.char_list)
        print(f"{indent}[{chars}: {node.freq}]")
    else:
        # For internal nodes, show frequency and total chars
        chars = ''.join(node.char_list)
        print(f"{indent}({chars}: {node.freq})")
    
    # Recursively print left and right subtrees
    if node.left:
        new_prefix = prefix + ("    " if is_left else "│   ")
        print_tree(node.left, new_prefix, True)
    if node.right:
        new_prefix = prefix + ("    " if is_left else "│   ")
        print_tree(node.right, new_prefix, False)



if __name__ == "__main__":
    tree = HuffmanTree()
    tree.build_tree("ABABCDABCDE")
    tree.print_tree()
    print("\nHuffman Codes:")
    for char in sorted(tree.char_freq.keys()):
        length, code = tree.get_code(char)
        # Convert code to binary string of correct length
        binary = bin(code)[2:].zfill(length)
        print(f"{char}: {binary} ({length} bits)")