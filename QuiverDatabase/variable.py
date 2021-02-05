from .atomic_symbol import AtomicSymbol as Atom
import re
from .keyword import Keyword


class Variable:
    regex = re.compile(
        r"(?P<b>" + Atom.alpha_regex + ")" + \
        r"((?P<p>'*)?|_([0-9]|\{(?P<s>-?[0-9]+)\})){0,2}")
    
    def __init__(self, base=None, prime=None, sub=None):
        self.base = base
        self.prime = prime
        self.sub = sub
                
    def __str__(self):
        res = self.base
        if self.prime:
            res += self.prime
            if self.sup and self.sub:
                res = '{' + res + '}'
        if self.sub:
            res += '_'
            if len(self.sub) > 1:
                res += '{' + self.sub + '}'
            else:
                res += self.sub
        return res
        
    @staticmethod
    def parse_template(text:str) -> str:
        template = []
        variables = {}
        k = 0
        start = 0
        
        for keyword in Keyword.regex.finditer(text):
            for match in Variable.regex.finditer(text[start:keyword.span()[0]]):
                span = match.span()
                literal = piece[start:span[0]]
                
                if literal:
                    template.append(literal)
                    k += 1
                    
                start = span[1]
                
                b = match.group('b')
                    
                if b is None:
                    template += piece[span[0]:span[1]]
                    continue
                    
                sub = match.group('s')
                prime = match.group('p')
                
                v = Variable(b, prime, sub)
                if v not in variables:
                    variables[v] = [k]
                else:
                    variables[v].append(k)
                template.append(v)
                k += 1
                    
            if start < len(piece):
                template += piece[start:]
            
            template.append(keyword.group())
                
        return template, variables
                    
        
        
        