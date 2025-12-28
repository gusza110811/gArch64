const hexconv_counter x1F0
const hexconv_output x1F4
const tmp x1F8
const print x10
const input x12

main:
    mov a, prompt
    int [print]

    mov a, input_buf
    int [input]
    mov x, [input_buf]
    mov y, 'r
    jeq [read]
    mov y, 'w
    jeq [write]

jmp [main]

read:
    mov a, input_buf1
    call [hexconv]

    movd a, [hexconv_output]
    int [print]
    mov a, newline
    int [print]
jmp [main]

write:
    mov a, input_buf1
    call [hexconv]

    movd x, [hexconv_output]
    mov y, x1FF
    sub 
    jc [show_protected]
    mov y, x10000
    add 
    jc [show_protected]

    mov a, data_prompt
    int [print]

    movd a, [hexconv_output]
    int [input]
jmp [main]

show_err:
    mov a, error_message
    int [print]
ret 

show_protected:
    mov a, protected_error_message
    int [print]
jmp [main]

; A is the address to the beginning of the hexadecimal string
; return 0 if successful, return 1 if invalid character is detected
hexconv:
    pushr 
    movd [hexconv_counter], a
    mov x, 0
    movd [hexconv_output], x

hexconv_loop:
    movd x, [hexconv_counter]
    ldv 
    jz [hexconv_end]
    mov x, a

    mov y, x30
    sub 
    jc [hexconv_err]

    mov y, x3A
    sub 
    jc [hexconv_num]

    mov y, x47
    sub 
    jc [hexconv_upper]

    jmp [hexconv_err]

hexconv_inc:
    movd x, [hexconv_counter]
    mov y, 1
    add 
    movd [hexconv_counter], a

    jmp [hexconv_loop]

hexconv_num:
    mov y, x30
    sub 
    movd [tmp], a

    movd x, [hexconv_output]
    mov y, 4
    shl 
    mov x, a
    movd y, [tmp]
    or 
    movd [hexconv_output], a
jmp [hexconv_inc]

hexconv_upper:
    mov y, x37
    sub 
    movd [tmp], a

    movd x, [hexconv_output]
    mov y, 4
    shl 
    mov x, a
    movd y, [tmp]
    or 
    movd [hexconv_output], a
jmp [hexconv_inc]

hexconv_err:
    popr 
    mov a, 1
    ret 

hexconv_end:
    popr 
    mov a, 0
    ret 


hex_target:
    .ascii Fa
    .zero

prompt:
    .ascii >
    .zero

data_prompt:
    .ascii text>
    .zero

newline:
    .ascii \n
    .zero

error_message:
    .ascii Bad Hex\n
    .zero

protected_error_message:
    .ascii Protected memory range\n
    .zero

input_buf:
.zero
input_buf1: