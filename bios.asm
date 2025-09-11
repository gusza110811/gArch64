const console xFE00_0000
const counter xEFFC

intr %x10, print
intr %x12, input

jmp x0

input:
    pushr
    mov *counter, $a        ; save target buffer pointer

listen_loop:
    mov $y, console         ; read character into Y

    ; check for backspace (0x08)
    mov $x, %x08
    jeq handle_backspace

    ; check for newline
    mov $x, %x0A
    jeq end_loop

    ; store character
    mov $a, $y
    jz listen_loop          ; ignore zero
    mov $x, *counter
    mov $y, %1
    stvr
    add
    mov *counter, $a
    jmp listen_loop

handle_backspace:
    ; only backspace if counter > start
    mov $a, *counter
    jz listen_loop          ; if already at start, skip
    mov $x, $a
    mov $y, %1
    sub
    mov *counter, $a         ; decrement counter
    jmp listen_loop

end_loop:
    mov $x, *counter
    mov $a, %0
    stvr
    popr
ret

print:
    pushr

    mov *counter, $a

    call printloop

    popr
ret

printloop:
    mov $x, *counter
    ldvr
    mov console, $a         ; print character

    mov $y, %1
    add
    mov *counter, $a

    ldvr
    jnz printloop
    mov console, $a
ret
