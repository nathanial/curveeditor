from las import VersionHeader, CurveHeader, Descriptor, LasFile, LasData

%%
parser LASParser:
    ignore: ' '
    token MNEMONIC: "\\w+"
    token UNIT: "(\\w|[/])*"
    token DESCRIPTION: "\\w*"
    token STRING: "\\w*"
    token NUM: '-?[0-9]+'
    token FLOAT: '-?[0-9]+[.][0-9]+'
    token EMPTY: ""

    rule las_file: version_header curve_header las_data {{ return LasFile(version_header, curve_header, LasData.split(las_data, curve_header)) }}
    
    rule version_header: end_line*
    	 	        "~V" STRING (" " STRING)* end_line
			"VERS." number ":" {{ vers = number }} end_line
			"WRAP." STRING ":" {{ wrap = STRING }} end_line
			{{ return VersionHeader(vers,wrap) }}

    rule curve_header: end_line* 
    	 	       "~C" STRING end_line {{ descriptors = [] }}
    	 	       (descriptor {{ descriptors.append(descriptor) }} end_line)*
		       {{ return CurveHeader(descriptors) }}
   
    rule descriptor: MNEMONIC "\." UNIT ":" DESCRIPTION
    	 	     {{ return Descriptor(MNEMONIC, UNIT, DESCRIPTION) }}

    rule las_data: end_line*
    	 	   "~A" STRING end_line {{data = []}}
		   (row {{data.extend(row)}} (end_line?) )*
		   EMPTY
		   {{ return data }}

    rule row: {{columns = []}}
    	      (number {{columns.append(number)}})+
	      {{ return columns }}	      

    rule number: NUM {{ return eval(NUM) }} |
		 FLOAT {{ return eval(FLOAT) }}
    
    rule end_line: "\n"
