const print = 0x10 ; a bios-defined software interupt routine
const console = 0xfe00_0000 ; raw console device

data text {
    .asciiz "Hello, World!"
}

func main {
    mov a, text
    int print

    mov x, '\n'
    mov [b 0x200], x
    mov a, [b 0x200]
    mov [b console], a
    halt
}
