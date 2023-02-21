import string
from tokenizer import Tokenizer, Token, XToken
from cfg import *
from instructions import *

class Parser():

    def __init__(self, lines):

        self.index = 0
        # self.table = {} # Remove it
        
        #Tokenized File
        self.string = lines

        #Main CFG
        self.cfg = ControlFlowGraph()

    def parse(self):

        return self.computation()

    def next_token(self, num: int = 1) -> XToken:
        """Move the index to the next token"""
        if self.index + num < len(self.string):
            self.index += num
            return self.string[self.index] 

    def get_token(self,) -> XToken:
        if self.index < len(self.string):
            return self.string[self.index]

    def number(self,) -> int:
        
        symbol = self.get_token()

        ###INIT CONST###
        self.cfg.init_const(int(symbol.item))

        self.next_token()
        
        return int(symbol.item)

    def factor(self,):

        x = self.get_token() 
        
        if x == Token.LPAREN:

            self.next_token() 
            
            x = self.expression()
            
            y = self.get_token()
            
            if y != Token.RPAREN:
                raise Exception("No closing Bracket")

            self.next_token() 
            
            return x
        
        ##Variable###
        
        elif x == Token.IDENT:
            
            val = self.cfg.get_variable(x.item) ### REMOVE?
       
            self.next_token()
           
            return val 
      
            
        return self.number() # >> by 1

    def term(self,):
        x = self.factor() #  at least 1 >>
        operator_symbol = self.get_token()
        
        while (operator_symbol==Token.MUL)|(operator_symbol==Token.DIV):
           self.next_token()
        
           y = self.factor() ## >> by 1 symbol
           x = self.cfg.add_insturction(operator_symbol, x,y)
           
           operator_symbol = self.get_token()
        return x

    def expression(self,):

        x = self.term() 
        operator_symbol = self.get_token()

        while (operator_symbol==Token.ADD)|(operator_symbol==Token.SUB):
           
            self.next_token()
           
            y = self.term() ## >> by 1 symbol
            x = self.cfg.add_insturction(operator_symbol, x,y)
           
            operator_symbol = self.get_token()

        return x

    def designator(self,):
       
        ### ASSUME THAT IT IS NOT AN ARRAY###
        # if x == Token.VAR:
        
        var_name = self.get_token().item
        
        self.next_token(2) ### SKIP IDENT and <- 
        expr = self.expression()
       
        ###INIT CONST##
        
        ### ADD TO CFG ###
        self.cfg.set_var(var_name, expr)
        
        # self.table[var_name] = expr
       
        # else:
        #     raise Exception("No variable name")

    def assignment(self,):
        x = self.get_token()
        if x == Token.LET:
            x = self.next_token()
            self.designator()

    def ifstatement(self,):
        x = self.get_token()
        
        if x == Token.IF:
            
            self.next_token()


            MAIN_block = self.cfg.current_block
            FALL_block = self.cfg.init_block(Block.FALL,parent=MAIN_block)

            self.cfg.set_block(FALL_block)

            instruction_main_branch = self.relation() 

            if self.get_token() != Token.THEN: ### CHANGE TO IF IN AVAILABLE TOKENS
                raise Exception("No then") 

            x = self.next_token()
            
            self.cfg.current_block = self.cfg.current_block.fall_through
            
            x = self.statsequence() ###FIX NEGATIVE NUMBER ASSIGNMENT

            ###THEN###
            instruction_then_branch = self.cfg.make_dummy_instruction(Instruction.BRA) 
            ###ADD FALL BLOCK### 

            if (self.get_token() == Token.ELSE): #NOT ALWAYS RL
                self.next_token()

                ### CREATE BRANCH BLOCK ###
                BRANCH_block = self.cfg.init_block(Block.BRANCH,parent=MAIN_block)
                self.cfg.set_block(BRANCH_block)
               
                self.cfg.current_block = BRANCH_block
                
                #PARSING BRANCH ELSE#
                self.statsequence()

                first_inst = BRANCH_block.instructions[0]

                #BACK TO MAIN BLOCK#
                self.cfg.current_block = MAIN_block
                instruction_main_branch.add_operand(first_inst.instruction_id)
                ### ADD FALL THROUGH INSTRUCTION ###
                ###

            if self.get_token() != Token.FI:
                raise Exception("No fi")

            ### ADD JOIN BLOCK###

            ###HERE WE UPDATE PHI###

            self.cfg.current_block = MAIN_block

            JOINT_block = self.cfg.init_block(Block.JOIN,parent=MAIN_block)
            self.cfg.set_block(JOINT_block)
            
            self.cfg.current_block = JOINT_block
            self.cfg.set_block(MAIN_block) 
            instruction_then_branch.op_ids.append(self.cfg.counter)

            self.cfg.update_phi(left_branch = BRANCH_block, right_branch = FALL_block)

            self.next_token()

    def relation(self,):
        
        # X <= / < / = / >= / > / <> Y

        x = self.expression()

        #Operator
        op = self.get_token()
        
        self.next_token()
        
        y = self.expression()
    
        instruction_cmp = self.cfg.init_comparison(op, x, y)

        if op == Token.EQ:
            inst = Instruction.BEQ

        elif op == Token.NEQ:
            inst = Instruction.BNE

        elif op == Token.LSS:
            inst = Instruction.BGE

        elif op == Token.LEQ:
            inst = Instruction.BGT

        elif op == Token.GTR:
            inst = Instruction.BLT

        elif op == Token.GEQ:
            inst = Instruction.BLE

        instruction = self.cfg.make_dummy_instruction(inst, instruction_cmp.instruction_id)
        return instruction
        
    def whilestatement(self,):
        pass


    def statsequence(self,):

        x = self.get_token()
        
        while (x==Token.LET)|(x==Token.IF)|(x==Token.WHILE):
            if x == Token.LET:
                self.assignment()
            elif x == Token.IF:
                self.ifstatement()
            elif x == Token.WHILE:
                self.whilestatement()
            x = self.get_token()
            self.next_token() #SEMICOLON
            x = self.get_token()
            
            # self.statement()
            # 
            # 
       

        ##TODO Implement function call##
        ##self.functioncall()
        ##self.returnstatement()

    def init_var(self, var_name):
        ###CALL TO CFG TO INIT VAR##
        self.cfg.init_var(var_name)
        # self.table[var_name] = 0

    def vardecl(self,):
        type = self.get_token()
        
        if type == Token.VAR: 
            var_name = self.next_token().item
            self.init_var(var_name)
            x = self.next_token()
            
            while x == Token.COMMA:
                var_name = self.next_token().item
                self.init_var(var_name)
                x = self.next_token()

        if x != Token.SEMICOLON:
            raise Exception("No semicolon")
        self.next_token()

    # def typedecl(self,):
    #     x = self.get_token()
    #     if x == Token.VAR:
    #        return x.item()
    #     elif x == Token.ARRAY: ###TODO
    #         return x.item()

    def computation(self,):
        results = []
        x = self.get_token()
        
        if x == Token.MAIN:
            x = self.next_token()
        else:
            raise Exception("No main function")

        while ( x != Token.PERIOD ):
            if (x == Token.VAR) | (x == Token.ARRAY):
                self.vardecl()

            elif x == Token.FUNCTION:
                raise Exception("Not implemented yet")

            ##STAT SEQUENCE##
            elif x == Token.LBRACE:
                
                self.next_token()
                evaluated_expr = self.statsequence()
                x = self.get_token()
                results.append(evaluated_expr)
                print(x)
                if x != Token.RBRACE:
                    raise Exception("No closing bracket")

                self.next_token() ##Gett Period token

            x = self.get_token()
        
        return results

file = open('test4.txt', 'r')
lines = file.readlines()
file.close()

tokenizer = Tokenizer()
lineParser = Parser(tokenizer.tokenize_file(lines))
lineParser.parse()
# print(lineParser.table)
lineParser.cfg.print_blocks()
lineParser.cfg.print_const_table()
lineParser.cfg.print_table()