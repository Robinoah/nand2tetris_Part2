'''
VM Translator!
reads a .vm file, translates the contents to the HACK Assembly Language
and writes to a new .asm file 

@author Noah Waller
'''

#Parse Through .vm file
class Parser:
    def __init__(self, vmFileName):
        self.inFile = open(vmFileName)
        self.command = ["blank"]
        self.EOF = False
    
        self.cType = {
            'add': 'C_ARITHMETIC',
            'sub': 'C_ARITHMETIC',
            'neg': 'C_ARITHMETIC',
            'eq': 'C_ARITHMETIC',
            'gt': 'C_ARITHMETIC',
            'lt': 'C_ARITHMETIC',
            'and': 'C_ARITHMETIC',
            'or': 'C_ARITHMETIC',
            'not': 'C_ARITHMETIC',
            'push': 'C_PUSH',
            'pop': 'C_POP',
        }

    #Checks if current line or End of File
    def hasMoreLines(self):
      pos = self.inFile.tell()
      self.advance()
      self.inFile.seek(pos)
      return not self.EOF
    
    #Called if HasMoreLines does not End File
    def advance(self):
      currentLine = self.inFile.readline()
      if currentLine == '':
        self.EOF = True
      else:
        split = currentLine.split("/")[0].strip()
        if split == '':
          self.advance()
        else:
          self.command = split.split()
    
    #Gets command Type from Dict (cType)
    def commandType(self):
        return self.cType.get(self.command[0], 'missing') 
    #returns segment of current command
    def arg1(self):
        return self.command[1]
    #returns index of 
    def arg2(self):
        return self.command[2]


#writes .asm files
class CodeWriter:
    def __init__(self, asmFileName):
        self.source = asmFileName[:-4].split('/')[-1]
        self.outfile = open(asmFileName, "w")
        #ASM snippets
        self.nextLabel = 0
        self.pushD = "@SP\nM=M+1\nA=M-1\nM=D\n"
        self.popD = "@SP\nAM=M-1\nD=M\n"
        self.popA = "@SP\nAM=M-1\nA=M\n"
     

    #arithmetic funtion
    def writeArithmetic(self, command):
      label = self.source+str(self.nextLabel)
      ASMtoWrite= "//" + command + "\n"
      ASMtoWrite += self.popD
      if command not in ["neg","not"]:     
          ASMtoWrite += self.popA
          if command == "add":      
            ASMtoWrite += "D=D+A\n"
          elif command == "sub":                     
            ASMtoWrite += "D=A-D\n"
          elif command == "eq":
            self.nextLabel += 1
            ASMtoWrite += "D=D-A\n@" + label + ".EQUAL\nD;JEQ\nD=0\n@" + label + ".END\n0;JMP\n(" + label + ".EQUAL)\nD=-1\n(" + label + ".END)\n"
          elif command == "gt":
            self.nextLabel += 1
            ASMtoWrite += "D=D-A\n@" + label + ".GT\nD;JLT\nD=0\n@" + label + ".END\n0;JMP\n(" + label + ".GT)\nD=-1\n(" + label + ".END)\n"
          elif command == "lt":
            self.nextLabel += 1
            ASMtoWrite += "D=D-A\n@" + label +".LT\nD;JGT\nD=0\n@"+ label +".END\n0;JMP\n("+ label +".LT)\nD=-1\n("+ label +".END)\n"
          elif command == "and":
            ASMtoWrite+= "D=D&A\n"
          elif command == "or":
            ASMtoWrite+= "D=D|A\n" 
      elif command in ["neg","not"]:
          if command == "neg":
            ASMtoWrite+= "D=-D\n" 
          elif command == "not":
            ASMtoWrite+= "D=!D\n" 
      else:  
        ASMtoWrite = command + " not implemented yet\n"
        
      ASMtoWrite += self.pushD
      #Write ASM to .asm file
      self.outfile.write(ASMtoWrite)

  #push Pop function
    def writePushPop(self, command, segment, index):
      ASMtoWrite= ""
      segmentdict = {
        "argument":"ARG",
        "static":self.source+"." + index,
        "local":"LCL",
        "this":"THIS",
        "that":"THAT"
        }
      #Push
      if command == "C_PUSH":
        ASMtoWrite += "// push " + segment + " " + index + "\n"
        if segment in ["local","argument","this","that","static"]:
          ASMtoWrite += "@" + segmentdict[segment] + "\nD=M\n@" + index + "\nA=A+D\nD=M\n"
        elif segment in ["pointer","temp"]:
            address = (3 + int(index)) if segment == "pointer" else (5 + int(index))
            ASMtoWrite += "@" + str(address)+ "\nD=M\n"
        elif segment == "constant":
            ASMtoWrite += "@" + index + "\nD=A\n"
        ASMtoWrite += self.pushD
      #Pop   
      if command == "C_POP":
        ASMtoWrite += "// pop " + segment + " " + index + "\n"
        if segment in ["local","argument","this","that","static"]:
            ASMtoWrite += "@" + index + "\nD=A\n@"+ segmentdict[segment] + "\nA=M\nD=D+A\n@R13\nM=D\n" + self.popD + "@R13\nA=M\nM=D\n"
        elif segment in ["pointer","temp"]:
            address = (3 + int(index)) if segment == "pointer" else (5 + int(index))
            ASMtoWrite += self.popD + "@" + str(address) + "\nM=D\n"
      self.outfile.write(ASMtoWrite)

  
def main():
  #Prompts user for file name withought extension and instantiates parser and codewrite classes
  print("Enter File Name without extension: ")
  file = input()
  vmFile = file + ".vm"
  asmFile = file + ".asm"
  parser = Parser(vmFile) 
  codewrite = CodeWriter(asmFile)

  #reads through file and translates each line 
  while parser.hasMoreLines():
    parser.advance()
    cType = parser.commandType() 
    if cType == 'C_ARITHMETIC':
      codewrite.writeArithmetic(parser.command[0])
    elif cType == 'C_PUSH' or cType == 'C_POP':
        segment = parser.arg1()
        index = parser.arg2()
        codewrite.writePushPop(cType, segment, index)


if __name__ == '__main__':
  main()
