const print = 0x10 ; a bios-defined software interupt routine
const input = 0x12
const console = 0xfe00_0000 ; raw console device

data buffer {
    .zero 0
}

func main {
    mov a, buffer
    mov x, '\n'

    call loop
}

func loop {
    int input
    int print
    mov [b console], x

    jmp loop
}
