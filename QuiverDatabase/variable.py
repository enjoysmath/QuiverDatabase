from .atomic_symbol import AtomicSymbol as Atom
import re
from .keyword import Keyword


class Variable:
    base_parser = Atom.alphabet_parser
    subscript_parser = re.compile(r"\{-?[0-9]+\}|[0-9]")  # Put longest alternative first
    prime_parser = re.compile(r"'+")
    # Couldn't get longest match to work when using {0, 2} in a regex, so had to split up into
    # multiple regexes and somewhat manually parse.    
    
    def __init__(self, base=None, prime=None, sub=None):
        self.base = base
        self.prime = prime
        self.sub = sub
                
    def __repr__(self):
        return 'Variable("' + str(self) + '")'
    
    def __str__(self):
        res = self.base
        if self.prime:
            res += self.prime
        if self.sub:
            res += '_'
            if len(self.sub) > 1:
                res += '{' + self.sub + '}'
            else:
                res += self.sub
        return res
    
    def __hash__(self):
        return hash(repr(self))
    
    def __eq__(self, x):
        return self.base == x.base and self.sub == x.sub and self.prime == x.prime
        
    @staticmethod
    def parse_into_template(text:str) -> tuple:
        """
        Returns template as a list of Keywords, literal str's, and Variables.
        Returns variables as a dict mapping each variable to every location within template (a list of locations).
        Returns template, variable (a tuple).
        """
        template = []
        variables = {}
               
        # Form the initial template composed of literal strings and Keywords
        start = 0
        for keyword in Keyword.regex.finditer(text):
            prefix = text[start : keyword.span()[0]]
            if prefix:
                template.append(prefix)
            template.append(Keyword(keyword.group()))     
            start = keyword.span()[1]
            
        # Append the remaining text, the previous entry either doesn't exist or is a keyword
        # since we're looping over all matches of Keywords above
        if start < len(text):
            template.append(text[start:])
        
        # For each string piece in the template, process variables
        # that occur within it, keeping track of where to insert.
        k = 0
        for piece in list(template):   # First make a copy 
            if isinstance(piece, str):
                start = 0
                prefix = ''
                template.pop(k)   # Rem to pop the piece we're further processing
                
                while start < len(piece):
                    V, end = Variable.longest_match(piece, pos=start)
                    #start = end
                    
                    if V is None:
                        # In the case a variable is not parsed, we just pass the text through as a literal.
                        prefix += piece[start:end]
                    else:                
                        if prefix:
                            template.insert(k, prefix)
                            k += 1
                            prefix = ''
                            
                        template.insert(k, V)
                        
                        if V not in variables:
                            variables[V] = [k]
                        else:
                            variables[V].append(k)
                        k += 1
                        
                    start = end
                
                # Append the remaining str or concat it to previous str entry
                if start < len(piece):
                    if k > 0 and isinstance(template[k-1], str):
                        template[k-1] += piece[start:]
                    else:
                        template.insert(k, piece[start:])
                        k += 1
                        
            elif isinstance(piece, Keyword):
                k += 1
                
        return template, variables
                    
                    
    @staticmethod
    def longest_match(text, pos):
        """
        Find the longest variable starting from pos, within text
        """
        
        base = Variable.base_parser.match(text, pos=pos)
        
        if base is None:
            return None, pos + 1
        
        pos = base.span()[1]
        subscript = None
        prime = None
        
        for i in range(2):
            if subscript is None and text.startswith('_', pos):
                subscript = Variable.subscript_parser.match(text, pos=pos+1)
                pos = subscript.span()[1]
            elif prime is None and text.startswith("'", pos):
                prime = Variable.prime_parser.match(text, pos=pos)
                pos = prime.span()[1]
                
        if prime is not None:
            prime = prime.group()
            
        if subscript is not None:
            subscript = subscript.group()
            if subscript.startswith("{"):
                subscript = subscript[1:-1]  # Remove the braces {}
        
        base = base.group()
        
        return Variable(base, prime, subscript), pos  
                       
        
        
        