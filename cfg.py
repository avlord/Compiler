###Control Graph Flow ###
from enum import Enum
from instructions import *
from tokenizer import *

class Block(Enum):
    JOIN = 'join'
    IF = 'if_then'
    WHILE = 'while'
    FUNCTION = 'function'
    ROOT = 'root'
    FALL = 'fall'
    BRANCH = 'branch'

class Instruction(Enum):
    CONST = 'const'
    ADD = 'add'
    SUB = 'sub'
    MUL = 'mul'
    DIV = 'div'
    CMP = 'cmp'
    ADDA = 'adda'
    LOAD = 'load'
    STORE = 'store'
    PHI = 'phi'
    END = 'end'
    BRA = 'bra'
    BNE = 'bne'
    BEQ = 'beq'
    BLE = 'ble'
    BLT = 'blt'
    BGE = 'bge'
    BGT = 'bgt'
    READ = 'read'
    WRITE = 'write'
    WRITENL = 'writeNL'
    CALL = 'call'
    SET = 'set' #Helper instruction

class VarType(Enum):
    VAR = 'var'
    ARRAY = 'array'

class XInstruction():
    def __init__(self, instruction, instruction_id ,op_ids=[], meta=None) -> None:
        self.instruction = instruction
        self.instruction_id = instruction_id
        self.meta = meta
        self.op_ids = [x for x in op_ids]
        

    def set_operands(self, op_ids):
  
        self.op_ids = op_ids
    
    def add_operand(self, op_id):
        if type(op_id)==list:
            self.op_ids.extend(op_id)
        else:
            self.op_ids.append(op_id)

    def __repr__(self) -> str:
        return f'{self.instruction_id, self.instruction} : {self.op_ids}\n'

    def __str__(self) -> str:
        return f'{self.instruction} op_ids: {self.op_ids}'


class Variable():
    def __init__(self, name, value, index, op_index, type=VarType.VAR) -> None:
        self.type = type
        self.name = name
        self.value = value
        self.index = index
        self.op_index = op_index

    def __eq__(self, o: object) -> bool:
        return self.name == o.name and self.value == o.value and self.index == o.index
    
    def __gt__(self, o: object) -> bool:
        return self.value > o.value
    
    def __repr__(self) -> str:
        return self.name

class BasicBlock():
    def __init__(self, type, parent = None, id=0) -> None:
        self.table = {}
        self.instructions = []
        self.type = type
        self.block_id = id

        self.parent = parent
        
        self.fall_through = None
        self.branch = None
        self.join = None
    def __repr__(self) -> str:
        return f'Block {self.block_id} : {self.type}'

