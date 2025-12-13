const console xFE00_0000
const counter xFFFF_0FFC
const disk_com xFE00_0001
const disk_data xFE00_0002
const disk_stat xFE00_0003

intr %x10, print
intr %x12, input

intr %x13, disk_set_sector
intr %x14, disk_read
intr %x15, disk_write

; allocate the 0 page
page 0

; load the program in boot sector
call disk_read

ajmp x0

; A is the sector number
disk_set_sector:
    pushr
    mov $x, %x10
    mov disk_com, $x
    mov $x, $a
    mov disk_data, $x
    shrb
    mov $x, $a
    mov disk_data, $x
    shrb
    mov $x, $a
    mov disk_data, $x
    shrb
    mov $x, $a
    mov disk_data, $x
    mov $x, disk_stat
    mov $y, %x31
    jeq bad_sector
    popr
    mov $a, %0
    ret

ret

bad_sector:
    mov $a, %bad_sector_error
    int x10
    popr
    mov $a, %1
ret

; A is the source address in memory to read from
disk_write:
    pushr
    mov $x, $a
    mov $a, %x21
    mov disk_com, $a
    mov $y, %1

    writeloop:
        ldvr
        mov disk_data, $a
        add
        mov $x, $a
        mov $a, disk_stat
        jnz writeloop
    popr
ret

; A is the target address in memory to save to
disk_read:
    pushr
    mov $x, $a
    mov $a, %x20
    mov disk_com, $a
    mov $y, %1

    readloop:
        mov $a, disk_data
        stvr
        add
        mov $x, $a
        mov $a, disk_stat
        jnz readloop
    popr
ret

; trailing newline not included
input:
    pushr
    movd counter, $a        ; save target buffer pointer

listen_loop:
    mov $y, console         ; read character into Y

    ; check for backspace (0x08)
    mov $x, %x08
    jeq handle_backspace

    ; check for newline
    mov $x, %x0A
    jeq end_loop

    ; store character
    mov $a, $y
    jz listen_loop          ; ignore zero
    movd $x, counter
    mov $y, %1
    stvr
    add
    movd counter, $a
    jmp listen_loop

handle_backspace:
    ; only backspace if counter > start
    movd $a, counter
    jz listen_loop          ; if already at start, skip
    mov $x, $a
    mov $y, %1
    sub
    movd counter, $a         ; decrement counter
    jmp listen_loop

end_loop:
    movd $x, counter
    mov $a, %0
    stvr
    popr
ret

print:
    pushr

    movd counter, $a

    call printloop

    popr
ret

printloop:
    movd $x, counter
    ldvr
    mov console, $a         ; print character

    mov $y, %1
    add
    movd counter, $a

    ldvr
    jnz printloop
    mov console, $a
ret

bad_sector_error:
    .ascii BAD SECTOR
    .zero