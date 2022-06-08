# EBNF Specification

This file contains the grammar rules for the parser
```
circuitDefinition = deviceList , connectList , monitorList ;
comment = "/" , { character } , "/" ;

deviceList = "DEVICE", device , { "," , { comment } , device } , ";" , { comment };
device = gate | switch | clock ;
deviceName = letter , { letter | digit } ;
switch = deviceName , ":" , "SWITCH" , ( 0 | 1 ) ;
clock = deviceName , ":" , "CLOCK" , digit , { digit } ;
gate = deviceName , ":" , operator , [ digit , { digit }, "INPUTS" ]
operator = "AND" | "OR" | "NAND" | "NOR" | "DTYPE" | "XOR" | "NOT" ;

connectList = "CONNECT" , connection , { "," , { comment } , connection } , ";" , { comment }
;
connection = output , "->" , input ;
input = deviceName , "." , ( "I" , { digit } | dtypeInput ) ;
dtypeInput = "DATA" | "CLK" | "SET" | "CLEAR" ;
output = deviceName , [ "." , ( "Q" | "QBAR" ) ] ;

monitorList = "MONITOR" , output , { "," , { comment } , output } , ";" , { comment } ;
```