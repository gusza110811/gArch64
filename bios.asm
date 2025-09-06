const console xFE00_0000
const counter xEFFC

INTR x10 print

JMP x0
label print
    ; To preserve state
    PUSHA
    PUSHX
    PUSHY

    ; Get source
    STA counter

    ; initialize
    LDAI x10
    STAR console

    CALL printloop

    ; Revert to previous state
    POPY
    POPX
    POPA
RET

label printloop
    ; print
    LDX counter
    LDVR
    STAR console

    ; increment
    LDYI 1
    ADD
    STA counter

    ; check loop condition
    LDX counter
    LDVR

    JNZ printloop
    STAR console
RET