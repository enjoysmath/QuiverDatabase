import re

class Keyword:
    regex = re.compile(
        r'(\\text|\\textbf|\\rm|\\bf)\{[^\}]*\}|' +    # Any text-like pattern
        r'\\begin\{[^\}]*\}|' +
        r'\\end\{[^\}]*\}|' +
        r'\\text{Hom}|' +
        r'\\textbf{Set}|' + 
        r'\\lim|' +
        r'\\otimes|' + 
        r'\\bullet',
        flags=re.IGNORECASE)
    
    def __init__(self, keyword:str):
        self.string = keyword
        
    def __repr__(self):
        return 'Keyword("' + self.string + '")'
