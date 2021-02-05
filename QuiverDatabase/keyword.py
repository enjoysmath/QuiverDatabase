import re

class Keyword:
    regex = re.compile(
        r'\\begin\{[^\}]*\}|' +
        r'\\end\{[^\}]*\}|' +
        r'\\text{Hom}|' +
        r'\\textbf{Set}|' + 
        r'\\lim', flags=re.IGNORECASE)
