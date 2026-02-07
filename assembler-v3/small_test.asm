const print = 0x10 ; bios-defined software interupt routine

data text {
    .asciiz "Hello, World!\n"
}

func main {
    mov a, text ; LDAI text
    int print   ; INT print
}