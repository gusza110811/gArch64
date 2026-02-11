const print = 0x10 ; a bios-defined software interupt routine
const console = 0xfe00_0000 ; raw console device

data text {
    .asciiz "Hello, World!"
}

func main {
    mov a, text
    int print
    mov a, '\n'
    mov [console], a
    mov [5], [b 5]
    halt
}
