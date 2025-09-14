const console xFE00_0000

main:
    mov $a, %prompt
    int %x10              ; prompt user

    mov $a, %buffer
    int %x12              ; read

    mov $y, buffer

    ; check input
    mov $x, %'r
    jeq read_mode
    mov $x, %'w
    jeq write_mode

jmp main

read_mode:
    call get_sector ; ask for sector
    int x13
    mov $a, %buffer
    int x14
    int x10
jmp main

write_mode:
    call get_sector ; ask for sector
    mov $x, $a
    mov $y, %0
    jeq write_error

    int x13
    mov $a, %dataprompt ; ask for data
    int x10
    mov $a, %buffer
    int x12
    int x15
jmp main

write_error:
    mov $a, %writeerror
    int x10

jmp main

get_sector:
    mov $a, %sectorprompt
    int x10
    mov $a, %buffer
    int x12

    mov $x, buffer
    mov $y, %x30
    sub
ret

prompt:
    .ascii \ncommand>\0
sectorprompt:
    .ascii sector>\0
dataprompt:
    .ascii data>\0
writeerror:
    .literal x1b
    .ascii [31mCan't write to sector 0
    .literal x1b
    .ascii [0m\n\0

buffer:

; because the output binary is a disk image
zeroes:
    ; pad boot sector
    .org 512
    ; a few extra sector
    .org 4608