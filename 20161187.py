import sys
from moz_sql_parser import parse
# table doesnt exist exit
# incorrect agg func

class Table:
	def __init__(self, name, metadata, data, parents):
		self.name = name
		self.columns = metadata
		self.data = data
		self.parents = parents

def sqlparse(string):
	if ';' not in string:
		print("No ; in statement")
		exit()
	else:
		string = string.strip(";")
	try:
		parsed = parse(string)
	except:
		print("Invalid Query")
		exit()
	if 'from' not in parsed:
		print("no 'from' keyword in query")
		exit()
	return parsed

def cartesian_product(table1,table2):
	columns = table1.columns+table2.columns
	data = []
	for i in table1.data:
		for j in table2.data:
			data.append(i+j)
	parents = table1.parents+table2.parents
	table3 = Table("Child", columns, data, parents)
	return table3

def file_parser(file):
	try:
		metafile = "metadata.txt"
		filename = file + ".csv"
		flag = 0
		metadata = []
		meta = open(metafile, "r")
		for lines in meta:
			line = lines.strip()
			if line == "<end_table>" and flag==1:
				break
			if flag == 1:
				metadata.append(line)
			if line == file:
				flag = 1
		if flag == 0:
			print("Table does not exist")
			# meta.close()
			# exit()
			sys.exit()
			print("gay")

		data = []
		datafile = open(filename, "r")
		for line in datafile:
			parsed = line.strip().split(',')
			parsed_line = [int(i) for i in parsed]
			data.append(parsed_line)
		columns = [file + "." + i for i in metadata]
		table = Table(file,columns,data,1)
		return table
	except:
		print("Error in opening files")
		exit()

def transform(P_columns, columns):
	count = [0]*len(P_columns)
	new_columns = []
	for i in range(0,len(P_columns)):
		item = P_columns[i]
		if len(item.split("."))>1:
			new_columns.append(item)
			count[i]=1
			continue
		for j in columns:
			if j.split('.')[1] == item:
				new_columns.append(j)
				count[i]+=1
	for i in range(0,len(count)):
		if count[i] >1:
			print("Column " + P_columns[i] + " is ambiguous")
			exit()
	for i in count:
		if i == 0:
			print("Column not found")
			exit(0)
	return new_columns

def transform_single(val,columns):
	value = transform([val],columns)
	return value[0]


def from_parser(parsed_query_dict):
	if isinstance(parsed_query_dict['from'], str):
		# print("yes")
		# exit()
		file = parsed_query_dict['from']
		table = file_parser(file)
		return table
	else:
		tablenames = parsed_query_dict['from']
		table_list = [file_parser(i) for i in tablenames]
		product = table_list[0]
		for i in range(1, len(table_list)):
			product = cartesian_product(product, table_list[i])
		return product

def delete_row(table1, index):
	columns = []
	for i in range(0,len(table1.columns)):
		if i!=index:
			columns.append(table1.columns[i])

	data = []
	for i in table1.data:
		row = []
		for j in range(0, len(i)):
			if j!=index:
				row.append(i[j])
		data.append(row)
	table2 = Table("final", columns, data, table1.parents)
	return table2

def check_cond(cond, op1,op2, columns, row):
	if isinstance(op1,str):
		op1 = transform_single(op1,columns)
		# print("check")
		try:
			index1 = columns.index(op1)
		except:
			print("Column"+op1+" can't be found")
		# print(index1)
		val1 = row[index1]
	else:
		val1 = op1
	if isinstance(op2,str):
		# print("check")
		op2 = transform_single(op2,columns)
		try:
			index2 = columns.index(op2)
		except:
			print("Column"+op2+" can't be found")
		# print(index1)
		val2 = row[index2]
	else:
		val2 = op2
	# print(val1,val2)
	if cond == "eq":
		return val1 == val2
	if cond == "gt":
		return val1>val2
	if cond == "gte":
		return val1>=val2
	if cond == "lt":
		return val1<val2
	if cond == "lte":
		return val1<=val2



