import sys
import collections
import re
import optparse
import os.path
import copy
import datetime

type_dic = {
'op_type' : 'std_logic_vector(11 downto 0)',
'bp_type' : 'std_logic_vector( 1 downto 0)'
}

#========================================================
def parse_file (f):
#========================================================
	"""Parse the first ENTITY declaration in an input file, breaking it into
	-  The name of the entity
	-  All IN  ports that do not have the suffix _in
	-  All IN  ports that have the suffix _in
	-  ALL OUT ports that have the suffix _out
	"""

	entity   = None
	packages = []
	generics = []
	others   = []
	ins      = []
	outs     = []

	sm = 0  
	generic_map =  False

	for line in f:
		if sm == 0:
			m = re.match("\s*USE\s+(work\.\w+)\s*;", line, flags=re.IGNORECASE)
			if m is not None:
				packages.append(m.group(1))
		if sm == 0: 
			m = re.match("\s*entity\s+(\w+)\s+", line, flags=re.IGNORECASE)
			if m is not None:
				entity = m.group(1)
				sm = 1
		elif sm == 1:
			m = re.match("\s*end\s+entity", line, flags=re.IGNORECASE)
			if m is not None:
				break
			m = re.match("\s*generic\s*", line, flags=re.IGNORECASE)
			if m is not None:
				generic_map = True
				continue
			if generic_map:
				m = re.match("\s*(\w+)\s*:\s*(\w+)\s*\:=\s*(\w+)\s*", line, flags=re.IGNORECASE)
				if m is not None:
					generics.append([m.group(1), m.group(2), m.group(3)])
					continue
				m = re.match("\s*\);\s*", line, flags=re.IGNORECASE)
				if m is not None:
					generic_map = False
					continue
			else:
				m = re.match("\s*(\w+)\s*:\s+in\s+([0-9, a-z, A-Z, (, ), _]+)", line, flags=re.IGNORECASE)
				if m is not None:
					name = m.group(1)
					type = m.group(2)
					#----change port to standard-------------------------------
					m = re.match("bit_type", type, flags=re.IGNORECASE)
					if m is not None:
						high = 0
						type = 'std_logic_vector('+str(high)+'downto 0)'
					m = re.match("", type, flags=re.IGNORECASE)
					if m is not None:
						high = int(m.group(1))-1
						type = 'std_logic_vector('+str(high)+'downto 0)'
					if type in type_dic:
						type = type_dic[type]
					#-----------------------------------------------------------
					others.append([name, type])
					continue
				m = re.match("\s*(\w+)_in\s*:\s+in\s+([0-9, a-z, A-Z, (, ), _]+)", line, flags=re.IGNORECASE)
				if m is not None:
					name = m.group(1)
					type = m.group(2)
					#----change port to standard-------------------------------
					m = re.match("bit_type", type, flags=re.IGNORECASE)
					if m is not None:
						high = 0
						type = 'std_logic_vector('+str(high)+'downto 0)'
					m = re.match("", type, flags=re.IGNORECASE)
					if m is not None:
						high = int(m.group(1))-1
						type = 'std_logic_vector('+str(high)+'downto 0)'
					if type in type_dic:
						type = type_dic[type]
					#-----------------------------------------------------------
					ins.append([name, type])
					continue
				m = re.match("\s*(\w+)_...out\s*:\s+in\s+([0-9, a-z, A-Z, (, ), _]+)", line, flags=re.IGNORECASE)
				if m is not None:
					name = m.group(1)
					type = m.group(2)
					#----change port to standard-------------------------------
					m = re.match("bit_type", type, flags=re.IGNORECASE)
					if m is not None:
						high = 0
						type = 'std_logic_vector('+str(high)+'downto 0)'
					m = re.match("", type, flags=re.IGNORECASE)
					if m is not None:
						high = int(m.group(1))-1
						type = 'std_logic_vector('+str(high)+'downto 0)'
					if type in type_dic:
						type = type_dic[type]
					#-----------------------------------------------------------
					outs.append([name, type])
					continue

	return[packages, entity, generics, others, ins, outs];


          
        
                                
