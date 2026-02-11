const print = 0x10

; this is a data block
data text {
    .asciiz "Hello, World!\n"
}

; this is an anonymous data block
data {
    text1:  .asciiz "Beep "

    text2:  .asciiz "Boop\n"
}

; main is always put at the top when assembled
func main {
    mov a, text ; LDAI text
    int print   ; INT print

    call printd

    halt
}

func printd {
    mov a, text1
    int print

    mov a, text2
    int print

    ret
}
