const hexconv_counter xAA10
const hexconv_output xAA11
const tmp xAA12
const print x10
const input x12
const input_buf x0000_1000

page 1 ; allocate 0000_1000-0000_1FFF

main:
    mov $a, %input_buf
    int input
    call hexconv
    bnz show_err
    halt
jmp main

show_err:
    mov $a, %error_message
    int print
ret

; A is the address to the beginning of the hexadecimal string
; return 0 if successful, return 1 if invalid character is detected
hexconv:
    pushr
    mov *hexconv_counter, $a

hexconv_loop:
    mov $x, *hexconv_counter
    ldvr
    jz hexconv_end
    mov $x, $a

    mov $y, %x30
    sub
    jc hexconv_err

    mov $y, %x3A
    sub
    jc hexconv_num

    mov $y, %x47
    sub
    jc hexconv_upper

    jmp hexconv_err

hexconv_inc:
    mov $x, *hexconv_counter
    mov $y, %1
    add
    mov *hexconv_counter, $a

    jmp hexconv_loop

hexconv_num:
    mov $y, %x30
    sub
    mov *tmp, $a

    mov $x, *hexconv_output
    mov $y, %4
    shl
    mov $x, $a
    mov $y, *tmp
    or
    mov *hexconv_output, $a
jmp hexconv_inc

hexconv_upper:
    mov $y, %x37
    sub
    mov *tmp, $a

    mov $x, *hexconv_output
    mov $y, %4
    shl
    mov $x, $a
    mov $y, *tmp
    or
    mov *hexconv_output, $a
jmp hexconv_inc

hexconv_err:
    popr
    mov $a, %1
    ret

hexconv_end:
    popr
    mov $a, %0
    ret


hex_target:
    .ascii Fa
    .zero

error_message:
    .ascii Bad Hex
    .zero