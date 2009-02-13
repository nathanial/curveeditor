import ply.lex as lex
from util import subdivide
from las.file import *
from las.headers import *

reserved = {
    ':' : 'COLON',
    '.' : 'DOT',
    '~A' : 'DATA_START',
    '~W' : 'WELL_START',
    '~P' : 'PARAMETER_START',
    '~V' : 'VERSION_START',
    '~C' : 'CURVE_START',
}

tokens = [
    'SPECIAL',
    'WORD',
    'NUMBER',
    'VERS',
    'WRAP',
    ] + list(reserved.values())

def LasLexer():
    t_WORD = r'[^\n:. ]+'
    t_VERS = r'VERS'
    t_WRAP = r'WRAP'
    
    def t_SPECIAL(t):
        r'[:]|[.]|(~A[^\n ]*)|~W[^\n ]*|~P[^\n ]*|~V[^\n ]*|~C[^\n ]*'
        t.type = reserved.get(t.value[:2])
        return t
    
    def t_NUMBER(t):
        r'-?\d+([.]\d+)?'
        t.value = float(t.value)
        return t
    
    def t_newline(t):
        r'\n+'
        t.lexer.lineno += len(t.value)
    
    t_ignore = ' \t'
    
    def t_error(t):
        print "Illegal character '%s'" % t.value[0]
        t.lexer.skip(1)
    
    return lex.lex()

import ply.yacc as yacc

def p_las_file(p):
    'las_file : version_header well_header curve_header parameter_header data'
    version_header = p[1]
    well_header = p[2]
    curve_header = p[3]
    parameter_header = p[4]
    data = p[5]
    p[0] = LasFile(version_header, well_header, curve_header,
                   paramater_header, subdivide(data, len(curve_header.descriptors)))

def p_well_header(p):
    "well_header : WELL_START descriptors"
    p[0] = WellHeader(p[2])

def p_parameter_header(p):
    "parameter_header : PARAMETER_START descriptors"
    p[0] = ParameterHeader(p[2])

def p_version_header(p):
    "version_header : VERSION_START version wrap"
    p[0] = VersionHeader(p[2], p[3])

def p_version(p):
    "version : VERS DOT words"
    p[0] = p[2]

def p_words(p):
    "words : words WORD"
    p[0] = " ".join(p[1]) + p[2]

def p_words_empty(p):
    "words : empty"
    p[0] = ""
    
def p_wrap(p):
    "wrap : WRAP DOT words"
    p[0] = p[2]

def p_curve_header(p):
    "curve_header : CURVE_START descriptors"
    p[0] = VersionHeader(p[2])

def p_descriptors(p):
    "descriptors : descriptors descriptor"
    p[0] = p[1] + [p[2]]

def p_descriptors_empty(p):
    "descriptors : empty"
    p[0] = []

def p_descriptor(p):
    "descriptor : WORD DOT WORD WORD COLON WORD"
    p[0] = Descriptor(mnemonic = p[1], 
                      unit = p[3],
                      data = p[4],
                      description = p[6])

def p_data(p):
    "data : DATA_START numbers"
    p[0] = p[2]

def p_numbers(p):
    "numbers : numbers NUMBER"
    p[0] = p[1] + [p[2]]

def p_numbers_empty(p):
    "numbers : empty"
    p[0] = []

def p_empty(p):
    "empty :"
    pass

def p_error(p):
    print "Illegal thing '%s'" % p.value
    raise "explosion"
                      
parser = yacc.yacc()
