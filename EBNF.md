# EBNF Specification

This file contains the grammar rules for the parser
```
deviceList = “DEVICE”, device , {“,”, device} , “;” ;
device = (arithmeticGate | dtype | xor | switch | clock);
deviceName = letter, {letter | digit} ;
switch = deviceName , “:” , “SWITCH”, (0 | 1) ;
clock = deviceName , “:” , “CLOCK”, digit , { digit };
gate = deviceName, “:” , operator , [digit , { digit }, “INPUTS”];  
operator = “AND” | “OR” | “NAND” | “NOR” | “DTYPE” | “XOR”;



connectList = “CONNECT”, connection , {“,”, connection} , “;” ;
connection = output, “->”, input , ;
input = deviceName, “.I”, {digit} ;
output = deviceName , [“.” , (“Q” | “QBAR”)];

monitorList = “MONITOR” , output , {“,” , output} , “;” ;
```