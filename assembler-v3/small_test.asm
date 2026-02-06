const print = 0x10

func main {
    mov a, text ; LDAI text
    int print   ; INT print

    ; implicit HALT (because this function is main)
}

data text {
    .asciiz "Hello"
}