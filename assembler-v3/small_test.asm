const print = 0x10

data text {
    .asciiz "Hello"
}

func main {
    mov a, text ; LDAI text
    int print   ; INT print

    jmp main

    ; implicit HALT (because this function is main)
}