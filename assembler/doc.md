# ASSEMBLY DOCS

## The Command
```
assembler.py [source] [-o output] [-O offset] [-v | --verbose]
```

`source` defaults to `main.asm` if not given

use `-o [name]` or `--output [name]` if you want the output binary to have a different name from the original assembly

use `-O [offset]` or `--offset [offset]` if your binary wont be loaded to memory at address x00000000

## Syntax

### Format
Each line is an instruction with its parameters. starts with the instruction's opcode, followed by
parameters separated by comma(`,`), which ends up looking like `OPCODE param1, param2`

### Prefix
| Prefix | Usage |
| --- | --- |
| `$` | Register; A, X, and Y |
| `%` | Immediate value; Constant value or a pointer to a memory address |
| `*` | Cache Address |
| None | Ram Address |

#### Register
For registers (`$[register]`) you use `a`, `x`, or `y` as register name, so `$a`, `$x`, or `$y` (case insensitive) coorespond to each registers respectively

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
Add `:` to the label's name (`[name]:`), it is recommended (but not required) to use indentation for the part that should be inside

### Special Directives
These are helper commands that give you more control over the output binary (case-insensitive)
| Command | Usage |
| --- | --- |
| `.literal [values]` | Add literal values |
| `.ascii [text]` | Add ASCII text |
| `.zero [n]` | Add [n] number of zeroes |

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
Use `;`, can be anywhere

## System and Hardware specification
There is a BIOS program that runs on every execution. it sets up useful commands

These can be called through `int [id]` instruction with the `id` as the command number in this table below
You set the A register to its parameter
| Command | Usage |
| --- | --- |
| `print` (`16`) | Print string that starts at ram address stored in A |
| `input` (`18`) | Get user input and save it to ram address stored in A |
| `disk_set_sector` (`19`) | Change current sector of the hard disk to value in A, set A to 0 if successful, set A to 1 if failed |
| `disk_read` (`20`) | Read the current 512 bytes sector to memory startimg at address stores in A |
| `disk_write` (`21`) | Write a 512 byte chunk stored in memory starting at address stored in A |

### Memory Management
By default, only page 0x00000 is allocated.
allocate more by using `page [page-id]` where `page-id` is a new page

#### Cache Layout
| range | purpose |
| --- | --- |
| `0000` - `EFFB` | General use memory |
| `EFFC` - `EFFF` | BIOS reserved |
| `F000` - `FEFF` | Data + Call Stack |
| `FF00` - `FFFF` | Software interrupt targets |

#### Ram Layout (x32 system)
| size | range (hexadecimal) | purpose |
| --- | --- | --- |
| 4064M | `0000_0000`-`FDFF_FFFF` | General use memory |
|    4K | `FE00_0000`-`FE00_0FFF` | Memory Mapped IO |
|    8K | `FE00_1000`-`FFFE_FFFF` | General use memory |
|   64K | `FFFF_0000`-`FFFF_FFFF` | BIOS Reserved |

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
| `not` | Bitwise NOT X and Y then save to A |
| `shr` | Shift X by Y to the right then save to A |
| `shl` | Shift X by Y to the left then save to A |
| `shrb` | Shift X by 8 bit to the right then save to A |
| `shlb` | Shift X by 8 to bit the left then save to A |
| **Control Flow** |
| `jmp [address/label]` | Jump to [address/label] |
| `jz [address/label]` | Jump to [address/label] if A = 0 |
| `jnz [address/label]` | Jump to [address/label] if A != 0 |
| `jc [address/label]` | Jump to [address/label] if previous operation resulted in overflow |
| `jnc [address/label]` | Jump to [address/label] if previous operation resulted in overflow |
| `jeq [address/label]` | Jump to [address/label] if X = Y |
| `jne [address/label]` | Jump to [address/label] if X = Y |
| **Flow Control** |
| `halt` | Halt execution immediately |
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
| **Page allocation and freeing** |
| `page [page-id]` | Allocate a page to the first available frame |
| `free [page-id]` | Unallocate a page |
