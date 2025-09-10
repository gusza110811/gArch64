const newline x0A
const console xFE00_0000

main:
    mov $a, %starttext
    int %x10

; Echo loop
loop:
    mov $a, %prompt
    int %x10

    mov $a, %text
    int %x12
    int %x10

    mov $a, %newline
    mov console, $a ; send newline

jmp loop

starttext:
    .ascii Welcome to the very interesting program that echoes back whatever you just typed\n\0

prompt:
    .ascii input>\0

; allocate 107 bytes for user's input
text:
    .zero 107
