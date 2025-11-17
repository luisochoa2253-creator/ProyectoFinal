Compilador C-Simple a x86 ASM
Este es un proyecto de compilador completo, escrito en Python, que traduce un lenguaje de alto nivel (similar a C) a código ensamblador x86 de 32 bits para Windows (MASM).

El compilador recorre todas las fases clásicas:

Análisis Léxico y Sintáctico (LR) para validar la gramática.

Construcción de un Árbol de Sintaxis Abstracta (AST).

Análisis Semántico para la validación de tipos, funciones y variables.

Generación de Código (Backend) que produce un archivo .asm funcional.

Generación de Imagen del AST para depuración visual.

🚀 Características del Lenguaje
El lenguaje que este compilador traduce soporta:

Variables Globales y Locales de tipo int y float.

Funciones con parámetros y sentencias return.

Lógica de Control con bucles while y condicionales if-else.

Operaciones Aritméticas (+, -, *, /) para enteros y flotantes (usando la FPU).

Operaciones Relacionales (>, <, ==, !=, etc.) en enteros y flotantes.

Función print() integrada (mapeada a printf de C) para mostrar enteros y flotantes en la consola.

📂 Estructura del Proyecto
El proyecto está modularizado en varios archivos de Python, cada uno con una responsabilidad específica.

/Traductor
│
├── 📜 main.py               # (Paso 0) El orquestador principal que ejecuta todos los pasos.
├── 📜 nodo.py               # Define la clase 'Nodo' para el AST.
│
├── 📜 analizador_lr.py      # (Paso 1) Verificador sintáctico rápido (True/False).
├── 📜 analizador_lr_arbol.py  # (Paso 2) Constructor del AST.
├── 📜 arbol_sem_lr.py     # (Paso 3 y 4) Analizador semántico y generador de imagen.
├── 📜 generador_asm.py      # (Paso 5) Generador de código ensamblador (x86).
│
├── 📄 compilador.lr         # (Gramática)
├── 📄 compilador.csv        # (Gramática) Tabla de análisis sintáctico.
├── 📄 compilador.inf        # (Gramática) Reglas de la gramática.
│
├── 📝 programa.txt          # (Entrada) Código fuente de ejemplo.
│
├── 🖥️ programa_traducido.asm  # (Salida 1) El código ensamblador generado.
├── 🖼️ programa_traducido.png  # (Salida 2) La imagen del AST.
└── 🚀 programa_traducido.exe  # (Salida Final) El ejecutable compilado.
📋 Requisitos
Para ejecutar este proyecto, necesitas dos conjuntos de herramientas.

1. Librerías de Python
Necesitarás las siguientes librerías, que puedes instalar con pip:

Bash

pip install pandas
pip install matplotlib
pip install networkx
pip install pydot
2. Herramientas de Compilación de Windows (MASM)
El compilador genera código .asm, pero para convertirlo en un .exe, necesitas las herramientas de ensamblado y enlace de Microsoft (MASM).

Descarga e instala las "Build Tools for Visual Studio" (Herramientas de compilación de VS).

Durante la instalación, asegúrate de seleccionar la carga de trabajo "Desarrollo para el escritorio con C++".

🛠️ Instrucciones de Uso
El proceso se divide en 3 pasos:

Paso 1: Escribir el Código Fuente
Crea un archivo de texto (ej. prueba.txt) con el código de tu lenguaje.
Paso 2: Compilar a .asm (Usando Python)
Ejecuta el main.py para generar el archivo ensamblador y la imagen del árbol.
¡Claro! Aquí tienes un archivo README.md detallado que documenta todo el proyecto que hemos construido, desde la estructura de archivos hasta cómo compilar el .exe final.

Puedes copiar este contenido, guardarlo en un archivo llamado README.md en la raíz de tu proyecto, y te servirá como una excelente documentación.

Compilador C-Simple a x86 ASM
Este es un proyecto de compilador completo, escrito en Python, que traduce un lenguaje de alto nivel (similar a C) a código ensamblador x86 de 32 bits para Windows (MASM).

