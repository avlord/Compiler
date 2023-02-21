### Performs Tokenizing of the file###
from enum import Enum
import re

class Token(Enum):
    SEMICOLON = ';'
    MAIN = 'main'
    FUNCTION = 'function'
    IF = 'if'
    THEN = 'then'
    ELSE = 'else'
    FI = 'fi'
    WHILE = 'while'
    DO = 'do'
    OD = 'od'
    RETURN = 'return'
    VOID = 'void'
    VAR = 'var'
    ARRAY ='array'
    LET = 'let'
    CALL = 'call'
    IDENT = re.compile(r'[a-zA-Z_][a-zA-Z_0-9]*')
    NUMBER = re.compile(r'[0-9]+')
    SET = '<-'
    PERIOD = '\.'
    NEWLINE = '\n'
    ADD = '\+'
    SUB = '-'
    MUL = '\*'
    DIV = '/'
    # REL_OP = re.compile(r'==|!=|<|<=|>|>=') # 20, 21, 22, 23, 24, 25
    EQ = '\=='
    NEQ = '\!='
    LSS = '\<'
    LEQ = '\<='
    GTR = '\>'
    GEQ = '\>='
    COMMA = '\,'
    LBRACKET = '\['
    RBRACKET = '\]'
    LPAREN = '\('
    RPAREN = '\)'
    LBRACE = '\{'
    RBRACE = '\}'
    SPACE = ' '

class XToken():
    def __init__(self, name, item):
        self.name = name
        self.item = item

    def __str__(self):
        return f'{self.name} {self.item}'

    def __repr__(self):
        return f'{self.name} {self.item}'

    def __eq__ (self, other):
        return self.name == other

class Tokenizer():
    def __init__(self,):
        self.index = 0
        self.tokens = []

    def get_token(self):
        for token in Token:
            pat = re.compile(token.value)            
            match = re.Pattern.match(pat, self.string[self.index:])
            if match is not None :
                if (token == Token.NEWLINE) | (token == Token.SPACE):
                    self.index += match.end()
                    return None
                self.index += match.end()  ### +1 to skip the space
                token.item = match[0]
                return XToken(token, token.item)
        raise Exception("Invalid Token")

    def tokenize(self, line):
        self.string = line
        self.index = 0
        self.tokens = []
        while self.index < len(self.string):
            new_token = self.get_token()
            
            if new_token is not None:
                self.tokens.append(new_token)
                
        return self.tokens
    
    def tokenize_file(self,lines):
        self.tokens = []
        for line in lines:
            print(line)
            self.tokens += self.tokenize(line)
        print(self.tokens)
        return self.tokens


# errorToken 0 
# * timesToken 1 
# / divToken 2 
# + plusToken 11 
# - minusToken 12 
# == eqlToken 20 
# != neqToken 21 
# < lssToken 22 
# >= geqToken 23 
# <= leqToken 24 
# > gtrToken 25 
# . periodToken 30 
# , commaToken 31 
# [ openbracketToken 32 
# ] closebracketToken 34 
# ) closeparenToken 35 
# <- becomesToken 40 
# then thenToken 41 
# do doToken 42 
# ( openparenToken 50 
# FileReader.Error =0 
# FileReader.EOF = 255 
# number number 60 
# identifier ident 61 
# ; semiToken 70 
# } endToken 80 
# od odToken 81 
# fi fiToken 82 
# else elseToken 90 
# let letToken 100 
# call callToken 101 
# if ifToken 102 
# while whileToken 103 
# return returnToken 104* 
# var varToken 110 
# array arrToken 111 
# void voidToken 112 
# function funcToken 113 
# procedure procToken 114 
# { beginToken 150 
# computation mainToken 200 
# end of file eofToken 255