def where_parser(table1, parsed_query_dict):
	if 'where' not in parsed_query_dict:
		return table1
	if 'eq' in parsed_query_dict['where'] and isinstance(parsed_query_dict['where']['eq'][0], str) and isinstance(parsed_query_dict['where']['eq'][1], str):
		index1 = -1
		index2 = -1
		P_column1 = parsed_query_dict['where']['eq'][0]
		P_column2 = parsed_query_dict['where']['eq'][1]
		# print(P_column1,P_column2)
		columns = table1.columns
		P_column1 = transform_single(P_column1, columns)
		P_column2 = transform_single(P_column2, columns)
		for i in range(0,len(columns)):
			column = columns[i]
			if P_column1==column:
				index1=i
			if P_column2==column:
				index2=i
		if index1==-1 or index2==-1:
			print("columns in 'where' condition cannot be found")
			exit()
		new_data = []
		for i in table1.data:
			if i[index1]==i[index2]:
				new_data.append(i)
		table2 = Table("One."+ str(index2), columns, new_data, table1.parents)
		# table3 = delete_row(table2, index2)
		return table2

	if 'and' not in parsed_query_dict['where'] and 'or' not in parsed_query_dict['where']:
		where_dict = parsed_query_dict['where']
		for key,value in where_dict.items():
			cond = key
			val = value
		data = []

		for i in table1.data:
			if check_cond(cond,val[0],val[1], table1.columns,i):
				data.append(i)
		table2 = Table("blech",table1.columns, data, table1.parents)
		return table2
		# print(cond)
		# print(val)

	if 'and' in parsed_query_dict['where']:
		where_dict = parsed_query_dict['where']['and']
		part1 = where_dict[0]
		part2 = where_dict[1]
		for key,val in part1.items():
			cond1 = key
			val1 = val 
		for key,val in part2.items():
			cond2 = key
			val2 = val
		data = []
		for i in table1.data:
			if check_cond(cond1,val1[0],val1[1], table1.columns,i) and check_cond(cond2,val2[0],val2[1], table1.columns,i):
				data.append(i)
		table2 = Table("blech",table1.columns, data, table1.parents)
		return table2

	if 'or' in parsed_query_dict['where']:
		where_dict = parsed_query_dict['where']['or']
		part1 = where_dict[0]
		part2 = where_dict[1]
		for key,val in part1.items():
			cond1 = key
			val1 = val 
		for key,val in part2.items():
			cond2 = key
			val2 = val
		data = []
		for i in table1.data:
			if check_cond(cond1,val1[0],val1[1], table1.columns,i) or check_cond(cond2,val2[0],val2[1], table1.columns,i):
				data.append(i)
		table2 = Table("blech",table1.columns, data, table1.parents)
		return table2


