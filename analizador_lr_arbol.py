import re
import pandas as pd
from nodo import Nodo  # <-- IMPORTA NODO

def imprimir_arbol(nodo, prefijo="", es_ultimo=True):
    """Imprime el árbol de forma recursiva para una fácil visualización."""
    if not isinstance(nodo, Nodo):
        print(f"Error: Se intentó imprimir algo que no es un Nodo: {nodo}")
        return
    print(prefijo + ("└── " if es_ultimo else "├── ") + f"{nodo.tipo}" + (f": '{nodo.valor}'" if nodo.valor else ""))
    hijos = nodo.hijos
    for i, hijo in enumerate(hijos):
        es_hijo_ultimo = (i == len(hijos) - 1)
        nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")
        imprimir_arbol(hijo, nuevo_prefijo, es_hijo_ultimo)


class AnalizadorLR:
    """
    Esta versión del AnalizadorLR está diseñada para
    construir y retornar el Árbol de Sintaxis Abstracta (AST).
    """
    def __init__(self, archivo_lr, archivo_csv, archivo_inf):
        df = pd.read_csv(archivo_csv)
        df.rename(columns={df.columns[0]: 'estado'}, inplace=True)
        self.simbolos = list(df.columns)[1:] 

        self.reglas = {}
        self.tabla_accion = {}
        self.tabla_goto = {}

        self._cargar_reglas_desde_inf(archivo_inf)
        self._cargar_tabla_desde_csv(df)

    def _cargar_reglas_desde_inf(self, archivo_inf):
        with open(archivo_inf, "r", encoding="utf-8") as f:
            content = f.read()
        rule_definitions = re.findall(r'R(\d+)\s+<([^>]+)>\s*::=\s*(.*)', content)
        for num, no_terminal, cuerpo in rule_definitions:
            num = int(num)
            elementos_rhs = []
            if cuerpo.strip() != '\\e':
                elementos_rhs = re.findall(r'<[^>]+>|\S+', cuerpo)
            no_terminal_limpio = no_terminal.strip()
            elementos_rhs_limpios = [s.replace('<', '').replace('>', '').strip() for s in elementos_rhs]
            self.reglas[num] = (no_terminal_limpio, elementos_rhs_limpios)

    def _cargar_tabla_desde_csv(self, df):
        terminales = []
        no_terminales = []
        for s in self.simbolos:
            if s and (s[0].isupper() or s.startswith("op")):
                no_terminales.append(s)
            else:
                terminales.append(s)
        
        for s in self.simbolos:
            if re.match(r"^[A-Z]", s) and s not in no_terminales:
                 no_terminales.append(s)
                 if s in terminales: terminales.remove(s)
            elif not re.match(r"^[A-Z]", s) and s not in terminales:
                 terminales.append(s)
                 if s in no_terminales: no_terminales.remove(s)

        for i, row in df.iterrows():
            estado = row['estado']
            for simbolo in self.simbolos:
                accion = row[simbolo]
                if pd.isna(accion) or accion == '0':
                    continue
                if simbolo in terminales:
                    self.tabla_accion[(estado, simbolo)] = str(accion)
                elif simbolo in no_terminales:
                    self.tabla_goto[(estado, simbolo)] = int(accion)

    def _tokenize(self, code):
        token_specification = [
            ('tipo',        r'\b(int|float|void|char|string)\b'),
            ('if',          r'\bif\b'),
            ('while',       r'\bwhile\b'),
            ('return',      r'\breturn\b'),
            ('else',        r'\belse\b'),
            ('cadena',      r'"[^"]*"'),
            ('identificador',r'[A-Za-z_][A-Za-z0-9_]*'),
            ('real',        r'\d+\.\d+'),
            ('entero',      r'\d+'),
            ('opSuma',      r'[+\-]'),
            ('opMul',       r'[*/]'),
            ('opRelac',     r'<=|>=|<|>'),
            ('opIgualdad',  r'==|!='),
            ('opAnd',       r'&&'),
            ('opOr',        r'\|\|'),
            ('opNot',       r'!'),
            ('ASIGN',       r'='),
            ('PUNTOCOMA',   r';'),
            ('COMA',        r','),
            ('LPAREN',      r'\('),
            ('RPAREN',      r'\)'),
            ('LBRACE',      r'{'),
            ('RBRACE',      r'}'),
            ('PESOS',       r'\$'),
            ('ESPACIO',     r'\s+'),
            ('DESCONOCIDO', r'.'),
        ]
        
        symbol_map = {
            'ASIGN': '=', 'PUNTOCOMA': ';', 'COMA': ',',
            'LPAREN': '(', 'RPAREN': ')', 'LBRACE': '{',
            'RBRACE': '}', 'PESOS': '$'
        }

        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
        tokens = []
        for mo in re.finditer(tok_regex, code):
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'ESPACIO':
                continue
            elif kind == 'DESCONOCIDO':
                print(f"Caracter desconocido: '{value}'")
                continue
            token_kind = symbol_map.get(kind, kind)
            tokens.append((token_kind, value))
        
        if not tokens or tokens[-1][0] != '$':
            if '$' not in [t[0] for t in tokens]:
                 tokens.append(('$', '$'))

        return tokens

    def analizar(self, expr):
        """
        Versión del analizador que construye y retorna el AST.
        Retorna un Nodo (raíz del AST) en éxito, o None en error.
        """
        if not expr.strip().endswith('$'):
            expr += '$'
            
        tokens = self._tokenize(expr)
        pila_estados = [0]
        pila_valores = [] # Pila para los nodos del AST
        i = 0

        while True:
            if i >= len(tokens):
                print("❌ Error: Se alcanzó el final de los tokens inesperadamente.")
                return None

            estado_actual = pila_estados[-1]
            simbolo, lexema = tokens[i]
            accion = self.tabla_accion.get((estado_actual, simbolo))
            
            if not accion:
                return None

            if accion.startswith("d"):
                nuevo_estado = int(accion[1:])
                pila_valores.append(Nodo(tipo=simbolo, valor=lexema))
                pila_estados.append(nuevo_estado)
                i += 1
            elif accion.startswith("r"):
                num_regla = int(accion[1:])
                
                if num_regla == 1: 
                    return pila_valores[0]
                
                izq, der = self.reglas[num_regla]
                
                nodos_hijos = []
                if len(der) > 0:
                    nodos_hijos = pila_valores[-len(der):]
                    pila_valores = pila_valores[:-len(der)]
                
                nodo_padre = Nodo(tipo=izq, hijos=nodos_hijos)
                pila_valores.append(nodo_padre)

                for _ in range(len(der)):
                    pila_estados.pop()
                
                estado_anterior = pila_estados[-1]
                goto_estado = self.tabla_goto.get((estado_anterior, izq))
                if goto_estado is None:
                    return None
                pila_estados.append(goto_estado)
            elif accion.lower() == "acc":
                return pila_valores[0] 
            else:
                return None