const newline = "\n"
const console = 0xfe00_0000

main {
    mov a, newline
    mov [console], a
}
