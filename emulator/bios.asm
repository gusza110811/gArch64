const offset 0xFFFF_0000

const console 0xFE00_0000
const counter 0xFFFF_0FFC
const disk_com 0xFE00_0001
const disk_data 0xFE00_0002
const disk_stat 0xFE00_0003

; setup the stack
mov a, 0xFFFF_FFFF
setst

; setup the IVT
mov a, 0xFFFF_E000
setiv

; define the functions
intr 0x10, print
intr 0x12, input

intr 0x13, disk_set_sector
intr 0x14, disk_read
intr 0x15, disk_write

; define the fault handlers
intr 0x100, intfault
intr 0x101, opcodefault
intr 0x102, pagefault
intr 0x103, intoverflow

; load the program in boot sector
mov a, 0
call disk_read

ajmp [0x0]

;-----------------------;
; End of the BIOS's job ;
;-----------------------;

; A is the sector number
disk_set_sector:
    pushr 
    mov x, x10
    mov [disk_com], x
    mov x, a
    mov [disk_data], x
    shrb 
    mov x, a
    mov [disk_data], x
    shrb 
    mov x, a
    mov [disk_data], x
    shrb 
    mov x, a
    mov [disk_data], x
    mov x, [disk_stat]
    mov y, 0x31
    cmp x, y
    jz [bad_sector]
    popr 
    mov a, 0
    ret 

ret 

bad_sector:
    popr 
    mov a, 1
ret 

; A is the source address in memory to read from
disk_write:
    pushr 
    mov x, a
    mov a, 0x21
    mov [disk_com], a
    mov y, 1

    writeloop:
        ldv 
        mov [disk_data], a
        add 
        mov x, a
        mov a, [disk_stat]
        cmp a, 0
        jnz writeloop
    popr 
ret 

; A is the target address in memory to save to
disk_read:
    pushr 
    mov x, a
    mov a, 0x20
    mov [disk_com], a
    mov y, 1

    readloop:
        mov a, [disk_data]
        stv 
        add 
        mov x, a
        mov a, [disk_stat]
        cmp a, 0
        jnz readloop
    popr 
ret 

; trailing newline not included
input:
    pushr 
    movd [counter], a ; save target buffer pointer


listen_loop:
    mov y, [console] ; read character into Y

    ; check for backspace (0x08)
    cmp y, 0x08
    jz handle_backspace

    ; check for newline
    cmp y, 0x0A
    jz end_loop

    ; store character
    cmp y, 0
    jz listen_loop ; ignore zero

    mov a, y
    movd x, [counter]
    stv
    mov y, 1
    add 
    movd [counter], a
    jmp listen_loop

handle_backspace:
    ; only backspace if counter > start
    movd a, [counter]
    cmp a, 0
    jz listen_loop ; if already at start, skip

    mov x, a
    mov y, 1
    sub 
    movd [counter], a ; decrement counter

    jmp listen_loop

end_loop:
    movd x, [counter]
    mov a, 0
    stv 
    popr 
ret 

print:
    pushr 

    movd [counter], a

    call printloop

    popr 
ret 

printloop:
    movd x, [counter]
    ldv 
    mov [console], a ; print character


    mov y, 1
    add 
    movd [counter], a

    ldv 
    cmp a, 0
    jnz printloop
    mov [console], a
ret 

opcodefault:
    mov a, offset + opcodefault_text
    call print
ret 

pagefault:
    mov a, offset + pagefault_text
    call print
ret 

intfault:
    mov a, offset + intfault_text
    call print
ret 

intoverflow:
    mov a, offset + intoverflow_text
    call print
ret 

opcodefault_text:
    .ascii OPCODEFAULT\0

pagefault_text:
    .ascii PAGEFAULT\0

intfault_text:
    .ascii INTFAULT\0

intoverflow_text:
    .ascii IVTOVERFLOW\0
