class Nodo:
    
    def __init__(self, tipo, valor=None, hijos=None):
        self.tipo = tipo
        self.valor = valor
        self.hijos = hijos if hijos is not None else []
        self.id = id(self) # ID único para cada nodo

    def __repr__(self):
        return f"Nodo({self.tipo}, {self.valor})"