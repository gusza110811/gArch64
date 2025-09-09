# ASSEMBLY DOCS

## Syntax
### Prefixes
| Prefix | Use |
| --- | --- |
| `X` | Hexadecimal number (dynamic length) |
| `B` | Decimal number (dynamic length) |
| `x` | Hexadecimal number (fixed length) |
| `b` | Binary number (fixed length) |
| `'` | Ascii character (4 or 8 bytes) |
| `"` | Ascii string of character (Cannot include space, as it marks the beginning of a new word) |

### Defining

| Command | Usage|
| --- | ---
| `CONST [name] [value]` | Define `name` as `value` |
| `LABEL [name]` | Define `name` as the byte address of the next command. Used for JMP/CALL etc |

Note that usage of defined `name` will be case-sensitive, but the `Command`s itself is not.

#### Misc
`.ascii [text]` -> Raw `text` encoded in ascii, can include space unlike `"` prefix

## BIOS service
The pre-loaded BIOS service program provides a few functions that would otherwise take lines of code

| Function | Usage | Description |
| --- | ---| --- |
| print [address] | Set register A to the address of the first character in your string then call INT 16 | print a string at ram [address] until null byte |
| input [address] | Set register A to the beginning address of where you want you input string to be at, then call INT 18 | Recors user's input to [address]

## Virtual Hardware Specification
MMIO mapped to FE00_0000 to FE00_00FF

The first one (FE00_0000) is always the serial console

### The Serial Console
| Command | use |
| --- | --- |
| write (`0x10`) | Begin outputting, stop when null (`0`) is sent |
| input (`0x12`)  |  Begin reading keyboard input into a buffer that can be loaded |
| stop_input (`0x13`) | Stop reading keyboard input |


## Instruction Definitions
These are case-insensitive
| Instruction | Usage |
| --- | ---|
| **Memory** |
| `LDA [addr]` | Load value at cache `addr` to register A |
| `LDX [addr]` | Load value at cache `addr` to register X |
| `LDY [addr]` | Load value at cache `addr` to register Y |
| `STA [addr]` | Store value in register A to cache `addr` |
| `STX [addr]` | Store value in register X to cache `addr` |
| `STY [addr]` | Store value in register Y to cache `addr` |
| `MOV [dest-addr source-addr]` | Copy value from cache `source-addr` to cache `dest-addr` |
| `LDV` | Use value in register X as (cache) memory address and copy value from there to register A |
| `STV` | Use value in register X as (cache) memory address and store value from register A to there |
| **Arithmetic** |
| `ADD` | Add register X and Y then save to register A |
| `SUB` | Subtract register X by Y and save to register A |
| `MUL` | Multiply register X and Y then save to register A |
| `DIV` | Floor Divide register X by Y and save to register A |
| `MOD` | Modulo X by Y and save to register A |
| **Bitwise Logic** |
| `AND` | Bitwise AND register X and Y and save to register A |
| `OR` | Bitwise OR register X and Y and save to register A |
| `XOR` | Bitwise XOR register X and Y and save to register A |
| `NOT` | Bitwise NOT register X and save to register A |
| **Flow Control** |
| `JMP [addr]` | Jump to `addr` |
| `JZ [addr]` | Jump to `addr` if register A is 0 |
| `JNZ [addr]` | Jump to `addr` if register A is not 0 |
| `JC [addr]` | Jump to `addr` if previous arithmetic resulted in overflow |
| `JNC [addr]` | Jump to `addr` if previous arithmetic did not result in overflow |
| `JEQ [addr]` | Jump to `addr` if register X is equal to register Y |
| `JNE [addr]` | Jump to `addr` if register X is not equal to register Y |
| **Subroutine** |
| `RET` | Return from subroutine |
| `CALL [addr]` | Branch to subroutine at `addr` |
| `BZ [addr]` | Branch to `addr` if register A is 0 |
| `BNZ [addr]` | Branch to `addr` if register A is not 0 |
| `BC [addr]` | Branch to `addr` if previous arithmetic resulted in overflow |
| `BNC [addr]` | Branch to `addr` if previous arithmetic did not result in overflow |
| `BEQ [addr]` | Branch to `addr` if register X is equal to register Y |
| `BNE [addr]` | Branch to `addr` if register X is not equal to register Y |
| **Load Immediate** |
| `LDAI [value]` | load `value` to register A |
| `LDXI [value]` | load `value` to register X |
| `LDYI [value]` | load `value` to register Y |
| **Register-Register Copy** |
| `MVAX` | Copy register A to register X |
| `MVAY` | Copy register A to register Y |
| `MVXA` | Copy register X to register A |
| `MVXY` | Copy register X to register Y |
| `MVYA` | Copy register Y to register A |
| `MVYX` | Copy register Y to register X |
| **Stack** |
| `PUSHA` | Push register A to stack |
| `POPA` | Pop from stack to register A |
| `PUSHX` | Push register X to stack |
| `POPX` | Pop from stack to register X |
| `PUSHY` | Push register Y to stack |
| `POPY` | Pop from stack to register Y |
| `PUSHR` | Push every registers to stack |
| `POPR` | Pop from stack to every registers |
| **Halt** |
| `HALT` | Stop Execution Immediately |

## Extended Instruction Definitions (x32 / x64)
| Instruction  | Usage |
|  --- | --- |
| **Interrupts** |
| `INT [ID]` | Raise interrupt of id [ID] |
| `INTR [ID] [addr]`| Register interrupt id [ID] to subroutine at [addr] |
| `LDAR [addr]` | Load value at ram `addr` to register A |
| `LDXR [addr]` | Load value at ram `addr` to register X |
| `LDYR [addr]` | Load value at ram `addr` to register Y |
| `STAR [addr]` | Store value in register A to ram `addr` |
| `STXR [addr]` | Store value in register X to ram `addr` |
| `STYR [addr]` | Store value in register Y to ram `addr` |
| `LDVR` | Use value in register X as (ram) memory address and copy value from there to register A |
| `STVR` | Use value in register X as (ram) memory address and store value from register A to there |
