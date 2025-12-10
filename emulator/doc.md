# Emulator docs
A documentation on how to use the emulator (more detail than `emulator.py -h`)

### The Command
The most basic usage of the emulator is to simply run it, it will look for `main.bin` in the current directory and use it as disk image
Or you can add a file name and it will use that file as the disk image
```
emulator.py [source file]
```

### Flags
You can use flag to define the behavior of the emulator, particularly for debugging

| Flag | Usage |
| --- | --- |
| `-t` `--time` | Log performance record, the slowest, fastest, median and average time to run instructions |
| `-d` `--trace` | Log each step of execution to a file named `.trace` in the current directory. record data such as the program counter, the instructions, the parameters, value of the registers and the relevant part of memory |
| `-m` `--dump` | Log a record of the final program counter, registers, cache and ram to console |
| `-M` `--dump-file` | Log a record of the final program counter, registers, cache and ram to a file named `.dump` |
| `-g` `--graph` | Create a logarithmic graph showing the time taken to execute each instructions |
| `-R` `--block-recursion` | Halt the program if the program counter repeated more than 10,000 times |
| `-r` `--block-small-recursion` | Halt the program if the program counter repeated more than 1,000 times |
| `--block-large-recursion` | Halt the program if the program counter repeated more than 1,000,000 times |