const console xFE00_0000
const counter xEFFC

INTR x10 print
INTR x12 input

JMP x0
label input
    PUSHR
    STA counter         ; save target buffer pointer

label listen_loop
    LDYR console        ; read character into Y

    ; check for backspace (0x08)
    LDXI x08
    JEQ handle_backspace

    ; check for newline
    LDXI x0A
    JEQ end_loop

    ; store character
    MVYA
    JZ listen_loop      ; ignore zero
    LDX counter
    LDYI 1
    STVR
    ADD
    STA counter
    JMP listen_loop

label handle_backspace
    ; only backspace if counter > start
    LDA counter
    JZ listen_loop      ; if already at start, skip
    MVAX
    LDYI x1             ; check if counter > 1
    SUB

    STA counter         ; decrement counter
    JMP listen_loop

label end_loop
    LDX counter
    LDAI x00
    STVR

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