El compilador recorre todas las fases clásicas:

Análisis Léxico y Sintáctico (LR) para validar la gramática.

Construcción de un Árbol de Sintaxis Abstracta (AST).

Análisis Semántico para la validación de tipos, funciones y variables.

Generación de Código (Backend) que produce un archivo .asm funcional.

Generación de Imagen del AST para depuración visual.

🚀 Características del Lenguaje
El lenguaje que este compilador traduce soporta:

Variables Globales y Locales de tipo int y float.

Funciones con parámetros y sentencias return.

Lógica de Control con bucles while y condicionales if-else.

Operaciones Aritméticas (+, -, *, /) para enteros y flotantes (usando la FPU).

Operaciones Relacionales (>, <, ==, !=, etc.) en enteros y flotantes.

Función print() integrada (mapeada a printf de C) para mostrar enteros y flotantes en la consola.

📂 Estructura del Proyecto
El proyecto está modularizado en varios archivos de Python, cada uno con una responsabilidad específica.

/Traductor
│
├── 📜 main.py               # (Paso 0) El orquestador principal que ejecuta todos los pasos.
├── 📜 nodo.py               # Define la clase 'Nodo' para el AST.
│
├── 📜 analizador_lr.py      # (Paso 1) Verificador sintáctico rápido (True/False).
├── 📜 analizador_lr_arbol.py  # (Paso 2) Constructor del AST.
├── 📜 arbol_sem_lr.py     # (Paso 3 y 4) Analizador semántico y generador de imagen.
├── 📜 generador_asm.py      # (Paso 5) Generador de código ensamblador (x86).
│
├── 📄 compilador.lr         # (Gramática)
├── 📄 compilador.csv        # (Gramática) Tabla de análisis sintáctico.
├── 📄 compilador.inf        # (Gramática) Reglas de la gramática.
│
├── 📝 programa.txt          # (Entrada) Código fuente de ejemplo.
│
├── 🖥️ programa_traducido.asm  # (Salida 1) El código ensamblador generado.
├── 🖼️ programa_traducido.png  # (Salida 2) La imagen del AST.
└── 🚀 programa_traducido.exe  # (Salida Final) El ejecutable compilado.
📋 Requisitos
Para ejecutar este proyecto, necesitas dos conjuntos de herramientas.

1. Librerías de Python
Necesitarás las siguientes librerías, que puedes instalar con pip:

Bash

pip install pandas
pip install matplotlib
pip install networkx
pip install pydot
2. Herramientas de Compilación de Windows (MASM)
El compilador genera código .asm, pero para convertirlo en un .exe, necesitas las herramientas de ensamblado y enlace de Microsoft (MASM).

Descarga e instala las "Build Tools for Visual Studio" (Herramientas de compilación de VS).

Durante la instalación, asegúrate de seleccionar la carga de trabajo "Desarrollo para el escritorio con C++".

Asegúrate de que los componentes "Herramientas de compilación de C++ de MSVC..." y un "SDK de Windows" estén seleccionados.

¡Importante! Para compilar, debes usar la terminal especial: "x86 Native Tools Command Prompt for VS" (Símbolo del sistema de herramientas nativas x86).

🛠️ Instrucciones de Uso
El proceso se divide en 3 pasos:

Paso 1: Escribir el Código Fuente
Crea un archivo de texto (ej. prueba.txt) con el código de tu lenguaje.

Ejemplo (prueba.txt):

C

int suma(int a, int b){
  return a + b;
}

void main() {
  int i;
  i = 10;
  
  while (i > 0) {
    if (i == 5) {
      print(99); // Imprime 99 cuando i es 5
    } else {
      print(i);
    }
    
    i = i - 1;
  }
  
  print(suma(5, 5)); // Debería imprimir 10
}
Paso 2: Compilar a .asm (Usando Python)
Ejecuta el main.py para generar el archivo ensamblador y la imagen del árbol.

Bash

python main.py
El script te pedirá el nombre de tu archivo de texto (prueba.txt). Si todo sale bien, generará:

prueba_traducido.asm

prueba_traducido_arbol.png

