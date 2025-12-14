# ASSEMBLY DOCS

## The Command
```
assembler.py [source] [-o output]
```

`source` defaults to `main.asm` if not given

use `-o [name]` or `--output [name]` if you want the output binary to have a different name from the original assembly

## Syntax

### Format
Each line is an instruction with its parameters. starts with the instruction (case insensitive), followed by parameters separated by comma(`,`), which ends up looking like `INST param1, param2`

### Prefix
| Prefix | Usage |
| --- | --- |
| `$` | Register; A, X, and Y |
| `%` | Immediate value; Constant value or a pointer to a memory address |
| None | Ram Address |

#### Register
For registers (`$[register]`) you use `a`, `x`, or `y` as register name, so `$a`, `$x`, or `$y` (case insensitive) coorespond to each registers.

#### Value prefixes
For every parameters, you can use another prefix just after the type prefix (`$`,`%`,`*`), this correspond to the format of the value
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
Add `:` to the label's name (`[name]:`), this sets a constant with the name of the label to a pointer to the next instruction

### Special Directives
These are helper commands that give you more control over the output binary (case-insensitive)
| Command | Usage |
| --- | --- |
| `.literal [values]` | Insert literal values |
| `.ascii [text]` | Insert ASCII text |
| `.zero [n]` | Insert [n] number of zeroes |
| `.org [addr]` | Insert zeroes until the next instruction starts at [addr] |

#### .ascii Escape Codes
Used within `.ascii` directive to add a normally non-printable and unusable characters within the string
| Escape code | Meaning |
| --- | --- |
| `\n` | Newline |
| `\r` | Carriage Return
| `\t` | Tab |
| `\0` | Null |
| `\\` | Backslash |

### Comment
Use `;` followed by the comment

## System and Hardware specification
There is a BIOS system that runs on boot. loads the boot sector of your disk image and run it  
it also sets up useful functions that can be called through `int [id]` instruction with the `id` as the command number in this table below,
You set the A register to its parameter
| Command | Usage |
| --- | --- |
| `print` (`16`) | Print string that starts at address stored in A |
| `input` (`18`) | Get user input and save it to address stored in A |
| `disk_set_sector` (`19`) | Change current sector of the hard disk to value in A, set A to 0 if successful, set A to 1 if failed |
| `disk_read` (`20`) | Read the current 512 bytes sector to memory starting at address stored in A |
| `disk_write` (`21`) | Write a 512 byte chunk stored in memory starting at address stored in A |

### Memory Management
By default, only page 0x00000 is allocated.
allocate more by using `page [page-id]` where `page-id` is a new page

#### Ram Layout/Code Segment (x32 system)
| size | range (hexadecimal) | purpose |
| ---: | --- | --- |
|  4064M | `0000_0000`-`FDFF_FFFF` | General use memory |
|     4K | `FE00_0000`-`FE00_0FFF` | Memory Mapped IO |
| 32764K | `FE00_1000`-`FFFE_FFFF` | General use memory |
|    56K | `FFFF_0000`-`FFFF_DFFF` | BIOS Reserved |
|     4K | `FFFF_E000`-`FFFF_EFFF` | IVT Memory |
|     4K | `FFFF_F000`-`FFFF_FFFF` | Stack |

## Opcodes
| OPCODE | Meaning/Usage |
| --- | --- |
| **Arithmetic** |
| `add` | Add X by Y and save to A |
| `sub` | Subtract X by Y and save to A |
| `mul` | Multiply X by Y and save to A |
| `div` | Divide X by Y and save to A |
| `mod` | Modulo X by Y and save to A |
| **Bitwise** |
| `and` | Bitwise AND X and Y then save to A |
| `or` | Bitwise OR X and Y then save to A |
| `xor` | Bitwise XOR X and Y then save to A |
| `not` | Bitwise NOT X then save to A |
| `shr` | Shift X by Y to the right then save to A |
| `shl` | Shift X by Y to the left then save to A |
| `shrb` | Shift X by 8 bit to the right then save to A |
| `shlb` | Shift X by 8 to bit the left then save to A |
| **Control Flow (Relative Address)** |
| `jmp [label]` | Jump to [label] |
| `jz [label]` | Jump to [label] if A = 0 |
| `jnz [label]` | Jump to [label] if A != 0 |
| `jc [label]` | Jump to [label] if previous operation resulted in overflow |
| `jnc [label]` | Jump to [label] if previous operation did not result in overflow |
| `jeq [label]` | Jump to [label] if X = Y |
| `jne [label]` | Jump to [label] if X = Y |
| **Flow Control (Relative Address)** |
| `halt` | Halt execution immediately |
| `ret` | Return from function |
| `call [label]` | Call function at [label] |
| `bz [label]` | Call function at [label] if A = 0 |
| `bnz [label]` | Call function at [label] if A != 0 |
| `bc [label]` | Call function at [label] if previous operation resulted in overflow |
| `bnc [label]` | Call function at [label] if previous operation did not result in overflow |
| `beq [label]` | Call function at [label] if X = Y |
| `bne [label]` | Call function at [label] if X = Y |
| **Control Flow (Absolute Address)** |
| `ajmp [address]` | Jump to [address] |
| `ajz [address]` | Jump to [address] if A = 0 |
| `ajnz [address]` | Jump to [address] if A != 0 |
| `ajc [address]` | Jump to [address] if previous operation resulted in overflow |
| `ajnc [address]` | Jump to [address] if previous operation did not result in overflow |
| `ajeq [address]` | Jump to [address] if X = Y |
| `ajne [address]` | Jump to [address] if X = Y |
| **Flow Control (Absolute Address)** |
| `acall [address]` | Call function at [address] |
| `abz [address]` | Call function at [address] if A = 0 |
| `abnz [address]` | Call function at [address] if A != 0 |
| `abc [address]` | Call function at [address] if previous operation resulted in overflow |
| `abnc [address]` | Call function at [address] if previous operation did not result in overflow |
| `abeq [address]` | Call function at [address] if X = Y |
| `abne [address]` | Call function at [address] if X = Y |
| **Indirect Flow Control** |
| `jmpv` | Jump to address stored in register A |
| `callv` | Call function at address stored in register A |
| **Move** |
| `mov [destination], [source]` | Copy from [source] to [destination]. Only copy the 8 rightmost bit if copying from a register to memory |
| `movd [destination], [source]` | Copy 32 bit (4 bytes) of data at [source] to [destination]. (only register-memory and memory-memory copy) |
| **Variable Move/Store** |
| `ldv` | Load value from memory address stored in X to A |
| `stv` | Store value from A to memory address stored in X |
| **Stack** |
| `push [register]` | Push [register] to stack |
| `pop [register]` | Pop from stack to [register] |
| `pushr` | Push every registers to stack (A register first) |
| `popr` | Pop from stack to every register (Y register first, return to state "saved" by `pushr`) |
| **Interrupts** |
| `int [int-id]` | Call interrupt assigned to [int-id] |
| `intr [int-id], [label]` | Assign [int-id] to function at [label] |
| **Page allocation and freeing** |
| `page [page-id]` | Allocate a page to the first available frame |
| `move [id-old] [id-new]` | Give a new id to an allocated page |
| `free [page-id]` | Unallocate a page |
