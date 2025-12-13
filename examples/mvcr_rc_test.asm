const cachet x3333
const ramt x0000_0F00
const cachet1 x3334
const ramt1 x0000_0F01

main:
    mov $a, %xAB
    mov ramt, $a
    mov *cachet, ramt ; mvrc

    mov $a, %xBA
    mov *cachet1, $a
    mov ramt1, *cachet1
