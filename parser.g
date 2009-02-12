from las.file import *
from las.headers import *
from util import subdivide

%%
parser LASParser:
    ignore: ' '
    ignore: "#[^\n]*\n"
    token MNEMONIC: "\\w+"
    token UNIT: "[.][^\n:. ]*"
    token DESCRIPTION: ":[^\n:]*"
    token STRING: ".*"
    token LINE: "[^\n]*"
    token DELIMITER_FREE_STRING: "[^\n:.]*"
    token COLON_FREE_STRING: "[^\n:]*"
    token NUM: '-?[0-9]+'
    token FLOAT: '-?[0-9]+[.][0-9]+'
    token EMPTY: ""
    token DATA: "[^\n]*(?= :[^\n:]*)"

    rule las_file: version_header well_header curve_header parameter_header data_rows 
    	 	   {{ return LasFile(version_header, well_header, curve_header, parameter_header, subdivide(data_rows, len(curve_header.descriptors))) }}

    rule well_header: space* 
    	 	      "~W" LINE end_line {{ descriptors = [] }}
		      (descriptor {{ descriptors.append(descriptor) }} end_line)*
		      {{ return WellHeader(descriptors) }}

    rule parameter_header: space*
    	 		   "~P" LINE end_line {{ descriptors = [] }}
			   (descriptor {{ descriptors.append(descriptor) }} end_line)*
			   {{ return ParameterHeader(descriptors) }}		      

    
    rule version_header: space*
    	 	        "~V" LINE end_line
			"VERS." number ":" {{ vers = number }} end_line
			"WRAP." COLON_FREE_STRING ":" {{ wrap = COLON_FREE_STRING }} end_line
			{{ return VersionHeader(vers,wrap) }}

    rule curve_header: space* 
    	 	       "~C" LINE end_line {{ descriptors = [] }}
    	 	       (descriptor {{ descriptors.append(descriptor) }} end_line)*
		       {{ return CurveHeader(descriptors) }}
   
    rule descriptor: MNEMONIC UNIT DATA DESCRIPTION 
    	 	     {{ return Descriptor(MNEMONIC, UNIT[1:], DATA, DESCRIPTION[1:].strip()) }}

    rule data_rows: space*
    	 	   "~A" LINE end_line {{data = []}}
		   (row {{data.extend(row)}} (end_line?) )*
		   space
		   {{ return data }}

    rule row: {{columns = []}}
    	      (number {{columns.append(number)}})+
	      {{ return columns }}	      

    rule number: NUM {{ return eval(NUM) }} |
		 FLOAT {{ return eval(FLOAT) }}
    
    rule end_line: "\n\r" | "\n" | "\r\n" | "\r"

    rule space: end_line | EMPTY
