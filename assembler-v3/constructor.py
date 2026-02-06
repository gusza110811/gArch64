from __future__ import annotations
from typing import TYPE_CHECKING
from memory import Memory
from parser import Transformer

class Constructor:
    def __init__(self):
        self.globals = Memory()

        self.locals = [self.globals]

        self.ir=[]
    
    def add_label(self):
        pass

    def make_local(self):
        local = Memory()
        self.locals.append(local)
        return local

    def main(self,ast:Transformer.start,filename="<main>"):

        ast.eval(self.globals)

        return
