const print x10

main:
    mov a, test
    jmpv 
halt 

test:
    mov a, text
    int [print]
halt 

text:
    .ascii Indirect Jump!\n\0