const newline x0A
const console xFE00_0000

; the label isnt necessary but just for source code readability
label main
    LDAI starttext
    INT x10

; Echo loop
label loop
    LDAI prompt
    INT x10

    LDAI text
    INT x12
    INT x10

    LDAI x10
    STAR console ; print command
    LDAI newline
    STAR console ; send newline
    LDAI x00
    STAR console ; null (stop printing)

JMP loop

label starttext
.ascii Welcome to the very interesting program that echoes back whatever you just typed\n\0

label prompt
.ascii input>\0

label text
; allocate 83 bytes for user's input
.blank 83