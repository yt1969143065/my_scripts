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

#============================================================================================
def parse_file (f):
#============================================================================================
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


          
#============================================================================================
def print_component (f, entity, generics, others, ins, outs, core):
#============================================================================================
	if core < 1:
		"""print the component declaration for the entity"""
		#print(r'''  COMPONENT {entity} IS '''.format(entity=entity), file=f)
		if generics:
			print(r'''  GENERIC(''', file=f)
			for name, type, value in generics[:-1]:
				print('    {name:<44} : {type:<44} := {value}'.format(name=name, type=type, value=value), file=f)
			print('    {name:<44} : {type:<44} := {value}'.format(name=generics[-1][0], type=generics[-1][1], value=generics[-1][2]), file=f)
			print(r'''  );''', file=f)
		print(r'''  PORT(''', file=f)
		for name, type in others:
			print('    {name:<44} : IN {type:<44};'.format(name=name, type=type), file=f)
		for name, type in ins:
			print('    {name:<44} : IN {type:<44};'.format(name=name, type=type), file=f)
		for name, type in outs[:-1]:
			print('    {name:<44} : IN {type:<44};'.format(name=name, type=type), file=f)
		print('    {name:<44} : IN {type:<44}'.format(name=outs[-1][0], type=outs[-1][1]), file=f)
		print(r'''    );
  END COMPONENT {entity};
'''.format(entity=entity), file=f)

        
#============================================================================================
def print_instance (f, entity, generics, others, ins, outs, new_ins, new_outs, core):
#============================================================================================
	"""Print an instance for the entity, binding others/ins/outs to identically named signals"""
	if core >= 0:
		label = entity + str(core)
	else:
		label = entity
	
	print(r'''a_{label} : {entity}'''.format(label=label, entity=entity), file=f)
	if generics:
		print(r'''GENERIC_MAP(''', file=f)
		for name, type, value in generics[:-1]:
			print('  {name:<44} => {name};'.format(name=name), file=f)
		print('  {name:<44} => {name}'.format(name=generics[-1][0]), file=f)
		print(r'  );''', file=f)
	print('''PORT_MAP(''', file=f)
	for name, _ in others:
		print('    {name:<44} => {name},'.format(name=name), file=f)
	i = 0
	for name, _ in ins:
		print('    {name:<44} => {new},'.format(name=name, new=new_ins[i]), file=f)
		i = i + 1
	i = 0
	for name, _ in outs[:-1]:
		print('    {name:<44} => {new},'.format(name=name, new=new_outs[i]), file=f)
		i = i + 1
	print(r'''    {name:<44} => {new}
  );'''.format(name=outs[-1][0], new=new_outs[i]), file=f)


