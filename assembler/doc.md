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

### Literal Values

Literal values are evaluated at assembly time and may refer to constants, labels, or registers.

#### Structure
```
Value ( + Value | - Value )*
```
* All additions and subtractions are resolved during assembly.
* Expressions are evaluated left-to-right.
* Whitespace is ignore.

Examples

* `label + 16`
-> immediate value of label plus 16
If label = 32, result is **48**

* `[label - K]`
-> RAM address label minus constant K
If label = 32 and K = 3, result is **29**

### Value prefixes

Each value may specify its numeric format using a prefix:

|Prefix | Format |
| --- | --- |
| `0x` | Hexadecimal |
| `0b` | Binary |
| `0o` | Octal |
| `'` | ASCII character|

Examples:
* `xFF`
* `b1010`
* `'A`

### Dereference

Deferencing is a process of getting the value stored at a memory address

For example
```
[ xE00 ]
```
means "The value stored at ram address `0x0E00`"

### Registers

Registers are written as:
```
A   X   Y
```
* Register names are case-insensitive.
* Only A, X, and Y are valid.

### Literal value addition and subtraction

Literal values may be offset using `+` or `-`:
* Offsets apply to both immediate values and RAM addresses.
* Offsets must be resolvable at assembly time.

Examples:
* `label + 4`
* `[label - 1]`
* `0x100 + K`

### Definition
#### Constants Definition
Use `const` keyword followed by the name, then its value (`const [name] [literal value]`)

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

#### Interrupts
As mentioned before that BIOS defines software interrupts, you can define other interrupts as well, like for handling faults or hardware interrupts

This is what each interrupt IDs are used for
| range (hexadecimal) | purpose |
| --- | --- |
| `000`-`0FF` | Software interrupts |
| `100`-`17F` | Fault interrupts |
| `180`-`1FF` | Hardware interrupts |

Fault interrupts
| interrupt id (hexadecimal) | Fault |
| `100` | Interrupt fault: The software or fault interrupt attempted to be called is undefined |
| `101` | Opcode fault; The CPU decoded an opcode in memory and is unable to execute it |
| `102` | Page fault; Attempted to access memory in unallocated address |
| `103` | IVT overflow; The interrupt id attempted to be registerd is above 512 |

## Opcodes
| OPCODE | Meaning/Usage |
| --- | --- |
| **Arithmetic** |
| `add` | Add X by Y and save to A |
| `sub` | Subtract X by Y and save to A |
| `mul` | Multiply X by Y and save to A |
| `div` | Divide X by Y and save to A |
| `mod` | Modulo X by Y and save to A |
| `sxtw` | Convert signed 8 bit to signed 16 bit in register A |
| `sxtd` | Convert signed 16 bit to signed 32 bit in register A |
| `sxtq` | Convert signed 32 bit to signed 64 bit in register A |
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
| `movw [destination], [source]` | Copy 16 bit (2 bytes) of data at [source] to [destination]. (only register-memory and memory-memory copy) |
| `movd [destination], [source]` | Copy 32 bit (4 bytes) of data at [source] to [destination]. (only register-memory and memory-memory copy) |
| `movq [destination], [source]` | Copy 64 bit (8 bytes) of data at [source] to [destination]. (only register-memory and memory-memory copy) |
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
