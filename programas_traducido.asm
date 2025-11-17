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