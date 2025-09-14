# ASSEMBLY DOCS

## Syntax

### Format
Each line is an instruction with its parameters. starts with the instruction's opcode, followed by
parameters separated by comma(`,`), which ends up looking like `OPCODE param1, [param2]`

### Prefix
| Prefix | Usage |
| --- | --- |
| `$` | Register |
| `%` | Immediate value |
| `*` | Cache Address |
| None | Ram Address

#### Register
For registers (`$[register]`) you use `a`, `x`, or `y` as register name, so `$a`, `$x`, or `$y` (case insensitive) coorespond to each registers respectively

#### Value prefixes
For every paramters, you can use another prefix just after the type prefix (`$`,`%`,`*`), this correspond
to the format of the value
| Prefix | Format|
| --- | --- |
| `x` | Hexadecimal |
| `b` | Binary |
| `o` | Octal |
| `'` | Ascii Character |

### Definition
#### Constants Definition
Use `const` keyword followed by the name, then its value (`const [name] [value]`)

#### Label Definition
Add `:` to the label's name (`[name]:`), it is recommended (but not required) to use indentation for the part that should
be inside

### Special Directives
These are helper commands that you more control over the output binary (case-insensitive)
| Command | Usage |
| --- | --- |
| `.literal [values]` | Add literal values |
| `.ascii [text]` | Add ASCII text |
| `.zero [n]` | Add [n] zeroes |

#### .ascii Escape Codes
Used within `.ascii` directive to add a normally non-printable and unusable characters within the string
| Escape code | Meaning |
| --- | --- |
| `\n` | Newline |
| `\r` | Carriage Return
| `\t` | Tab |
| `\0` | Null |
| `\\` | Backspace |

### Comment
Use `;`, can be anywhere

## System and Hardware specification
There is a BIOS program that runs on every execution. it sets up useful commands

These can be called through `int [id]` instruction with thr `id` as the command number in this table below
You set the A register to its parameter
| Command | Usage |
| --- | --- |
| `print` (`16`) | Print string that starts at ram address stored in A |
| `input` (`18`) | Get user input and save it to ram address stored in A |

You can also interact with the SerialConsole device directly by copying data from or to it. By default this device is mapped to memory address `0xFE00_0000`

Copy value to it for printing, Copy value from it to read user input buffer
## Opcodes
| OPCODE | Meaning/Usage |
| --- | --- |
| **HALT** |
| `halt` | End execution immediately |
| **Arithmetic** |
| `add` | Add X by Y and save to A |
| `sub` | Subtract X by Y and save to A |
| `mul` | Multiply X by Y and save to A |
| `div` | Divide X by Y and save to A |
| `mod` | Modulo X by Y and save to A |
| **Bitwise** |
| `and` | Bitwise AND X by Y then save to A |
| `or` | Bitwise OR X by Y then save to A |
| `xor` | Bitwise XOR X by Y then save to A |
| `not` | Bitwise NOT X by Y then save to A |
| `shr` | Shift X by Y to the right then save to A |
| `shl` | Shift X by Y to the left then save to A |
| `shrb` | Shift X by 8 to the right then save to A |
| `shlb` | Shift X by 8 to the left then save to A |
| **Control Flow** |
| `jmp [address/label]` | Jump to [address/label] |
| `jz [address/label]` | Jump to [address/label] if A = 0 |
| `jnz [address/label]` | Jump to [address/label] if A != 0 |
| `jc [address/label]` | Jump to [address/label] if previous operation resulted in overflow |
| `jnc [address/label]` | Jump to [address/label] if previous operation resulted in overflow |
| `jeq [address/label]` | Jump to [address/label] if X = Y |
| `jne [address/label]` | Jump to [address/label] if X = Y |
| **Function/Subroutine Control** |
| `ret` | Return from function |
| `call [address/label]` | Call function at [address/label] |
| `bz [address/label]` | Call function at [address/label] if A = 0 |
| `bnz [address/label]` | Call function at [address/label] if A != 0 |
| `bc [address/label]` | Call function at [address/label] if previous operation resulted in overflow |
| `bnc [address/label]` | Call function at [address/label] if previous operation resulted in overflow |
| `beq [address/label]` | Call function at [address/label] if X = Y |
| `bne [address/label]` | Call function at [address/label] if X = Y |
| **Move** |
| `mov [destination], [source]` | Copy from [source] to [destination]. Does not support direct cache/ram to ram/cache copy, only cache-cache and ram-ram. and does not support direct immediate store to ram/cache |
| **Variable Move/Store** |
| `ldv` | Load value from cache address stored in X to A |
| `stv` | Store value from A to cache address stored in X |
| `ldvr` | Load value from ram address stored in X to A |
| `stvr` | Store value from A to ram address stored in X |
| **Stack** |
| `push [register]` | Push [register] to stack |
| `pop [register]` | Pop from stack to [register] |
| `pushr` | Push every registers to stack (A register first) |
| `popr` | Pop from stack to every register (Y register first, return to state "saved" by `pushr`) |
| **Interrupts** |
| `int [int-id]` | Call interrupt assigned to [int-id] |
| `intr [int-id], [address]` | Assign [int-id] to function at [address] |
