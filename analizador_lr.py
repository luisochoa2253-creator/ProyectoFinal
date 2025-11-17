import re
import pandas as pd

class AnalizadorLR:
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
        return tokens

    def analizar(self, expr):
        """
        Versión modificada: Retorna True si es aceptada, False si hay error.
        Imprime el seguimiento de la pila para depuración.
        """
        if not expr.strip().endswith('$'):
            expr += '$'
            
        tokens = self._tokenize(expr)
        pila = [0]
        i = 0

        print(f"\nAnalizando: '{expr.strip()}'")
        print("-" * 110)
        print(f"{'PILA':<45}{'ENTRADA':<45}{'ACCION'}")
        print("-" * 110)

        while True:
            if i >= len(tokens):
                print("❌ Error: Se alcanzó el final de los tokens inesperadamente.")
                return False # MODIFICADO

            estado = pila[-1]
            simbolo, lexema = tokens[i]
            
            pila_str = ' '.join(str(s) for s in pila)
            entrada_str = ' '.join(t[1] for t in tokens[i:i+15])
            if len(tokens) > i + 15:
                entrada_str += ' ...'

            accion = self.tabla_accion.get((estado, simbolo))
            
            if not accion:
                print(f"{pila_str:<45}{entrada_str:<45}{'ERROR'}")
                print("-" * 110)
                print(f"❌ Error de sintaxis: No hay acción para estado {estado} y símbolo '{simbolo}' ('{lexema}')")
                return False # MODIFICADO

            if accion.startswith("d"):
                accion_str = f"Desplazar {accion[1:]}"
                print(f"{pila_str:<45}{entrada_str:<45}{accion_str}")
                
                nuevo_estado = int(accion[1:])
                pila.append(simbolo)
                pila.append(nuevo_estado)
                i += 1
            elif accion.startswith("r"):
                num_regla = int(accion[1:])
                
                if num_regla == 1: # Asumiendo R1 como aceptación
                    print(f"{pila_str:<45}{entrada_str:<45}{'Aceptar'}")
                    print("-" * 110)
                    print("\n✅ Cadena aceptada (Paso 1)")
                    return True # MODIFICADO
                
                izq, der = self.reglas[num_regla]
                cuerpo_regla = ' '.join(der) if der else 'ε'
                accion_str = f"Reducir por R{num_regla}: {izq} -> {cuerpo_regla}"
                print(f"{pila_str:<45}{entrada_str:<45}{accion_str}")
                
                for _ in range(2 * len(der)):
                    pila.pop()
                
                estado_anterior = pila[-1]
                goto_estado = self.tabla_goto.get((estado_anterior, izq))
                if goto_estado is None:
                    print("-" * 110)
                    print(f"❌ Error GOTO: No hay transición para estado {estado_anterior} y no terminal '{izq}'")
                    return False # MODIFICADO
                pila.append(izq)
                pila.append(goto_estado)
            elif accion.lower() == "acc":
                print(f"{pila_str:<45}{entrada_str:<45}{'Aceptar'}")
                print("-" * 110)
                print("\n✅ Cadena aceptada (Paso 1)")
                return True # MODIFICADO
            else:
                print("-" * 110)
                print(f"❌ Error: Acción desconocida '{accion}'.")
                return False # MODIFICADO
            
            print("-" * 110)

# Este archivo ya no se ejecuta solo, es importado por main.py
# Por lo tanto, el bloque if __name__ == "__main__": se elimina.