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
    'VERS' : 'VERS',
    'WRAP' : 'WRAP',
    }

tokens = [
    'SPECIAL1',
    'SPECIAL2',
    'UNIT',
    'WORD',
    'DATA',
    ] + list(reserved.values())

def LasLexer():

    def t_SPECIAL2(t):
        r'[:]|[.]|VERS|WRAP'
        t.type = reserved.get(t.value)
        return t
    
    def t_UNIT(t):
        r'(?<=.)[^\n:. ]+'
        t.type = "UNIT"
        return t

    def t_DATA(t):
        '(?<!\A)[^\n]+(?=[:])'
        t.value = t.value.strip()
        return t
    
    def t_SPECIAL1(t):
        r'(~A[^\n ]*)|(~W[^\n ]*)|(~P[^\n ]*)|(~V[^\n ]*)|(~C[^\n ]*)'
        t.type = reserved.get(t.value[:2])
        return t

    def t_WORD(t):
        r'[^\n:. ]+'
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

def LasParser(start):
    def p_las_file(p):
        'las_file : version_header well_header curve_header parameter_header data'
        version_header = p[1]
        well_header = p[2]
        curve_header = p[3]
        parameter_header = p[4]
        data = p[5]
        p[0] = LasFile(version_header, well_header, curve_header,
                       paramater_header, subdivide(data, len(curve_header.descriptors)))

    def p_version_header(p):
        "version_header : VERSION_START words version wrap"
        p[0] = VersionHeader(p[3], p[4])    

    def p_well_header(p):
        "well_header : WELL_START descriptors"
        p[0] = WellHeader(p[2])

    def p_curve_header(p):
        "curve_header : CURVE_START descriptors"
        p[0] = VersionHeader(p[2])

    def p_parameter_header(p):
        "parameter_header : PARAMETER_START descriptors"
        p[0] = ParameterHeader(p[2])
        
    def p_version(p):
        "version : VERS DOT DATA COLON"
        p[0] = p[3]

    def p_wrap(p):
        "wrap : WRAP DOT WORD COLON"
        p[0] = p[3]
    
    def p_words(p):
        "words : words WORD"
        p[0] = " ".join(p[1]) + p[2]
    
    def p_words_empty(p):
        "words : empty"
        p[0] = ""
        
    def p_descriptors(p):
        "descriptors : descriptors descriptor"
        p[0] = p[1] + [p[2]]
    
    def p_descriptors_empty(p):
        "descriptors : empty"
        p[0] = []
    
    def p_descriptor1(p):
        "descriptor : WORD UNIT desc_data COLON description"
        mnemonic = p[1]
        unit = p[2]
        data = p[3]
        description = p[5]
        p[0] = Descriptor(mnemonic, unit, data, description)
        print p[0]

    def p_descriptor2(p):
        "descriptor : WORD DOT desc_data COLON description"
        mnemonic = p[1]
        data = p[3]
        description = p[5]
        p[0] = Descriptor(mnemonic = mnemonic,
                          data = data,
                          description = description)
                          
    def p_unit(p):
        '''unit : WORD 
                | empty'''
        p[0] = p[1]
    
    def p_desc_data_word(p):
        'desc_data : desc_data WORD'
        p[0] = p[1] + " " + p[2]
    
    def p_desc_data_num(p):
        'desc_data : desc_data DATA'
        p[0] = p[1] + " " + p[2]

    def p_desc_data_colon(p):
        'desc_data : desc_data COLON'
        p[0] = p[1] + p[2]

    def p_desc_data_empty(p):
        'desc_data : empty'
        p[0] = ""
    
    def p_description(p):
        '''description : WORD 
                       | empty'''
        p[0] = p[1]

    def p_data(p):
        "data : DATA_START words"
        p[0] = p[2]
    
    def p_empty(p):
        "empty :"
        pass
    
    def p_error(p):
        print p
        print "Illegal thing '%s'" % p.value
        print "of type = %s " % p.type
        print "at line %s " % p.lineno
        print p.lexpos
        raise "explosion"

    lexer = LasLexer()
    return yacc.yacc(start=start)
