from las.file import *
from las.headers import *
from util import subdivide

%%
parser LASParser:
    ignore: "( |[#][^\n\r]*)"
    token ENDLINE: "(\n\r)|\n|(\r\n)|\r"
    token MNEMONIC: "[^.]+"
    token DESCRIPTION: "[^\n\r:]+"
    token STRING: ".*"
    token LINE: "[^\n\r]*"
    token DELIMITER_FREE_STRING: "[^\n\r:.]*"
    token COLON_FREE_STRING: "[^\n:]*"
    token NUM: '-?[0-9]+'
    token FLOAT: '-?[0-9]+[.][0-9]+'
    token EMPTY: ""
    token DATA: "[^\n\r]+(?= :[^\n\r:]*)"

    rule las_file: version_header well_header curve_header parameter_header data_rows 
    	 	   {{ return LasFile(version_header, well_header, curve_header, parameter_header, subdivide(data_rows, len(curve_header.descriptors))) }}

    rule well_header: space* 
    	 	      "~W" LINE ENDLINE {{ descriptors = [] }}
		      (descriptor {{ descriptors.append(descriptor) }} ENDLINE)*
		      {{ return WellHeader(descriptors) }}

    rule parameter_header: space*
    	 		   "~P" LINE ENDLINE {{ descriptors = [] }}
			   (descriptor {{ descriptors.append(descriptor) }} ENDLINE)*
			   {{ return ParameterHeader(descriptors) }}		      
    
    rule version_header: space*
    	 	        "~V" LINE ENDLINE
			"VERS." number ":" {{ vers = number }} ENDLINE
			"WRAP." COLON_FREE_STRING ":" {{ wrap = COLON_FREE_STRING }} ENDLINE
			{{ return VersionHeader(vers,wrap) }}

    rule curve_header: space* 
    	 	       "~C" LINE ENDLINE {{ descriptors = [] }}
    	 	       (descriptor {{ descriptors.append(descriptor) }} ENDLINE)*
		       {{ return CurveHeader(descriptors) }}
   
    rule descriptor: MNEMONIC "." {{ unit = None}} {{ data = None }} 
    	 	     (UNIT {{unit = UNIT}})?
		     (DATA {{data = DATA}})? ":" DESCRIPTION 
    	 	     {{ print "pmnemonic = %s " % MNEMONIC, }}
		     {{ print "punit = %s " % unit, }}
		     {{ print "pdata = %s " % data, }}
		     {{ print "pdescription = %s" % DESCRIPTION }}
    	 	     {{ return Descriptor(MNEMONIC, unit, data, DESCRIPTION.strip()) }}

    rule data_rows: space*
    	 	   "~A" LINE ENDLINE {{data = []}}
		   (number {{data.append(number)}} (ENDLINE?) )*
		   space
		   {{ return data }}

    rule number: NUM {{ return eval(NUM) }} |
		 FLOAT {{ return eval(FLOAT) }}
    

    rule space: ENDLINE | EMPTY
