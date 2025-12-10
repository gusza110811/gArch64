const hexconv_counter xAA10
const hexconv_output xAA11
const tmp xAA12

main:

hexconv:
    mov $x, *hexconv_counter
    ldvr
    jz end
    mov $x, $a
    mov $y, %x40
    sub
    jc num

    mov $x, *hexconv_counter
    mov $y, %1
    add
    mov *hexconv_counter, $a
    
    jmp hexconv

num:
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
    
    jmp hexconv

end:
    halt


hex_target:
    .ascii 10