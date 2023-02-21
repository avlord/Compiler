import string

class EXParser():
    def __init__(self, str):
        self.string = str
        self.index = 0
        self.const = ['0','1','2','3','4','5','6','7','8','9']
        self.chars = ' '.join(string.ascii_lowercase).split(' ')
        self.name_vars  = self.const + self.chars
        self.table = {}

    def next_symbol(self,num=1):
        if self.index + num < len(self.string):
            self.index += num
            return self.string[self.index] 

    def get_symbol(self,):
        if self.index < len(self.string):
            return self.string[self.index]

    def digit(self,):
        number = self.get_symbol()
        x  = self.next_symbol() 
        if x in self.const:
            number += x
            x = self.next_symbol()
        return int(number)

    def number(self,):
        symbol = self.digit()
        return symbol

    def identifier(self,):
        name = self.get_symbol()
        x = self.next_symbol().lower()
        while x in self.name_vars:
            name += x 
            x = self.next_symbol()
        return name

    def factor(self,):
        x = self.get_symbol() 
        
        if x == '(':
            self.next_symbol() 
            x = self.expression()
            y = self.get_symbol()
            if y != ')':
                raise Exception("No closing Bracket")
            self.next_symbol() 
            return x
        
        ##Variable###
        elif x in self.chars:
            name = self.table[self.identifier()]
            return name
            
        return self.number() # >> by 1

    def term(self,):
        x = self.factor() #  at least 1 >>
        operator_symbol = self.get_symbol()
        while (operator_symbol=='*')|(operator_symbol=='/'):
            self.next_symbol()
            y = self.factor() ## >> by 1 symbol
            if operator_symbol == '*':
                x = x*y
            elif operator_symbol == '/':
                x = x/y
            operator_symbol = self.get_symbol()
        return x

    def expression(self,):
        x = self.term() 
        operator_symbol = self.get_symbol()
        while (operator_symbol=='+')|(operator_symbol=='-'):
            self.next_symbol()
            y = self.term() ## >> by 1 symbol
            if operator_symbol == '+':
                x = x + y
            elif operator_symbol == '-':
                x = x - y
            operator_symbol = self.get_symbol()

        return x

    def computation(self,):
        results = []
        x = self.get_symbol()
        while x!= '.':
            if self.string[self.index:self.index+3] == 'var':
                self.index += 4
                var_name = self.identifier()
                self.next_symbol(4)
                expr = self.expression()
                self.table[var_name] = expr
                self.next_symbol()
            else:
                evaluated_expr = self.expression()
                self.next_symbol()
                results.append(evaluated_expr)
            x = self.get_symbol()

        return results


test_string = 'var abcd <- 3;var qq <- 7;2+5+abcd*15/qq;abcd/qq.'
parser = Parser(test_string)
print('Result of computation', parser.computation())

#Change to Tokens?