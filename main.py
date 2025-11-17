import os
import sys
import traceback

# --- Importaciones de los módulos separados ---
from nodo import Nodo
from analizador_lr import AnalizadorLR as VerificadorLR
from analizador_lr_arbol import AnalizadorLR as ConstructorAST, imprimir_arbol
from arbol_sem_lr import AnalizadorSemantico, generar_imagen_arbol
from generador_asm import GeneradorASM

def main():
    """
    Función principal que orquesta el proceso de compilación.
    """
    
    # Comprobar si los archivos de tablas existen
    archivos_requeridos = ["compilador.lr", "compilador.csv", "compilador.inf"]
    archivos_faltantes = [f for f in archivos_requeridos if not os.path.exists(f)]
    
    if archivos_faltantes:
        print(f"❌ Error Crítico: No se encontraron los siguientes archivos del compilador:")
        for f in archivos_faltantes:
            print(f"  - {f}")
        sys.exit(1)
        
    print("Cargando analizadores...")
    try: # <--- CORRECCIÓN DE SYNTAXERROR (FALTABA ':')
        # Inicializamos los dos analizadores sintácticos
        verificador = VerificadorLR("compilador.lr", "compilador.csv", "compilador.inf")
        constructor = ConstructorAST("compilador.lr", "compilador.csv", "compilador.inf")
        print("¡Analizadores listos! ✅")
    except Exception as e:
        print(f"❌ Error Crítico al cargar las tablas del compilador: {e}")
        sys.exit(1)

    while True:
        try:
            nombre_archivo = input("\n>>> Ingresa el nombre del archivo .txt a analizar (o escribe 'salir' para terminar): ")

            if nombre_archivo.lower() == 'salir':
                print("Cerrando el programa. ¡Hasta luego!")
                break
            
            if not nombre_archivo.endswith('.txt'):
                nombre_archivo_txt = nombre_archivo + '.txt'
            else:
                nombre_archivo_txt = nombre_archivo
            
            nombre_base = os.path.splitext(nombre_archivo_txt)[0]

            with open(nombre_archivo_txt, "r", encoding="utf-8") as f:
                codigo_del_archivo = f.read()
            
            if not codigo_del_archivo.strip():
                print(f"⚠️  El archivo '{nombre_archivo_txt}' está vacío.")
                continue

            # ================================================================
            # --- PASO 1: Verificación Sintáctica Rápida (analizador_lr.py) ---
            # ================================================================
            print(f"\n--- PASO 1: Iniciando Verificación Sintáctica (de analizador_lr.py) ---")
            es_sintaxis_valida = verificador.analizar(codigo_del_archivo)
            
            if not es_sintaxis_valida:
                print(f"\n❌ El código en '{nombre_archivo_txt}' falló la verificación sintáctica.")
                continue 

            print(f"\n✅ Verificación sintáctica exitosa.")

            # ================================================================
            # --- PASO 2: Construcción del Árbol (analizador_lr_arbol.py) ---
            # ================================================================
            print(f"\n--- PASO 2: Iniciando Construcción de Árbol (de analizador_lr_arbol.py) ---")
            arbol_sintactico = constructor.analizar(codigo_del_archivo)
            
            if not arbol_sintactico:
                print("\n❌ Error inesperado: La sintaxis fue válida pero no se pudo construir el árbol.")
                continue
                
            print("\n✅ Árbol de Sintaxis Abstracta (AST) generado:")
            imprimir_arbol(arbol_sintactico) 

            # ================================================================
            # --- PASO 3: Análisis Semántico (arbol_sem_lr.py) ---
            # ================================================================
            print(f"\n--- PASO 3: Iniciando Análisis Semántico (de arbol_sem_lr.py) ---")
            analizador_semantico = AnalizadorSemantico()
            es_semantica_valida = analizador_semantico.analizar(arbol_sintactico)
            
            # ================================================================
            # --- PASO 4: Generación de Imagen (de arbol_sem_lr.py) ---
            # ================================================================
            print(f"\n--- PASO 4: Generando Imagen del Árbol ---")
            nombre_imagen = f"{nombre_base}_arbol.png"
            generar_imagen_arbol(arbol_sintactico, 
                                 nombre_imagen, 
                                 semantico_valido=es_semantica_valida)
            
            # ================================================================
            # --- PASO 5: Generación de Código (generador_asm.py) ---
            # ================================================================
            if es_semantica_valida:
                print(f"\n🎉 ÉXITO: El código en '{nombre_archivo_txt}' es sintáctica y semánticamente válido.")
                print(f"\n--- PASO 5: Iniciando Generación de Código (Ensamblador) ---")
            
                generador = GeneradorASM()
                codigo_asm = generador.generar(arbol_sintactico) 
                
                print("\n--- CÓDIGO ENSAMBLADOR GENERADO ---")
                print(codigo_asm)
                print("-----------------------------------")
                
                # Guardar el código en un archivo .asm
                nombre_salida_asm = f"{nombre_base}_traducido.asm"
                with open(nombre_salida_asm, "w", encoding="utf-8") as f:
                    f.write(codigo_asm)
                print(f"✅ Código ensamblador guardado en '{nombre_salida_asm}'")
                print(f"   (Para compilarlo a .exe, necesitarás MASM: ml.exe y link.exe)")
            
            else:
                print(f"\n❌ FALLO: El código en '{nombre_archivo_txt}' es sintácticamente correcto, pero tiene errores semánticos.")

        except FileNotFoundError:
            print(f"❌ Error: No se pudo encontrar el archivo '{nombre_archivo_txt}'.")
        except Exception as e:
            print(f"Ocurrió un error inesperado en el flujo principal: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    main()