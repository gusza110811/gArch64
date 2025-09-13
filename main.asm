const newline x0A
const console xFE00_0000

; Read disk data
mov $a, %starttext
int %x14

main:
    mov $a, %starttext
    int %x10
    mov $a, %infotext
    int %x10

    mov $a, %prompt
    int %x10

    mov $a, %text
    int %x12

    mov $a, %text
    int %x15

halt

infotext:
    .ascii \nType something to print on next run\n\0

starttext:
    .zero 256

prompt:
    .ascii Message>\0

text: