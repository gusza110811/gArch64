const newline x0A
const console xFE00_0000
const disk_com xFE00_0001
const disk_data xFE00_0002
const disk_stat xFE00_0003

; Read disk data
diskload:
    mov $a, %x20
    mov disk_com, $a
    mov $x, %starttext
    mov $y, %1

    diskloop:
        mov $a, disk_data
        stvr
        add
        mov $x, $a
        mov $a, disk_stat
        jnz diskloop

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
    .zero 256

prompt:
    .ascii input>\0

; 512 byte final binary size funny number go brrr
text:
    .zero 141