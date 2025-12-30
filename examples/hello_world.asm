const print x10
main:
    mov a, data
    int print
halt 

data:
    .ascii Hello, World!\n
    .zero 1