class ControlFlowGraph():
    def __init__(self) -> None:

        self.table = {}
        self.const_table = {}

        self.blocks = []
        self.root = BasicBlock(Block.ROOT)
        self.blocks.append(self.root)
        
        self.current_block = self.root

        self.counter = 0
        self.var_counter = 0
        self.block_counter = 1
        # self.instruction_counter = 0

    def set_block(self, block):
        if block.type == Block.FALL:
            self.current_block.fall_through = block
        elif block.type == Block.BRANCH:
            self.current_block.branch = block
        elif block.type == Block.JOIN:
            self.current_block.join = block
        else:
            self.current_block.parrent = block

    def init_block(self, block_type: Block, parent) -> BasicBlock:
        "Initialize a new block"

        block = BasicBlock(block_type, id = self.block_counter, parent=parent)
        self.blocks.append(block)
        self.block_counter += 1
        return block
   
    def init_var(self, var_name):
        "Initialize a variable"
        var = Variable(name=var_name, value=0, index=self.var_counter, type=VarType.VAR, op_index=None)
        self.current_block.table[var_name] = var
        
        #To all blocks or to the current block?
        self.var_counter += 1

    def update_phi(self, left_branch, right_branch):
        idents = set(left_branch.table.keys()) | set(right_branch.table.keys())
        
        for var in idents:
            print('UPD PHI,', var)
            if var in left_branch.table and var in right_branch.table:
                
                if left_branch.table[var] != right_branch.table[var]:

                    inst = self.make_dummy_instruction(Instruction.PHI, )
                    inst.add_operand([left_branch.table[var].op_index, right_branch.table[var].op_index])
                    
                    continue 
            
            elif var in left_branch.table:
                val = left_branch.table[var].op_index
            else: 
                val = right_branch.table[var].op_index

            inst = self.make_dummy_instruction(Instruction.PHI, )
            inst.add_operand([self.current_block.parent.table[var].op_index, val])

    def set_var(self,var_name, value):

        #IF WE HAVE A VARIABLE and attaching an instruction
        if type(value) == XInstruction:
            op_index = value.instruction_id

        #IF WE HAVE A VARIABLE and attaching a constant
        if type(value) == int:
            op_index = self.const_table[value]
        
        #IF WE HAVE A VARIABLE and attaching a variable
        if type(value) == Variable:
            op_index = value.op_index

        #SSA VARIABLE, WE NEED TO CREATE A NEW ONE #
        var = Variable(name=var_name, value=value, index=self.var_counter, type=VarType.VAR, op_index= op_index)
        
        #MAKE A FUNCTION FOR THAT ONE#
        self.current_block.table[var_name] = var
        print('SET VAR', var_name, value, self.current_block)
        #FOR DEBUG PURPOSES#
        self.add_empty_insturction(Instruction.SET, var)

        self.var_counter += 1

        self.counter += 1

    def get_variable(self, var_name):
        "Get a variable"
        if var_name in self.current_block.table:
            return self.current_block.table[var_name]
        else:
            return self.current_block.parent.table[var_name].value

    def init_const(self, value):
        ## IF ALREADY INITIALIZED ##
        if value in self.const_table:
            return
        ## BB0 ##
        self.const_table[value] = self.counter
        
        self.add_insturction(Instruction.CONST, value)
        
    def init_comparison(self,op,x,y):
        
        instruction = self.add_insturction(Instruction.CMP, x, y)
        return instruction

        # fall_through_block_id = self.current_block.fall_through

        # if op == Token.LSS:
        #     self.add_insturction(Instruction.BGE, instruction.instruction_id, fall_through_block_id)




    def add_empty_insturction(self, instruction, *var):
        instruction = self.make_instruction(instruction, *var)
        self.current_block.instructions.append(instruction)
        
        return instruction

    def make_dummy_instruction(self, instruction, *var):
        
        instruction_new = XInstruction(instruction, self.counter, op_ids=var)
        self.current_block.instructions.append(instruction_new)
        self.counter += 1
        return instruction_new


    def add_insturction(self, instruction, *var):
        
        if type(instruction) == XToken:
            instruction = self.init_insturction(instruction)
        
        instruction = self.make_instruction(instruction, *var)
        self.current_block.instructions.append(instruction)
        self.counter += 1
        return instruction

    def init_insturction(self,token):
        if token == Token.ADD:
            return Instruction.ADD

        elif token == Token.SUB:
            return Instruction.SUB

        elif token == Token.MUL:
            return Instruction.MUL

        elif token == Token.DIV:
            return Instruction.DIV

    def make_instruction(self, instruction, *var):
        var_idx = []
        for v in var:
            
            if type(v) == Variable:
                var_idx.append(self.current_block.table[v.name].op_index)
            elif type(v) == XInstruction:
                var_idx.append(v.instruction_id)
            else:
                var_idx.append(self.const_table[v])

        instruction_new = XInstruction(instruction, self.counter, op_ids=var_idx)
 
        return instruction_new
    
    def print_blocks(self):
        print(self.blocks)
        for block in self.blocks:
            print('BLOCK ID: ', block.block_id, 'TYPE: ', block.type)
            print(block.instructions, )
    
    def print_table(self):
        print('\n PRINT VAR TABLE')
        for block in self.blocks:
            print('\n BLOCK ID: ', block.block_id, 'TYPE: ', block.type)
            for var in block.table:
                print(var, 'ID: ',block.table[var].op_index, 'VAL: ', block.table[var].value)
    
    def print_const_table(self):
        print('\n PRINT CONST TABLE')
        
        for const in self.const_table:
            print('ID: ', self.const_table[const], 'Val:', const, )