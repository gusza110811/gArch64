const mem1 x100
const mem2 x102

main:
    mov $a, %x80
    sxtw
    movw mem1, $a
    sxtd
    movd mem2, $a