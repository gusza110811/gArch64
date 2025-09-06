const console xFE00_0000
const counter xEFFC

INTR x10 print
INTR x12 input

JMP x0
label input
    PUSHR
    STA counter ; register A is the target to save at
    LDXI x12    ; listen command
    STXR console

    label listen_loop
        LDYR console
        LDXI x0A

        JEQ end_loop
        MVYA

        JZ listen_loop
        LDX counter
        LDYI 1
        STVR
        ADD
        STA counter
        JMP listen_loop

    label end_loop
    LDXI x13
    STXR console
    POPR
RET

label print
    ; To preserve state
    PUSHR

    ; Get source
    STA counter

    ; initialize
    LDAI x10
    STAR console

    CALL printloop

    ; Revert to previous state
    POPR
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