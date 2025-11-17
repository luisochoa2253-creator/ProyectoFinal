from nodo import Nodo  # <-- IMPORTA NODO

class GeneradorASM:
    def __init__(self):
        self.seccion_data = []
        self.seccion_code_global = [] 
        
        # Mapa de variables: {'nombre': {'dir': '[ebp-4]', 'tipo': 'int'}}
        self.mapa_variables_locales = {}
        self.mapa_variables_globales = {}
        
        self.offset_pila_actual = 0 
        self.offset_pila_parametros = 8
        self.codigo_func_actual = [] 
        self.contador_etiquetas = 0
        self.mapa_cadenas = {}
        self.contador_cadenas = 0
        self.mapa_reales = {}
        self.contador_reales = 0

    def nueva_etiqueta(self):
        self.contador_etiquetas += 1
        return f"_L{self.contador_etiquetas}"

    def obtener_o_crear_cadena(self, texto):
        if texto in self.mapa_cadenas:
            return self.mapa_cadenas[texto]
        etiqueta = f"_S{self.contador_cadenas}"
        self.contador_cadenas += 1
        if texto == "formato_int_nl":
            self.seccion_data.append(f"    {etiqueta} DB '%d', 0Ah, 0")
        elif texto == "formato_float_nl":
            self.seccion_data.append(f"    {etiqueta} DB '%f', 0Ah, 0")
        else:
            self.seccion_data.append(f"    {etiqueta} DB '{texto}', 0")
        self.mapa_cadenas[texto] = etiqueta
        return etiqueta

    def obtener_o_crear_real(self, numero_real):
        if numero_real in self.mapa_reales:
            return self.mapa_reales[numero_real]
        etiqueta = f"_R{self.contador_reales}"
        self.contador_reales += 1
        self.seccion_data.append(f"    {etiqueta} REAL4 {numero_real}")
        self.mapa_reales[numero_real] = etiqueta
        return etiqueta

    def generar(self, arbol_raiz):
        self.visitar(arbol_raiz) 
        
        encabezado = [
            ".386",
            ".model flat, C", 
            "option casemap:none",
            
            " ; --- Librerias a incluir ---",
            "includelib msvcrt.lib",
            "includelib kernel32.lib", # <-- BUENA PRÁCTICA AÑADIR ESTA
            
            " ; --- Prototipos ---",
            # CORRECCIÓN: Le decimos a MASM que printf es 'C' (default)
            "printf PROTO, :VARARG", 
            # CORRECCIÓN: Le decimos a MASM que ExitProcess es 'stdcall'
            "ExitProcess PROTO stdcall, dwExitCode:DWORD",
        ]
        
        data = ["\n.data"] + self.seccion_data
        
        code_start = [
            "\n.code",
            "start:",
            "    call _main",
            "\n    ; --- Rutina de Salida ---",
            "    ; El valor de retorno de _main está en EAX",
            "    push  eax            ; <-- ¡ESTE ES EL CAMBIO!",
            "    call  ExitProcess"
        ]
        
        code_funciones = self.seccion_code_global
        final = ["\nEND start"]
        asm_completo = "\n".join(encabezado + data + code_start + code_funciones + final)
        
        return asm_completo

    # --- Métodos Visitantes ---
    
    def visitar(self, nodo, **kwargs):
        if not isinstance(nodo, Nodo): return
        metodo_visitante = f"visitar_{nodo.tipo}"
        if hasattr(self, metodo_visitante):
            return getattr(self, metodo_visitante)(nodo, **kwargs)
        else:
            for hijo in nodo.hijos: self.visitar(hijo, **kwargs)
            return None

    def visitar_programa(self, nodo, **kwargs):
        self.visitar(nodo.hijos[0], **kwargs) 

    def visitar_Definiciones(self, nodo, **kwargs):
        if not nodo.hijos: return 
        self.visitar(nodo.hijos[0], **kwargs) 
        self.visitar(nodo.hijos[1], **kwargs) 
    
    def visitar_Definicion(self, nodo, **kwargs):
        self.visitar(nodo.hijos[0], **kwargs)
    
    def visitar_DefVar(self, nodo, **kwargs):
        nombre_var = nodo.hijos[1].valor
        tipo_var = nodo.hijos[0].valor
        self.mapa_variables_globales[nombre_var] = {'dir': f"_[{nombre_var}]", 'tipo': tipo_var}
        if tipo_var == 'float':
            self.seccion_data.append(f"    _{nombre_var} REAL4 0.0")
        else:
            self.seccion_data.append(f"    _{nombre_var} DWORD 0")

    # --- VISITANTES DE FUNCIONES ---

    def visitar_DefFunc(self, nodo, **kwargs):
        nombre_func = nodo.hijos[1].valor
        self.mapa_variables_locales = {}
        self.offset_pila_actual = 0
        self.offset_pila_parametros = 8
        self.codigo_func_actual = [] 

        self.visitar(nodo.hijos[3], **kwargs) # Visita <Parametros>
        self.visitar(nodo.hijos[5], **kwargs) # Visita <BloqFunc>

        asm_func = []
        asm_func.append(f"\n_{nombre_func}:") 
        asm_func.append("    push ebp")
        asm_func.append("    mov ebp, esp")
        if self.offset_pila_actual > 0:
            asm_func.append(f"    sub esp, {self.offset_pila_actual}  ; Reservar espacio para locales")

        asm_func += self.codigo_func_actual

        asm_func.append(f"    ; --- Epilogo (fallback) de _{nombre_func} ---")
        asm_func.append("    mov esp, ebp")
        asm_func.append("    pop ebp")
        asm_func.append("    ret")
        
        self.seccion_code_global += asm_func

    # --- VISITANTES DE PARÁMETROS ---

    def visitar_Parametros(self, nodo, **kwargs):
        if not nodo.hijos: return
        tipo_param = nodo.hijos[0].valor
        nombre_param = nodo.hijos[1].valor
        direccion_param = f"[ebp+{self.offset_pila_parametros}]"
        self.mapa_variables_locales[nombre_param] = {'dir': direccion_param, 'tipo': tipo_param}
        self.offset_pila_parametros += 4
        self.visitar(nodo.hijos[2], **kwargs) 
        
    def visitar_ListaParam(self, nodo, **kwargs):
        if not nodo.hijos: return
        tipo_param = nodo.hijos[1].valor
        nombre_param = nodo.hijos[2].valor
        direccion_param = f"[ebp+{self.offset_pila_parametros}]"
        self.mapa_variables_locales[nombre_param] = {'dir': direccion_param, 'tipo': tipo_param}
        self.offset_pila_parametros += 4
        self.visitar(nodo.hijos[3], **kwargs)

    def visitar_BloqFunc(self, nodo, **kwargs):
        self.visitar(nodo.hijos[1], **kwargs) 

    def visitar_DefLocales(self, nodo, **kwargs):
        if not nodo.hijos: return
        self.visitar(nodo.hijos[0], **kwargs) 
        self.visitar(nodo.hijos[1], **kwargs) 

    def visitar_DefLocal(self, nodo, **kwargs):
        tipo_hijo = nodo.hijos[0].tipo
        if tipo_hijo == 'DefVar':
            var_nodo = nodo.hijos[0]
            tipo_var = var_nodo.hijos[0].valor
            nombre_var = var_nodo.hijos[1].valor
            self.offset_pila_actual += 4 
            direccion_var = f"[ebp-{self.offset_pila_actual}]" 
            self.mapa_variables_locales[nombre_var] = {'dir': direccion_var, 'tipo': tipo_var}
            kwargs['tipo_heredado'] = tipo_var
            self.visitar(var_nodo.hijos[2], **kwargs) 
        elif tipo_hijo == 'Sentencia':
            self.visitar(nodo.hijos[0], **kwargs)
        else:
            self.visitar(nodo.hijos[0], **kwargs)

    def visitar_ListaVar(self, nodo, **kwargs):
        if not nodo.hijos: return
        tipo_heredado = kwargs.get('tipo_heredado', 'int')
        nombre_var = nodo.hijos[1].valor
        self.offset_pila_actual += 4 
        direccion_var = f"[ebp-{self.offset_pila_actual}]" 
        self.mapa_variables_locales[nombre_var] = {'dir': direccion_var, 'tipo': tipo_heredado}
        self.visitar(nodo.hijos[2], **kwargs)

    # --- VISITANTES DE SENTENCIAS ---
    
    def visitar_Sentencia(self, nodo, **kwargs):
        primer_hijo = nodo.hijos[0]

        # R21: Asignación
        if (primer_hijo.tipo == 'identificador' and 
            len(nodo.hijos) > 1 and nodo.hijos[1].tipo == '='):
            
            nombre_var = nodo.hijos[0].valor
            info_var = self.mapa_variables_locales.get(nombre_var)
            if not info_var: info_var = self.mapa_variables_globales.get(nombre_var)
            if not info_var:
                print(f"Error de generación: Variable '{nombre_var}' no encontrada.")
                return

            tipo_resultado = self.visitar(nodo.hijos[2], **kwargs)
            
            # --- CORRECCIÓN A2023: Añadir DWORD/QWORD PTR ---
            if info_var['tipo'] == 'int' and tipo_resultado == 'int':
                self.codigo_func_actual.append(f"    mov {info_var['dir']}, eax  ; {nombre_var} = EAX")
            
            elif info_var['tipo'] == 'float' and tipo_resultado == 'float':
                self.codigo_func_actual.append(f"    fstp DWORD PTR {info_var['dir']}  ; {nombre_var} = st(0) (float)")
            
            elif info_var['tipo'] == 'float' and tipo_resultado == 'int':
                self.codigo_func_actual.append("    push eax")
                self.codigo_func_actual.append("    fild DWORD PTR [esp] ; Cargar int de pila a st(0)")
                self.codigo_func_actual.append("    add esp, 4")
                self.codigo_func_actual.append(f"    fstp DWORD PTR {info_var['dir']}  ; {nombre_var} = st(0) (float)")
            
            elif info_var['tipo'] == 'int' and tipo_resultado == 'float':
                self.codigo_func_actual.append(f"    fistp DWORD PTR {info_var['dir']} ; {nombre_var} = st(0) (truncado)")
        
        # R23: while
        elif primer_hijo.tipo == 'while':
            etiqueta_inicio = self.nueva_etiqueta() 
            etiqueta_fin = self.nueva_etiqueta()   
            
            self.codigo_func_actual.append(f"{etiqueta_inicio}:")
            tipo_resultado = self.visitar(nodo.hijos[2], **kwargs)
            if tipo_resultado == 'float':
                self.codigo_func_actual.append("    fldz")
                self.codigo_func_actual.append("    fcomip st(0), st(1)")
                self.codigo_func_actual.append("    fstp st(0)")
                self.codigo_func_actual.append("    fnstsw ax")
                self.codigo_func_actual.append("    sahf")
                self.codigo_func_actual.append(f"    je {etiqueta_fin}")
            else:
                self.codigo_func_actual.append("    cmp eax, 0")
                self.codigo_func_actual.append(f"    je {etiqueta_fin}")

            self.visitar(nodo.hijos[4], **kwargs)
            self.codigo_func_actual.append(f"    jmp {etiqueta_inicio}")
            self.codigo_func_actual.append(f"{etiqueta_fin}:")
        
        # R25: <LlamadaFunc>
        elif primer_hijo.tipo == 'LlamadaFunc':
            self.visitar(primer_hijo, **kwargs)
        
        # R24: return
        elif primer_hijo.tipo == 'return':
            self.visitar(nodo.hijos[1], **kwargs) 
            self.codigo_func_actual.append("    ; --- return ---")
            self.codigo_func_actual.append("    mov esp, ebp")
            self.codigo_func_actual.append("    pop ebp")
            self.codigo_func_actual.append("    ret")
        
        # R22: if
        elif primer_hijo.tipo == 'if':
            nodo_otro = nodo.hijos[5]
            tiene_else = bool(nodo_otro.hijos) 
            etiqueta_else = self.nueva_etiqueta()
            etiqueta_fin = self.nueva_etiqueta() if tiene_else else etiqueta_else
            
            tipo_resultado = self.visitar(nodo.hijos[2], **kwargs)
            if tipo_resultado == 'float':
                self.codigo_func_actual.append("    fldz")
                self.codigo_func_actual.append("    fcomip st(0), st(1)")
                self.codigo_func_actual.append("    fstp st(0)")
                self.codigo_func_actual.append("    fnstsw ax")
                self.codigo_func_actual.append("    sahf")
                self.codigo_func_actual.append(f"    je {etiqueta_else}")
            else:
                self.codigo_func_actual.append("    cmp eax, 0")
                self.codigo_func_actual.append(f"    je {etiqueta_else}")

            self.visitar(nodo.hijos[4], **kwargs)
            
            if tiene_else:
                self.codigo_func_actual.append(f"    jmp {etiqueta_fin}")
            self.codigo_func_actual.append(f"{etiqueta_else}:")
            if tiene_else:
                self.visitar(nodo_otro, **kwargs) 
                self.codigo_func_actual.append(f"{etiqueta_fin}:")
        
        else:
            for hijo in nodo.hijos:
                self.visitar(hijo, **kwargs)

    def visitar_ValorRegresa(self, nodo, **kwargs):
        if nodo.hijos:
            return self.visitar(nodo.hijos[0], **kwargs) 
        else:
            self.codigo_func_actual.append("    mov eax, 0")
            return 'int'

    # --- VISITANTE Expresion (¡CORREGIDO!) ---
    def visitar_Expresion(self, nodo, **kwargs):
        
        # R52: <Expresion> ::= <Termino>
        if len(nodo.hijos) == 1 and nodo.hijos[0].tipo == 'Termino':
            return self.visitar(nodo.hijos[0], **kwargs)

        # R46-R51: Operaciones Binarias
        if len(nodo.hijos) == 3 and nodo.hijos[0].tipo != '(':
            
            # 1. Visitar operando DERECHO
            tipo_der = self.visitar(nodo.hijos[2], **kwargs)
            
            # 2. Guardar resultado de la derecha
            if tipo_der == 'int':
                self.codigo_func_actual.append("    push eax  ; Guardar int (der) en pila")
            else:
                # (float (der) ya está en st(0))
                pass
            
            # 3. Visitar operando IZQUIERDO
            tipo_izq = self.visitar(nodo.hijos[0], **kwargs)
            # (resultado de izq está en EAX o st(0))
            
            # 4. Decidir el tipo de operación
            operador = nodo.hijos[1]
            es_comparacion = operador.tipo in ('opRelac', 'opIgualdad')
            
            # --- CASO 1: INT op INT ---
            if tipo_izq == 'int' and tipo_der == 'int':
                self.codigo_func_actual.append("    pop ebx      ; Recuperar int (der) a EBX")
                if not es_comparacion:
                    if operador.tipo == 'opSuma':
                        if operador.valor == '+': self.codigo_func_actual.append("    add eax, ebx")
                        elif operador.valor == '-': self.codigo_func_actual.append("    sub eax, ebx")
                    elif operador.tipo == 'opMul':
                        if operador.valor == '*': self.codigo_func_actual.append("    imul eax, ebx")
                        elif operador.valor == '/':
                            self.codigo_func_actual.append("    cdq")
                            self.codigo_func_actual.append("    idiv ebx")
                    return 'int'
                else:
                    self.codigo_func_actual.append("    cmp eax, ebx")
            
            # --- CASO 2: FLOAT op FLOAT (o MIXTO) ---
            else:
                # --- CORRECCIÓN A2023: Añadir DWORD/QWORD PTR ---
                if tipo_izq == 'int':
                    self.codigo_func_actual.append("    push eax")
                    self.codigo_func_actual.append("    fild DWORD PTR [esp]")
                    self.codigo_func_actual.append("    add esp, 4")
                if tipo_der == 'int':
                    self.codigo_func_actual.append("    fild DWORD PTR [esp]")
                    self.codigo_func_actual.append("    add esp, 4")
                
                if not es_comparacion:
                    if operador.tipo == 'opSuma':
                        if operador.valor == '+': self.codigo_func_actual.append("    faddp st(1), st(0)")
                        elif operador.valor == '-': self.codigo_func_actual.append("    fsubp st(1), st(0)")
                    elif operador.tipo == 'opMul':
                        if operador.valor == '*': self.codigo_func_actual.append("    fmulp st(1), st(0)")
                        elif operador.valor == '/': self.codigo_func_actual.append("    fdivp st(1), st(0)")
                    return 'float'
                else:
                    self.codigo_func_actual.append("    fcomip st(0), st(1)")
                    self.codigo_func_actual.append("    fstp st(0)")

            # --- Lógica de Comparación (Común para Int y Float) ---
            if es_comparacion:
                es_float = (tipo_izq == 'float' or tipo_der == 'float')
                
                if es_float:
                    self.codigo_func_actual.append("    fnstsw ax")
                    self.codigo_func_actual.append("    sahf")
                
                self.codigo_func_actual.append("    mov eax, 0")
                
                if operador.valor == '>':
                    self.codigo_func_actual.append("    seta al" if es_float else "    setg al")
                elif operador.valor == '<':
                    self.codigo_func_actual.append("    setb al" if es_float else "    setl al")
                elif operador.valor == '>=':
                    self.codigo_func_actual.append("    setae al" if es_float else "    setge al")
                elif operador.valor == '<=':
                    self.codigo_func_actual.append("    setbe al" if es_float else "    setle al")
                elif operador.valor == '==': 
                    self.codigo_func_actual.append("    sete al")
                elif operador.valor == '!=': 
                    self.codigo_func_actual.append("    setne al")
                
                return 'int'

        # R43: ( <Expresion> )
        if len(nodo.hijos) == 3 and nodo.hijos[0].tipo == '(':
            return self.visitar(nodo.hijos[1], **kwargs) 

        # R44, R45: Operadores unarios
        if len(nodo.hijos) == 2: 
            tipo_res = self.visitar(nodo.hijos[1], **kwargs) 
            operador = nodo.hijos[0]
            if operador.tipo == 'opSuma' and operador.valor == '-':
                if tipo_res == 'float':
                    self.codigo_func_actual.append("    fchs")
                else:
                    self.codigo_func_actual.append("    neg eax")
            elif operador.tipo == 'opNot':
                if tipo_res == 'float':
                    self.codigo_func_actual.append("    fldz")
                    self.codigo_func_actual.append("    fcomip st(0), st(1)")
                    self.codigo_func_actual.append("    fstp st(0)")
                    self.codigo_func_actual.append("    fnstsw ax")
                    self.codigo_func_actual.append("    sahf")
                else:
                    self.codigo_func_actual.append("    cmp eax, 0")
                self.codigo_func_actual.append("    mov eax, 0")
                self.codigo_func_actual.append("    setz al")
            return tipo_res
            
        return 'int' 

    # --- VISITANTE Termino (¡CORREGIDO!) ---
    def visitar_Termino(self, nodo, **kwargs):
        hijo = nodo.hijos[0]
        
        if hijo.tipo == 'identificador':
            nombre_var = hijo.valor
            info_var = self.mapa_variables_locales.get(nombre_var)
            if not info_var: info_var = self.mapa_variables_globales.get(nombre_var)
            if not info_var:
                print(f"Error: Variable '{nombre_var}' no encontrada.")
                return 'int'
            
            # --- CORRECCIÓN A2023: Añadir DWORD/QWORD PTR ---
            if info_var['tipo'] == 'float':
                self.codigo_func_actual.append(f"    fld DWORD PTR {info_var['dir']}  ; Cargar float {nombre_var} a st(0)")
                return 'float'
            else:
                self.codigo_func_actual.append(f"    mov eax, {info_var['dir']}  ; Cargar int {nombre_var}")
                return 'int'
        
        elif hijo.tipo == 'entero':
            valor = hijo.valor
            self.codigo_func_actual.append(f"    mov eax, {valor}")
            return 'int'
        
        elif hijo.tipo == 'real':
            etiqueta_real = self.obtener_o_crear_real(hijo.valor)
            self.codigo_func_actual.append(f"    fld DWORD PTR [{etiqueta_real}]  ; Cargar float {hijo.valor} a st(0)")
            return 'float'

        elif hijo.tipo == 'LlamadaFunc':
            # TODO: Necesitamos saber el tipo de retorno de la función
            self.visitar(hijo, **kwargs)
            return 'int' 
        
        return 'int'

    # --- VISITANTES DE LLAMADA A FUNCIÓN (ACTUALIZADO) ---
    def visitar_LlamadaFunc(self, nodo, **kwargs):
        nombre_func = nodo.hijos[0].valor
        argumentos_nodo = nodo.hijos[2] 

        if nombre_func == "print":
            if not argumentos_nodo.hijos: return
            tipo_arg = self.visitar(argumentos_nodo.hijos[0], **kwargs) 
            
            if tipo_arg == 'float':
                # --- CORRECCIÓN A2023: Añadir DWORD/QWORD PTR ---
                self.codigo_func_actual.append("    sub esp, 8")
                self.codigo_func_actual.append("    fstp QWORD PTR [esp] ; Guardar st(0) como double en pila")
                etiqueta_formato = self.obtener_o_crear_cadena("formato_float_nl")
                self.codigo_func_actual.append(f"    push offset {etiqueta_formato}")
                self.codigo_func_actual.append("    call printf")
                self.codigo_func_actual.append("    add esp, 12")
            else:
                self.codigo_func_actual.append("    push eax")
                etiqueta_formato = self.obtener_o_crear_cadena("formato_int_nl")
                self.codigo_func_actual.append(f"    push offset {etiqueta_formato}")
                self.codigo_func_actual.append("    call printf")
                self.codigo_func_actual.append("    add esp, 8")
            
        else:
            lista_nodos_argumentos = self.obtener_lista_argumentos(argumentos_nodo)
            num_argumentos = len(lista_nodos_argumentos)
            
            for arg_nodo in reversed(lista_nodos_argumentos):
                tipo_arg = self.visitar(arg_nodo, **kwargs) 
                if tipo_arg == 'float':
                    # --- CORRECCIÓN A2023: Añadir DWORD/QWORD PTR ---
                    self.codigo_func_actual.append("    sub esp, 4")
                    self.codigo_func_actual.append("    fstp DWORD PTR [esp]")
                else:
                    self.codigo_func_actual.append("    push eax")
            
            self.codigo_func_actual.append(f"    call _{nombre_func}")
            
            if num_argumentos > 0:
                bytes_a_limpiar = num_argumentos * 4
                self.codigo_func_actual.append(f"    add esp, {bytes_a_limpiar}")

    def obtener_lista_argumentos(self, argumentos_nodo):
        argumentos = []
        if argumentos_nodo.hijos:
            argumentos.append(argumentos_nodo.hijos[0]) 
            self._visitar_ListaArgumentos_recursivo(argumentos_nodo.hijos[1], argumentos)
        return argumentos

    def _visitar_ListaArgumentos_recursivo(self, lista_args_nodo, argumentos):
        if lista_args_nodo.hijos:
            argumentos.append(lista_args_nodo.hijos[1]) 
            self._visitar_ListaArgumentos_recursivo(lista_args_nodo.hijos[2], argumentos)

    # --- VISITANTES "CONTENEDORES" Y "PASIVOS" ---
    
    def visitar_Sentencias(self, nodo, **kwargs):
        if not nodo.hijos: return
        self.visitar(nodo.hijos[0], **kwargs)
        self.visitar(nodo.hijos[1], **kwargs)
        
    def visitar_Bloque(self, nodo, **kwargs):
        if len(nodo.hijos) > 1:
            self.visitar(nodo.hijos[1], **kwargs) 
            
    def visitar_SentenciaBloque(self, nodo, **kwargs):
        if nodo.hijos:
            self.visitar(nodo.hijos[0], **kwargs)

    def visitar_Otro(self, nodo, **kwargs):
        if nodo.hijos:
            self.visitar(nodo.hijos[1], **kwargs)
        pass

    def visitar_Argumentos(self, nodo, **kwargs): pass
    def visitar_ListaArgumentos(self, nodo, **kwargs): pass