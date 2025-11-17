import sys
import matplotlib.pyplot as plt
import networkx as nx
from nodo import Nodo  # <-- IMPORTA NODO

# -----------------------------------------------------------------
# --- FUNCIÓN DE IMAGEN (VERSION CORREGIDA Y MEJORADA) ---
# -----------------------------------------------------------------
def generar_imagen_arbol(raiz, nombre_archivo="arbol_sintactico.png", semantico_valido=False):
    """
    Genera y guarda una imagen del AST con mejoras estéticas.
    """
    G = nx.DiGraph()
    labels = {}
    
    def anadir_nodos_y_aristas(nodo):
        nodo_id = nodo.id
        etiqueta = f"{nodo.tipo}" # Tipo de nodo
        if nodo.valor: # Si tiene valor (ej. identificador, tipo, entero)
            etiqueta += f"\n'{nodo.valor}'" # Añadir valor en una nueva línea

        labels[nodo_id] = etiqueta
        G.add_node(nodo_id)
        
        for hijo in nodo.hijos:
            hijo_id = hijo.id
            G.add_edge(nodo_id, hijo_id)
            anadir_nodos_y_aristas(hijo)

    anadir_nodos_y_aristas(raiz)
    
    # --- CORRECCIÓN: Definir atributos de Graphviz EN EL GRAFO ---
    G.graph['graph'] = {
        'ranksep': '1.5', 
        'nodesep': '0.8'
    }

    plt.figure(figsize=(20, 15)) 
    
    try:
        from networkx.drawing.nx_pydot import graphviz_layout
        
        # --- CORRECCIÓN: Eliminar el argumento 'args' ---
        pos = graphviz_layout(G, prog='dot')
        
        print(f"\nℹ️  Usando Graphviz ('dot') para generar un layout jerárquico y optimizado.")
    except ImportError: 
        print(f"\n⚠️  Advertencia: Graphviz/pydot no funcionó.")
        print("    Asegúrate de tener Graphviz instalado y 'pip install pydot networkx'.")
        print("    Usando un layout genérico 'spring' (menos jerárquico).")
        pos = nx.spring_layout(G, k=0.9, iterations=50) 
    except Exception as e: 
        print(f"\n⚠️  Advertencia: Error al usar Graphviz/pydot ({e}).")
        print("    Usando un layout genérico 'spring' (menos jerárquico).")
        pos = nx.spring_layout(G, k=0.9, iterations=50)

    # Configuración de nodos y aristas (con node_shape='s')
    nx.draw(G, pos, labels=labels, with_labels=True, 
            arrows=True, 
            node_size=4000, 
            node_color='lightgreen', 
            edgecolors='gray', 
            linewidths=1.0, 
            font_size=9, 
            font_weight='bold', 
            font_color='black', 
            node_shape='s', # <-- CORRECCIÓN: 's' para square
            alpha=0.9, 
            edge_color='gray', 
            width=1.5, 
            bbox=dict(facecolor="white", edgecolor='black', boxstyle='round,pad=0.5') 
            )
    
    # Título de la figura
    if semantico_valido:
        plt.title("Árbol de Sintaxis Abstracta (AST) - SEMÁNTICAMENTE VÁLIDO", 
                  color='green', 
                  fontsize=22, 
                  fontweight='bold',
                  pad=20) 
    else:
        plt.title("Árbol de Sintaxis Abstracta (AST) - (Sintaxis OK, Semántica Fallida)", 
                  color='red', 
                  fontsize=18, 
                  fontweight='bold',
                  pad=20)
    
    # --- CORRECCIÓN: Eliminar plt.tight_layout() para silenciar la advertencia ---
    # plt.tight_layout() 
    
    try:
        plt.savefig(nombre_archivo, dpi=300) 
        print(f"🖼️  Imagen del árbol mejorada guardada como '{nombre_archivo}'")
    except Exception as e:
        print(f"❌ Error al guardar la imagen: {e}")
    plt.close()

# -----------------------------------------------------------------
# --- LÓGICA DEL ANÁLISIS SEMÁNTICO ---
# -----------------------------------------------------------------

class TablaSimbolos:
    def __init__(self):
        self.ambitos = [{}] 

    def entrar_ambito(self):
        self.ambitos.append({})

    def salir_ambito(self):
        if len(self.ambitos) > 1:
            self.ambitos.pop()
        else:
            print("Advertencia: Se intentó salir del ámbito global.")

    def declarar(self, nombre, tipo, clase='variable'):
        ambito_actual = self.ambitos[-1]
        if nombre in ambito_actual:
            return False
        
        ambito_actual[nombre] = {'tipo': tipo, 'clase': clase}
        return True

    def buscar(self, nombre):
        for ambito in reversed(self.ambitos):
            if nombre in ambito:
                return ambito[nombre]
        return None


