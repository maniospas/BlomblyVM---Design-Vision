# Blombly

*A virtual machine of the code block assembly language.*

This repository holds the design concept of the VM and compiler
alongside Python implementations.

## Blombly VM specification

Blombly machines contain a dictionary of one-output
methods implemented in their host programming
language, as well as the following list of assembly 
commands. All commands have the form

`NAME result arg1 arg2`

where the result and arguments point to respective
memory locations to store and retrieve data. Memory
locations may hold data types of the host language
or blombly code blocks that can be executed by the 
CALL command.

| Command        | Description                                                                                                                                                                                         |
|----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| INPUT Y X;     | Transfers the contents of the program input's memory location X to the current memory location Y. The program's inputs are viewable by any block, and will typically hold parameters and constants. |                                                                                                                                                                                     |
| LAZY Y;        | Indicates the start of a current code block, searches the program until the block's end, and stores the block (e.g., its start and end positions within the program) at the memory location Y.      |
| END none;      | Ends the current code block. Should never store the block (the none result specification is mandatory).                                                                                             |   
| RETURN none X; | Returns from the current code block's execution with value X (the none result specification is mandatory).                                                                                          |
| IS Y X;        | Moves a value from memory location X to Y or runs a code block without creating a copy of memory. Thus, memory Y will never be holding a code block.                                                |
| CALL Y P B ;   | Creates a copy of the current memory, in which first the code block P (this can be none) is called and afterwards B. The value returned from B is stored in the memory location Y.                  |                                                                                                        

Memory symbols are parsed and optimized at design times. The same
symbols should always point to the same memory locations. The IS 
command should *not* copy memory, but move around pointers. Any
number of CALLs should be able to run concurrently. When parsing
source code, create an initial memory (maybe only the first portion of
it and let the VM copy it) with any constants that are transferred
to local variables through INPUT.

## The blombly language

This repository comes alongside a parser for the blombly language,
which is a functional programming language running on the namesake VM.

This language can perform the same function calls as the VM,
but simplifies other instructions. In particular, code blocks
should look like this, where the brackets `{}` indicate the start 
and end of the blocks, and `return` method immediately breaks the
block's execution and returns its value:

```javascript
code = {
    z = add(x,y);
    return(z);
}
```

Code blocks serve as functions to be called. By default,
they retrieve values from their calling scope (the same 
symbols refer to the same memory locations between
any parts of the code). However, you can pass another
block as an argument to execute that first. Block
calling is memory-safe, i.e., a copy of the memory
is pushed and popped afterwards.

```javascript
x = 1;
y = 2;
z = code();
print(z); // 3
z = code(x=2);
print(x); // still 1
print(z); // 4
```
