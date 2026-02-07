const console xFE00_0000

main:
    mov a, prompt
    int x10 ; prompt user

    mov a, buffer
    int x12 ; read

    mov x, [buffer]

    ; check input
    cmp x, 'r
    jz [read_mode]
    cmp x, 'w
    jz [write_mode]

jmp main

read_mode:
    call [get_sector]
    int [x13]
    mov a, buffer
    int [x14]
    int [x10]
jmp [main]

write_mode:
    call get_sector
    mov x, a
    mov y, 0
    cmp x, y
    jz write_error

    int 0x13
    mov a, dataprompt ; ask for data

    int 0x10
    mov a, buffer
    int 0x12
    int 0x15
jmp main

write_error:
    mov a, writeerror
    int [x10]

jmp main

get_sector:
    mov x, [buffer1]
    mov y, x30
    sub 
ret 

prompt:
    .ascii \ncommand>\0
dataprompt:
    .ascii data>\0
writeerror:
    .literal x1b
    .ascii [31mCan't write to sector 0
    .literal x1b
    .ascii [0m\n\0

buffer:
.zero 1
buffer1:

; because the output binary is a disk image
zeroes:
    ; pad boot sector
    .org 512
    ; a few extra sector
    .org 5120