def select_parser(table1, parsed_query_dict):
	select_dict = parsed_query_dict['select']
	# print(select_dict['value'])
	columns = []
	data = []
	if select_dict == '*':
		name_parse = table1.name.split(".")
		if len(name_parse)>1:
			table2 = delete_row(table1, int(name_parse[1]))
			return table2
		return table1
		# columns = [table1.name + "." + i for i in table1.columns]
		# data = table1.data
		# final_table = Table("Final", columns, data)
		# return final_table
	if len(select_dict) == 1 and 'max' in select_dict['value']:
		val = select_dict['value']['max']
		if len(val.split(".")) == 1:
			val = table1.name+"."+val
		index = -1
		for i in range(0, len(table1.columns)): 
			column = table1.columns[i]
			if column == val:
				index = i
				break
		if index == -1:
			print("column doesn't exist in table")
			exit()
		values = [i[index] for i in table1.data]
		data = [[max(values)]]
		val = "max("+ val+")"
		columns = [val]
		final_table = Table("final", columns, data,1)
		return final_table

	if len(select_dict) == 1 and 'min' in select_dict['value']:
		val = select_dict['value']['min']
		if len(val.split(".")) == 1:
			val = table1.name+"."+val
		index = -1
		for i in range(0, len(table1.columns)): 
			column = table1.columns[i]
			if column == val:
				index = i
				break
		if index == -1:
			print("column doesn't exist in table")
			exit()
		values = [i[index] for i in table1.data]
		data = [[min(values)]]
		val = "min("+ val+")"
		columns = [val]
		final_table = Table("final", columns, data,1)
		return final_table

	if len(select_dict) == 1 and 'sum' in select_dict['value']:
		val = select_dict['value']['sum']
		if len(val.split(".")) == 1:
			val = table1.name+"."+val
		index = -1
		for i in range(0, len(table1.columns)): 
			column = table1.columns[i]
			if column == val:
				index = i
				break
		if index == -1:
			print("column doesn't exist in table")
			exit()
		values = [i[index] for i in table1.data]
		data = [[sum(values)]]
		val = "sum("+ val+")"
		columns = [val]
		final_table = Table("final", columns, data,1)
		return final_table

	if len(select_dict) == 1 and  'avg' in select_dict['value']:
		val = select_dict['value']['avg']
		if len(val.split(".")) == 1:
			val = table1.name+"."+val
		index = -1
		for i in range(0, len(table1.columns)): 
			column = table1.columns[i]
			if column == val:
				index = i
				break
		if index == -1:
			print("column doesn't exist in table")
			exit()
		values = [i[index] for i in table1.data]
		data = [[sum(values)/len(values)]]
		val = "avg("+ val+")"
		columns = [val]
		final_table = Table("final", columns, data,1)
		return final_table

	if len(select_dict) == 1 and 'value' in select_dict and 'distinct' in select_dict['value']:
		if select_dict['value']['distinct'] == '*':
			data = []
			for i in table1.data:
				if i not in data:
					data.append(i)
			table2=Table("blech",table1.columns, data, table1.parents)
			return table2
		# print("Check")
		index = -1
		val = select_dict['value']['distinct']
		P_columns = transform([val], table1.columns)
		# print(P_columns)
		val = P_columns[0]
		# if len(val.split(".")) == 1:
		# 	val = table1.name+"."+val

		for i in range(0, len(table1.columns)): 
			column = table1.columns[i]
			if column == val:
				index = i
				break
		if index == -1:
			print("column doesn't exist in table")
			exit()
		columns = [val]
		row = []
		# print(index)
		for i in table1.data:
			# print(i)
			row.append(i[index])
			data.append(row)
			row = []
		distinct_data = []
		for i in data:
			if i not in distinct_data:
				distinct_data.append(i)
		final_table = Table("final", columns, distinct_data,1)
		return final_table

	if len(select_dict) == 1 and 'value' in select_dict and not isinstance(select_dict['value'],str):
		print("Wrong aggregate")
		exit()

	if len(select_dict) == 1 and 'value' in select_dict:
		index = -1
		val = select_dict['value']
		P_columns = transform([val], table1.columns)
		# print(P_columns)
		val = P_columns[0]
		# print(val)
		# if len(val.split(".")) == 1:
		# 	val = table1.name+"."+val
		# 	print(val)
		for i in range(0, len(table1.columns)): 
			column = table1.columns[i]
			if column == val:
				index = i
				break
		if index == -1:
			print("column doesn't exist in table")
			exit()
		columns = [val]
		row = []
		# print(index)
		for i in table1.data:
			# print(i)
			row.append(i[index])
			data.append(row)
			row = []
		final_table = Table("final", columns, data,1)
		return final_table

	if len(select_dict) > 1 and 'value' in select_dict[0]  and 'distinct' in select_dict[0]['value']:
		# print("Check")
		# P_columns = [i['value'] for i in select_dict]
		P_columns = []
		for i in select_dict:
			if 'distinct' in i['value']:
				P_columns.append(i['value']['distinct'])
			else:
				P_columns.append(i['value'])
		# print(P_columns)
		checklist = []
		if table1.parents == 1:
			# for i in P_columns:
			# 	if len(i.split(".")) == 1:
			# 		checklist.append(table1.name+"."+ i)
			# 	else:
			# 		checklist.append(i)
			# P_columns = checklist
			P_columns = transform(P_columns,table1.columns)
		else:
			P_columns = transform(P_columns,table1.columns)
		# 		print("")
		# P_columns = [table1.name+"."+ i for i in P_columns]
		index = [-1] * len (P_columns)
		for j in range(0,len(P_columns)):
			P_column = P_columns[j]
			for i in range(0, len(table1.columns)):
				column = table1.columns[i]
				if P_column == column:
					index[j] = i
					break
		for i in index:
			if i == -1:
				print("One or more of the columns not in the table")
				exit()
		row = []
		for i in table1.data:
			row = [i[x] for x in index]
			data.append(row)
			row = []
		distinct_data = []
		for i in data:
			if i not in distinct_data:
				distinct_data.append(i)
		final_table = Table("final", P_columns, distinct_data,1)
		return final_table


	if len(select_dict) > 1 and 'value' in select_dict[0]  and 'distinct' not in select_dict[0]['value']:
		# print("Check")
		# print(table1.parents)
		P_columns = [i['value'] for i in select_dict]
		# print(P_columns)
		checklist = []
		if table1.parents == 1:
			# for i in P_columns:
			# 	if len(i.split(".")) == 1:
			# 		checklist.append(table1.name+"."+ i)
			# 	else:
			# 		checklist.append(i)
			# P_columns = checklist
			P_columns = transform(P_columns,table1.columns)
		
		else:
			P_columns = transform(P_columns,table1.columns)
		# print(P_columns)
		# 		print("")
		# P_columns = [table1.name+"."+ i for i in P_columns]
		index = [-1] * len (P_columns)
		for j in range(0,len(P_columns)):
			P_column = P_columns[j]
			for i in range(0, len(table1.columns)):
				column = table1.columns[i]
				if P_column == column:
					index[j] = i
					break
		for i in index:
			if i == -1:
				print("One or more of the columns didn't match")
				exit()
		row = []
		for i in table1.data:
			row = [i[x] for x in index]
			data.append(row)
			row = []
		final_table = Table("final", P_columns, data,1)
		return final_table


def display(table1):
	columns = ",".join(table1.columns)
	print(columns)
	for i in table1.data:
		row = ",".join([str(x) for x in i])
		print(row)





parsed_query_dict = sqlparse(sys.argv[1])
# print(parsed_query_dict)
# print(len(parsed_query_dict['from']))	
table1 = from_parser(parsed_query_dict)
# display(table1)
table1 = where_parser(table1, parsed_query_dict)
# exit()
table1 = select_parser(table1, parsed_query_dict)
display(table1)
# print(table1.name)
# print(table1.columns)
# print(table1.data)
