from lark import Transformer as t

class Transformer(t):
    class Node:
        def __init__(self, value):
            self.value = value
        
        def __repr__(self):
            return f"{self.__class__.__name__}({self.value})"

        def get(self):
            return self.value
    
    class start(Node):pass

    def transform(self, tree) -> start:
        return super().transform(tree)
    
    class code_block(Node):
        def __repr__(self):
            return repr(self.value[0]) + "{" + "; ".join([repr(value) for value in self.value[1:]]) + "}"
    
    class instruction(Node):
        def __repr__(self):
            return f"{self.value[0]}({", ".join([repr(value) for value in self.value[1:]])})"

    class register(Node):
        def __init__(self, value):
            value[0] = value[0].lower()
            super().__init__(value)
        def __repr__(self):
            return f"register {self.value[0]}"
    class immediate(Node):
        def __repr__(self):
            return f"immediate {self.value[0]}"
    class address(Node):
        def __repr__(self):
            return f"deref {self.value[0]}"

    class constantdef(Node):
        def __repr__(self):
            return f"{self.value[0]} = {self.value[1]}"
    
    class labeldef(Node):
        def __repr__(self):
            return f"label {self.value[0]}"

    class or_op(Node):
        def __repr__(self):
            return f"<{self.value[0]} | {self.value[1]}>"
    class and_op(Node):
        def __repr__(self):
            return f"<{self.value[0]} & {self.value[1]}>"
    class add(Node):
        def __repr__(self):
            return f"<{self.value[0]} + {self.value[1]}>"
    class sub(Node):
        def __repr__(self):
            return f"<{self.value[0]} - {self.value[1]}>"

    class literal(Node):
        def __repr__(self):
            return f"lit {self.value[0]}"

    class IDENTIFIER(Node):
        def __repr__(self):
            return f"identifer {self.value}"
        
    class DECIMAL(Node):
        def __repr__(self):
            return f"decimal {self.value}"
    class BINARY(Node):
        def __repr__(self):
            return f"0b{self.value}"
    class OCTAL(Node):
        def __repr__(self):
            return f"0o{self.value}"
    class HEX(Node):
        def __init__(self, value):
            value = value.lower()
            super().__init__(value)

        def __repr__(self):
            return f"0x{self.value}"