#============================================================================================
def print_top (f, entity_top, entities, components):
#============================================================================================
	sub_port_match = re.compile('(\w+)_([a-zA-Z0-9]+)_([a-zA-Z0-9]+)$')
	top_port_match = re.compile('(\w+)_([a-zA-Z0-9]+)_([a-zA-Z0-9]+)_([a-zA-Z0-9]+)$')
	c_name_match   = re.compile('(\w+)_unit\w*\s*$')
	gen_name_match = re.compile('(\w+)_unit_top\s*$')
	
	sub_units = []
	for _, c, generics, _, ins, outs in components:
		c_name = c_name_match.match(c)
		if c_name is not None:
			c_name = c_name.group(1)
		else:
			c_name = ""
		
		#add core number 
		if c_name == "dsp":
			core = "0"
		elif c_name == "mcu":
			core = "1"
		else:
			core = ""
		
		gen = False
		gen_name = gen_name_match.match(c)
		if gen_name is not None:
			gen = True
		
		if gen:
			for name, _ in ins:
				units = top_port_match(name)
				if units is not None:
					dest_unit = units.group(3) + core
					if dest_unit not in sub_units:
						sub_units.append(dest_unit)
				else:
					print(r'''{c_name} have an illegal port: {name} !!!'''.format(c_name=c, name=name))
					sys.exit(1)
			for name, _ in outs:
				units = top_port_match(name)
				if units is not None:
					source_unit = units.group(2) + core
					if source_unit not in sub_units:
						sub_units.append(source_unit)
				else:
					print(r'''{c_name} have an illegal port: {name} !!!'''.format(c_name=c, name=name))
					sys.exit(1)
		else:
			sub_units.append(c_name)
	
	top_ins  = []
	top_outs = []
	sig_ins  = []
	sig_bufs = []
	i = 0
	
	for _, c, generics, _, ins, outs in components:
		new_ins  = []
		new_outs = []
		
		c_name = c_name_match.match(c)
		if c_name is not None:
			c_name = c_name.group(1)
		else:
			c_name = ""
			
		#add core number 
		if c_name == "dsp":
			core = "0"
		elif c_name == "mcu":
			core = "1"
		else:
			core = ""
		
		gen = False
		gen_name = gen_name_match.match(c)
		if gen_name is not None:
			gen = True
		
		if gen:
			for name, type in ins:
				new_name = name
				units = top_port_match.match(name)
				if units is not None:
					prefix      = units.group(1)
					source_unit = units.group(2)
					dest_unit   = units.group(3)
					suffix      = units.group(4)
					if source_unit not in sub_units:
						new_name = prefix + "_" + source_unit + "_" + dest_unit + core + "_" + suffix
						top_ins.append([new_name, type])
					else:
						new_name = prefix + "_" + source_unit + "_" + dest_unit + core
						if new_name not in [i[0] for i in sig_ins]:
							sign_ins.append([new_name, type])
						
						buf_pos = prefix.find("_buf")
						if buf_pos > -1:
							o_name = prefix[0:buf_pos] + "_" + source_unit + "_" + dest_unit
							sign_bufs.append([o_name, new_name])
				else:
					print(r"erro auto-top input port of {c}: {name}".format(c=c, name=name))
				new_ins.append(new_name)
					
			for name, type in outs:
				new_name = name
				units = top_port_match.match(name)
				if units is not None:
					prefix      = units.group(1)
					source_unit = units.group(2)
					dest_unit   = units.group(3)
					suffix      = units.group(4)
					if dest_unit not in sub_units:
						new_name = prefix + "_" + source_unit + core + "_" + dest_unit + "_" + suffix
						top_outs.append([new_name, type])
					else:
						new_name = prefix + "_" + source_unit + "_" + core + dest_unit
						if new_name not in [i[0] for i in sig_ins]:
							sign_ins.append([new_name, type])
						
					print(r"erro auto-top output port of {c}: {name}".format(c=c, name=name))
				new_outs.append(new_name)
					
			components[i].append(new_ins)
			components[i].append(new_outs)
			i = i + 1
				
		else:
			for name, type in ins:
				new_name = name
				units = sub_port_match.match(name)
				if units is not None:
					prefix      = units.group(1)
					source_unit = units.group(2)
					dest_unit   = c_name
					suffix      = units.group(4)
					if source_unit not in sub_units:
						new_name = prefix + "_" + source_unit + "_" + dest_unit + "_" + suffix
						top_ins.append([new_name, type])
					else:
						new_name = prefix + "_" + source_unit + "_" + dest_unit
						if new_name not in [i[0] for i in sig_ins]:
							sign_ins.append([new_name, type])
						
						buf_pos = prefix.find("_buf")
						if buf_pos > -1:
							o_name = prefix[0:buf_pos] + "_" + source_unit + "_" + dest_unit
							sign_bufs.append([o_name, new_name])
				else:
					print(r"erro subunit input port of {c}: {name}".format(c=c, name=name))
				new_ins.append(new_name)
					
			for name, type in outs:
				new_name = name
				units = sub_port_match.match(name)
				if units is not None:
					prefix      = units.group(1)
					source_unit = c_name
					dest_unit   = units.group(3)
					suffix      = units.group(4)
					if dest_unit not in sub_units:
						new_name = prefix + "_" + source_unit + "_" + dest_unit + "_" + suffix
						top_outs.append([new_name, type])
					else:
						new_name = prefix + "_" + source_unit + "_" + dest_unit
						if new_name not in [i[0] for i in sig_ins]:
							sign_ins.append([new_name, type])
				else:
					print(r"erro subunit output port of {c}: {name}".format(c=c, name=name))
				new_outs.append(new_name)
					
			components[i].append(new_ins)
			components[i].append(new_outs)
			i = i + 1
				
	"""generate a stylized top"""
	print(r'''
-------------------------------------------------------------------------------
-- Title   :
-- Project : 
-- Date    :{d} 
-------------------------------------------------------------------------------
--*************AUTO GEN FILE, DON'T MODIFY*************************************
'''.format(d=datetime.date.today), file=f)
	print(r'''
ENTITY {entity}_unit_top IS'''.format(entity=entity_top), file=f)
	print(r'''i
PORT(''', file=f)
	for name, type in components[0][3]:
		#restart only used in dsp/mcu inner
		if (entity_top == "dsp" or entity_top == "mcu") and name == "restart":
			continue
		print('  {name:<44} : IN  {type};'.format(name=name, type=type), file=f)
	for name, type in top_ins:
		print('  {name:<44} : IN  {type};'.format(name=name, type=type), file=f)
	for name, type in top_outs[:-1]:
		print('  {name:<44} : OUT {type};'.format(name=name, type=type), file=f)
	print('  {name:<44} : OUT {type}'.format(name=top_outs[-1][0], type=top_outs[-1][1]), file=f)
	print(r''');
 END ENTITY {entity}_unit_top;
'''.format(entity=entity_top), file=f)
	
	print(r'''
ARCHITECTURE behavior OF {entity}_unit_top IS'''.format(entity=entity_top), file=f)
	for _, component, generics, others, ins, outs, _, _ in components:
		print_component(f, component, generics, others, ins, outs, -1)
	for name, type in sig_ins:
		print('  SIGNAL {name:<24} : {type};'.format(name=name, type=type), file=f)
	print(r'''BEGIN''', file=f)
	if(len(sign_bufs) > 0):
		print(r'''  
  bufs : PROCESS(clock)
  BEGIN
    IF (rising_edge(clock)) THEN''', file=f)
		for bufs in sig_bufs:
			for i, b in enumerate(bufs):
				if i is 0:
					continue
				print(r'''    {b1} <= {b0} after 10 ps;'''.format(b1=b, b0=bufs[i-1]), file=f)
		print(r'''
    END IF;
  END PROCESS;''', file=f)
	for _, component, generics, others, ins, outs, new_ins, new_outs in components:
		print_insntance(f, component, generics, others, ins, outs, new_ins, new_outs, -1)
	print(r'''
END ARCHITECTURE behavior;''', file=f)



