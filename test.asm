const console xFE00_0000

main:
    mov $A, %text
    INT %x10
halt:
    HALT

text:
    .ascii Hellooo\n\0