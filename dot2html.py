import re
import sys
import os.path

def parsedot(filename):
	# outdict["nodes"] = node list
	# outdict["links"] = link list
	# node : {id, label} dict list
	# link : {from, to} dict list
	outdict = {"nodes":[], "links":[]}
	with open(filename, 'r') as f:
		# Read first line
		f.readline()
		while True:
			line = f.readline()
			if not line: 
				break
			if bool(re.match('^[^\[\n]+(?=\[)', line)) or bool(re.match('(?<=\[).*(?=\])', line)):
				id_info = re.findall('^[^\[\n]+(?=\[)', line)[0].strip()
				meta_info = re.findall('(?<=\[).*(?=\])', line)[0].strip()
				if bool(re.match('^\d+$', id_info)):
					label_info = re.findall('(?<=").*(?=")', meta_info)[0]
					outdict["nodes"].append({"id":id_info, "label":label_info})
				elif bool(re.match('\d+\s*->\s*\d+', id_info)):
					from_info = re.findall("\d+\s*(?=->)", id_info)[0].strip()
					to_info = re.findall("(?<=->)\s*\d+", id_info)[0].strip()
					outdict["links"].append({"from":from_info, "to":to_info})
	return outdict

def getVertexWithID(_id, vertices):
	for vertex in vertices:
		if vertex["id"] == _id:
			return vertex
	print _id
	raise  Exception("No such vertex exists!")

def findNeibors(vertex, graph):
	vertices = graph["nodes"] # ["id"]	
	edges = graph["links"]
	res = []
	for edge in edges:
		if edge["from"] == vertex["id"]:
			res.append(getVertexWithID(edge["to"], vertices))
	return res

def computeSCCs(graph):
	vertices = graph["nodes"] # ["id"]
	edges = graph["links"] # ["from"] ["to"]
	index = 0
	stack = []
	sccs = []
	push = stack.append
	pop = stack.pop

	for vertex in vertices:
		if not ("index" in vertex):
			newsccs, index = computeSCC(vertex, graph, push, pop, index)
			sccs  = sccs + newsccs

	# Remove singletons
	realsccs = []
	for scc in sccs:
		if len(scc) > 1:
			realsccs.append(scc)

	return realsccs

def computeSCC(vertex, graph, push, pop, index):
	sccs = []
	vertices = graph["nodes"] # ["id"]
	edges = graph["links"] # ["from"] ["to"]	
	vertex["index"] = index
	vertex["lowlink"] = index
	index = index + 1
	push(vertex)
	vertex["onstack"] = True

	for w in findNeibors(vertex, graph):
		if not "index" in w:
			newsccs, index = computeSCC(w, graph, push, pop, index)
			sccs = sccs + newsccs
			vertex["lowlink"] = min([vertex["lowlink"], w["lowlink"]])
		elif w["onstack"]:
			vertex["lowlink"] = min([vertex["lowlink"], w["index"]])

	if vertex["lowlink"] == vertex["index"]:
		scc = []
		while True:
			w = pop()
			w["onstack"] = False
			scc.append(w)
			if w["id"] == vertex["id"]:
				break
		if len(scc) != 0:
			sccs.append(scc)
	return sccs, index

def nodesToStr(nodelist):
	map_fcn = lambda x: '\t{"id":"' + x["id"] + '","label":"' + x["label"] + '"}'
	nodeStrList = list(map(map_fcn, nodelist))
	return "[\n" + (",\n".join(nodeStrList)) + "]"

def linksToStr(linklist):
	map_fcn = lambda x: '\t["' + x["from"] + '","' + x["to"] + '",{"label":""}]'
	nodeStrList = list(map(map_fcn, linklist))
	return "[\n" + (",\n".join(nodeStrList)) + "]"

def SCCsToStr(sccs):
	map_fcn = lambda (i,x): '"scc' + str(i) + '":["' + '","'.join([item["id"] for item in x]) + '"]'
	sccStrList = list(map(map_fcn, enumerate(sccs)))
	return "{" + (",\n".join(sccStrList)) + "}"

infilename = sys.argv[1]
outfilename = os.path.splitext(infilename)[0] + '.html'
templatename = "dagre-d3.html"

parsedData = parsedot(infilename)

sccs = computeSCCs(parsedData)

for scc in sccs:
	print "newscc:",
	for node in scc:
		print node["id"] + ", ",
	print ""


with open (outfilename, 'w') as f:
	with open (templatename, 'r') as tp:
		while True:
			line = tp.readline()
			if not line: break
			if "####" in line:
				nodeStr = nodesToStr(parsedData["nodes"])
				linkStr = linksToStr(parsedData["links"])
				sccStr = SCCsToStr(sccs)
				f.write("var nodes = ")
				f.write(nodeStr + "\n")
				f.write(",\n links = ")
				f.write(linkStr + "\n")
				f.write(",\n SCClist = ")
				f.write(sccStr + ";\n")
			else:
				f.write(line)

