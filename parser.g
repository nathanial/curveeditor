from las.file import *
from las.headers import *

%%
parser LASParser:
    ignore: ' '
    ignore: "#[^\n]*\n"
    token MNEMONIC: "\\w+"
    token UNIT: "[^\n:. ]*"
    token DESCRIPTION: "[^\n]*"
    token STRING: ".*"
    token LINE: "[^\n]*"
    token DELIMITER_FREE_STRING: "[^\n:.]*"
    token COLON_FREE_STRING: "[^\n:]*"
    token NUM: '-?[0-9]+'
    token FLOAT: '-?[0-9]+[.][0-9]+'
    token EMPTY: ""
    token DATA: "[^\n:]*"

    rule las_file: version_header well_header curve_header parameter_header las_data 
    	 	   {{ return LasFile(version_header, well_header, curve_header, parameter_header, LasData.split(las_data, curve_header)) }}

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
   
    rule descriptor: MNEMONIC "\." UNIT DATA ":" DESCRIPTION 
    	 	     {{ return Descriptor(MNEMONIC, UNIT, DATA, DESCRIPTION.strip()) }}

    rule las_data: space*
    	 	   "~A" LINE end_line {{data = []}}
		   (row {{data.extend(row)}} (end_line?) )*
		   EMPTY
		   {{ return data }}

    rule row: {{columns = []}}
    	      (number {{columns.append(number)}})+
	      {{ return columns }}	      

    rule number: NUM {{ return eval(NUM) }} |
		 FLOAT {{ return eval(FLOAT) }}
    
    rule end_line: "\n"

    rule space: end_line | EMPTY