Paso 3: Ensamblar y Enlazar el .exe
Abre la terminal "x86 Native Tools Command Prompt for VS" y navega a la carpeta de tu proyecto.

Ejecuta los siguientes dos comandos:

1. Ensamblar (Crear .obj):

Bash

ml /c /Zd /Zi /Fo"prueba_traducido.obj" "prueba_traducido.asm"
2. Enlazar (Crear .exe): Este comando vincula tu código con las librerías C (ucrt.lib, vcruntime.lib) y las librerías de Windows (kernel32.lib) necesarias para printf y ExitProcess.

Bash

link /SUBSYSTEM:CONSOLE /ENTRY:start "prueba_traducido.obj" ucrt.lib vcruntime.lib kernel32.lib legacy_stdio_definitions.lib
Paso 4: ¡Ejecutar!
Si los pasos anteriores no dieron errores, ahora tendrás un .exe ejecutable.

Bash

programa_traducido.exe
<img width="473" height="332" alt="image" src="https://github.com/user-attachments/assets/445554e3-76c0-4be9-a001-37037af3f0ad" />

ejemplo 2:
programas.txt
void main() {
  int mi_variable;
  mi_variable = 10 * 2;
  while (mi_variable > 0) {
    mi_variable = mi_variable - 1;
  }
programas_traducido.asm
  .386
.model flat, C
option casemap:none
 ; --- Librerias a incluir ---
includelib msvcrt.lib
includelib kernel32.lib
 ; --- Prototipos ---
printf PROTO, :VARARG
ExitProcess PROTO stdcall, dwExitCode:DWORD

.data
    _S0 DB '%d', 0Ah, 0  ; <-- CAMBIO 1: Añadir cadena de formato

.code
start:
    call _main

    ; --- Rutina de Salida ---
    push  0            ; <-- CAMBIO 2: Devolver 0 (éxito)
    call  ExitProcess

_main:
    push ebp
    mov ebp, esp
    sub esp, 4  ; Reservar espacio para locales
    mov eax, 2
    push eax  ; Guardar int (der) en pila
    mov eax, 10
    pop ebx      ; Recuperar int (der) a EBX
    imul eax, ebx
    mov [ebp-4], eax  ; mi_variable = EAX
_L1:
    mov eax, 0
    push eax  ; Guardar int (der) en pila
    mov eax, [ebp-4]  ; Cargar int mi_variable
    pop ebx      ; Recuperar int (der) a EBX
    cmp eax, ebx
    mov eax, 0
    setg al
    cmp eax, 0
    je _L2

    ; --- CAMBIO 3: INICIA CÓDIGO DE PRINT AÑADIDO A MANO ---
    mov eax, [ebp-4]       ; 1. Cargar 'mi_variable' en EAX
    push eax               ; 2. Poner el valor en la pila para printf
    push offset _S0        ; 3. Poner la cadena de formato "%d\n"
    call printf            ; 4. Llamar a la función
    add esp, 8             ; 5. Limpiar la pila (2 push = 8 bytes)
    ; --- TERMINA CÓDIGO DE PRINT ---

    mov eax, 1
    push eax  ; Guardar int (der) en pila
    mov eax, [ebp-4]  ; Cargar int mi_variable
    pop ebx      ; Recuperar int (der) a EBX
    sub eax, ebx
    mov [ebp-4], eax  ; mi_variable = EAX
    jmp _L1
_L2:
    ; --- Epilogo (fallback) de _main ---
    mov esp, ebp
    pop ebp
    ret

END start
}
Resultado programas_traducido.exe
<img width="798" height="528" alt="Captura de pantalla 2025-11-16 191632" src="https://github.com/user-attachments/assets/10b19d75-324d-4c6c-9f22-78a11e9461fc" />

Asegúrate de que los componentes "Herramientas de compilación de C++ de MSVC..." y un "SDK de Windows" estén seleccionados.

¡Importante! Para compilar, debes usar la terminal especial: "x86 Native Tools Command Prompt for VS" (Símbolo del sistema de herramientas nativas x86).