#============================================================================================
#>>>>>>>>>>>>>>>>>>>>>>    MAIN   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
#============================================================================================
argparser = optparse.OptionParser(
	usage = '%prog [OPTION]...[VHDL] [VHDL]',
	version = '%PROG 1.0',
	description = 'This program analyzes the input VHDL code and generate VHDL top.')

argparser.add_option('-o', '--output',
	dest = 'output', type = 'string', default = 'top_unit.vhd',
	help = 'output file for generated code.')

argparser.add_option('-t', '--type',
	dest = 'type', type = 'string', default = 'top',
	help = 'type of file to be generates.')

(options, filearg) = argparser.parse_args()

if (options.type not in [ 'top' ]):
	argparser.error("unkown output type" + options.type)
	sys.exit(1)

infs = []
if len(filearg) < 1:
	argparser.error("File input must be specified!")
	sys.exit(1)
else:
	for f in filearg:
		infs.append(open(f, "r"))

if options.output == None:
	outf = sys.stdout
else:
	outf = open(options.output, "w")

componnets = []
entities   = []

for inf in infs:
	[packages, entity, generics, others, ins, outs ] = parser_file(inf)
	
	e =entity;
	pos = e.find("_")
	entities.append(e[0:pos])
	
	components.append([packages, entity, generics, others, ins, outs])

entities.sort(key=len, reverse=True)

top_entity = os.path.basename(options.output)
comp_name_match = re.compile('(\w+)_unit(\w+)\.vhd$')
top_entity = comp_name_match.match(top_entity)

if top_entity is not None:
	top_entity = top_entity.group(1)
else:
	top_entity = ""

print_top(outf, top_entity, entities, components)




