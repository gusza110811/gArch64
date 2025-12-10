const print x10
const input x12
const buffer_address x0E00

main:
    mov $a, %prompt
    int print
    mov $a, %buffer_address
    int input
    int print
halt

prompt:
    .ascii >
    .zero 1