const console xFE00_0000

INTR 5 subroutine

INT 5
INT 5

HALT

label subroutine
    LDXI x10
    STXR console
    LDXI 'A
    STXR console
    STYR console
RET