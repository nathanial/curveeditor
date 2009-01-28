from __future__ import with_statement
import parser
import las

def read_lasfile(path):
    las_text = ""
    with open(path) as f:
        for line in f:
            las_text += line        
    return parser.parse("las_file", las_text)
