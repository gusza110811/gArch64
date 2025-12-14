const target x0000_0200
const target1 x0000_0204

main:
    mov $a, %xA5A5_ABAB
    movd target, $a
    movw target1, $a
halt