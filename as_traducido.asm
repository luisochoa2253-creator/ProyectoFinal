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
    _a DWORD 0

.code
start:
    call _main

    ; --- Rutina de Salida ---
    ; El valor de retorno de _main está en EAX
    push  eax            ; <-- ¡ESTE ES EL CAMBIO!
    call  ExitProcess

_suma:
    push ebp
    mov ebp, esp
    mov eax, [ebp+12]  ; Cargar int b
    push eax  ; Guardar int (der) en pila
    mov eax, [ebp+8]  ; Cargar int a
    pop ebx      ; Recuperar int (der) a EBX
    add eax, ebx
    ; --- return ---
    mov esp, ebp
    pop ebp
    ret
    ; --- Epilogo (fallback) de _suma ---
    mov esp, ebp
    pop ebp
    ret

_main:
    push ebp
    mov ebp, esp
    sub esp, 12  ; Reservar espacio para locales
    mov eax, [ebp-8]  ; Cargar int b
    push eax  ; Guardar int (der) en pila
    fld DWORD PTR [ebp-4]  ; Cargar float a a st(0)
    fild DWORD PTR [esp]
    add esp, 4
    faddp st(1), st(0)
    fstp DWORD PTR [ebp-12]  ; c = st(0) (float)
    mov eax, 9
    push eax
    mov eax, 8
    push eax
    call _suma
    add esp, 8
    push eax
    fild DWORD PTR [esp] ; Cargar int de pila a st(0)
    add esp, 4
    fstp DWORD PTR [ebp-12]  ; c = st(0) (float)
    fld DWORD PTR [ebp-12]  ; Cargar float c a st(0)
    ; --- return ---
    mov esp, ebp
    pop ebp
    ret
    ; --- Epilogo (fallback) de _main ---
    mov esp, ebp
    pop ebp
    ret

END start