class AnalizadorSemantico:
    def __init__(self):
        self.tabla_simbolos = TablaSimbolos()
        self.errores = []

    def registrar_error(self, mensaje):
        print(f"❌ Error Semántico: {mensaje}")
        self.errores.append(mensaje)

    def analizar(self, arbol_raiz):
        """Punto de entrada. Retorna True si es válido, False si hay errores."""
        try:
            self.visitar(arbol_raiz)
        except Exception as e:
            self.registrar_error(f"Error interno durante la visita: {e}")
            
        if not self.errores:
            print("\n✅ Análisis semántico exitoso. No se encontraron errores.")
        else:
            print(f"\n❌ Falló el análisis semántico. Se encontraron {len(self.errores)} errores.")
        return not self.errores 

    def visitar(self, nodo, **kwargs):
        if not isinstance(nodo, Nodo):
            print(f"Advertencia: Se intentó visitar un objeto que no es un Nodo: {nodo}")
            return None

        metodo_visitante = f"visitar_{nodo.tipo}"

        if hasattr(self, metodo_visitante):
            return getattr(self, metodo_visitante)(nodo, **kwargs)
        else:
            # Método por defecto: visitar todos los hijos
            for hijo in nodo.hijos:
                self.visitar(hijo, **kwargs)
            return None

    # --- MÉTODOS DE VISITA (1 por cada tipo de nodo del AST) ---

    def visitar_programa(self, nodo, **kwargs):
        if nodo.hijos:
            self.visitar(nodo.hijos[0], **kwargs)

    def visitar_Definiciones(self, nodo, **kwargs):
        if not nodo.hijos: return 
        self.visitar(nodo.hijos[0], **kwargs)
        self.visitar(nodo.hijos[1], **kwargs)

    def visitar_Definicion(self, nodo, **kwargs):
        if nodo.hijos:
            self.visitar(nodo.hijos[0], **kwargs)

    def visitar_DefVar(self, nodo, **kwargs):
        if len(nodo.hijos) < 3: return
        tipo_base_nodo = nodo.hijos[0]
        id_nodo = nodo.hijos[1]
        lista_var_nodo = nodo.hijos[2]

        tipo_base = tipo_base_nodo.valor
        nombre_var = id_nodo.valor
        
        if not self.tabla_simbolos.declarar(nombre_var, tipo_base):
            self.registrar_error(f"Variable '{nombre_var}' ya está declarada en este ámbito.")
        
        kwargs['tipo_heredado'] = tipo_base
        self.visitar(lista_var_nodo, **kwargs)

    def visitar_ListaVar(self, nodo, **kwargs):
        if not nodo.hijos: return
        
        tipo_base = kwargs.get('tipo_heredado')
        if not tipo_base:
            self.registrar_error("Error interno: Se perdió el tipo en ListaVar.")
            return

        id_nodo = nodo.hijos[1]
        lista_var_nodo_siguiente = nodo.hijos[2]
        nombre_var = id_nodo.valor

        if not self.tabla_simbolos.declarar(nombre_var, tipo_base):
            self.registrar_error(f"Variable '{nombre_var}' ya está declarada en este ámbito.")

        self.visitar(lista_var_nodo_siguiente, **kwargs)
        
    def visitar_DefFunc(self, nodo, **kwargs):
        if len(nodo.hijos) < 6: return
        tipo_retorno = nodo.hijos[0].valor
        nombre_func = nodo.hijos[1].valor
        
        if not self.tabla_simbolos.declarar(nombre_func, tipo_retorno, clase='funcion'):
            self.registrar_error(f"Función '{nombre_func}' ya está declarada.")
            return

        self.tabla_simbolos.entrar_ambito()
        kwargs['tipo_retorno_func'] = tipo_retorno
        self.visitar(nodo.hijos[3], **kwargs) # <Parametros>
        self.visitar(nodo.hijos[5], **kwargs) # <BloqFunc>
        self.tabla_simbolos.salir_ambito()
        
    def visitar_Parametros(self, nodo, **kwargs):
        if not nodo.hijos: return 
        if len(nodo.hijos) < 3: return
        tipo_param = nodo.hijos[0].valor
        nombre_param = nodo.hijos[1].valor
        if not self.tabla_simbolos.declarar(nombre_param, tipo_param):
            self.registrar_error(f"Parámetro '{nombre_param}' ya está declarado.")
        self.visitar(nodo.hijos[2], **kwargs)
        
    def visitar_ListaParam(self, nodo, **kwargs):
        if not nodo.hijos: return 
        if len(nodo.hijos) < 4: return
        tipo_param = nodo.hijos[1].valor
        nombre_param = nodo.hijos[2].valor
        if not self.tabla_simbolos.declarar(nombre_param, tipo_param):
            self.registrar_error(f"Parámetro '{nombre_param}' ya está declarado.")
        self.visitar(nodo.hijos[3], **kwargs) 

    def visitar_BloqFunc(self, nodo, **kwargs):
        if len(nodo.hijos) > 1:
            self.visitar(nodo.hijos[1], **kwargs) 
    
    def visitar_DefLocales(self, nodo, **kwargs):
        if not nodo.hijos: return 
        self.visitar(nodo.hijos[0], **kwargs) 
        self.visitar(nodo.hijos[1], **kwargs) 
    
    def visitar_DefLocal(self, nodo, **kwargs):
        if nodo.hijos:
            self.visitar(nodo.hijos[0], **kwargs)

    def visitar_Bloque(self, nodo, **kwargs):
        self.tabla_simbolos.entrar_ambito()
        if len(nodo.hijos) > 1:
            self.visitar(nodo.hijos[1], **kwargs) 
        self.tabla_simbolos.salir_ambito()
    
    def visitar_Sentencias(self, nodo, **kwargs):
        if not nodo.hijos: return 
        self.visitar(nodo.hijos[0], **kwargs)
        self.visitar(nodo.hijos[1], **kwargs)
        
    def visitar_Sentencia(self, nodo, **kwargs):
        if not nodo.hijos: return
        primer_hijo = nodo.hijos[0]

        # R21: <Sentencia> ::= identificador = <Expresion> ;
        if (primer_hijo.tipo == 'identificador' and 
            len(nodo.hijos) > 1 and nodo.hijos[1].tipo == '='):
            id_nodo = nodo.hijos[0]
            expr_nodo = nodo.hijos[2]
            
            simbolo = self.tabla_simbolos.buscar(id_nodo.valor)
            if not simbolo:
                self.registrar_error(f"Variable '{id_nodo.valor}' no ha sido declarada.")
                return
            if simbolo['clase'] == 'funcion':
                self.registrar_error(f"No se puede asignar un valor a una función '{id_nodo.valor}'.")
                return

            tipo_variable = simbolo['tipo']
            tipo_expresion = self.visitar(expr_nodo, **kwargs)
            
            if tipo_expresion:
                if tipo_variable == 'float' and tipo_expresion == 'int':
                    pass # Válido
                elif tipo_variable != tipo_expresion:
                    self.registrar_error(f"Error de Tipos: No se puede asignar tipo '{tipo_expresion}' "
                                         f"a la variable '{id_nodo.valor}' (de tipo '{tipo_variable}').")

        # R22: <Sentencia> ::= if ( <Expresion> ) <SentenciaBloque> <Otro>
        elif primer_hijo.tipo == 'if':
            tipo_condicion = self.visitar(nodo.hijos[2], **kwargs)
            if tipo_condicion and tipo_condicion not in ('int', 'float'):
                 self.registrar_error(f"La condición del 'if' debe ser un número (int/float), no '{tipo_condicion}'.")
            self.visitar(nodo.hijos[4], **kwargs)
            self.visitar(nodo.hijos[5], **kwargs)
        
        # ... (Resto de visitantes semánticos) ...
        else:
            for hijo in nodo.hijos:
                self.visitar(hijo, **kwargs)

    def visitar_Expresion(self, nodo, **kwargs):
        if not nodo.hijos: return None
        
        # R52: <Expresion> ::= <Termino>
        if len(nodo.hijos) == 1 and nodo.hijos[0].tipo == 'Termino':
            return self.visitar(nodo.hijos[0], **kwargs)
        
        # R46-R51: Operadores binarios (A + B)
        if len(nodo.hijos) == 3:
            tipo_izq = self.visitar(nodo.hijos[0], **kwargs)
            op_nodo = nodo.hijos[1]
            tipo_der = self.visitar(nodo.hijos[2], **kwargs)
            
            if not tipo_izq or not tipo_der:
                return None
            
            if op_nodo.tipo in ('opMul', 'opSuma'):
                if tipo_izq not in ('int', 'float') or tipo_der not in ('int', 'float'):
                    self.registrar_error(f"Operación aritmética '{op_nodo.valor}' no válida entre '{tipo_izq}' y '{tipo_der}'.")
                    return None
                if tipo_izq == 'float' or tipo_der == 'float':
                    return 'float'
                return 'int'
            
            # (Resto de operadores)
            return 'int' # Asumir int para relacionales/lógicos
                
        return None

    def visitar_Termino(self, nodo, **kwargs):
        if not nodo.hijos: return None
        hijo = nodo.hijos[0]
        
        if hijo.tipo == 'identificador':
            simbolo = self.tabla_simbolos.buscar(hijo.valor)
            if not simbolo:
                self.registrar_error(f"Variable '{hijo.valor}' no ha sido declarada.")
                return None
            if simbolo['clase'] == 'funcion':
                 self.registrar_error(f"No se puede usar el nombre de la función '{hijo.valor}' como una variable.")
                 return None
            return simbolo['tipo']
        
        if hijo.tipo == 'entero': return 'int'
        if hijo.tipo == 'real': return 'float'
        if hijo.tipo == 'cadena': return 'string'
        
        if hijo.tipo == 'LlamadaFunc':
            return self.visitar(hijo, **kwargs)
        return None

    def visitar_LlamadaFunc(self, nodo, **kwargs):
        if len(nodo.hijos) < 4: return None
        nombre_func = nodo.hijos[0].valor
        simbolo_func = self.tabla_simbolos.buscar(nombre_func)
        if not simbolo_func:
            self.registrar_error(f"Función '{nombre_func}' no ha sido declarada.")
            return None
        return simbolo_func['tipo']