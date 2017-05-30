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
			if not line: break
			if re.match('.+(?=\[)', line) or re.match('(?<=\[).*(?=\])', line):
				id_info = re.findall('.+(?=\[)', line)[0].strip()
				meta_info = re.findall('(?<=\[).*(?=\])', line)[0].strip()
				if re.match('^\d+$', id_info):
					label_info = re.findall('(?<=").*(?=")', meta_info)[0]
					outdict["nodes"].append({"id":id_info, "label":label_info})
				elif re.match('\d+\s*->\s*\d+', id_info):
					from_info = re.findall("\d+\s*(?=->)", id_info)[0].strip()
					to_info = re.findall("(?<=->)\s*\d+", id_info)[0].strip()
					outdict["links"].append({"from":from_info, "to":to_info})
	return outdict

def nodesToStr(nodelist):
	map_fcn = lambda x: '\t{"id":"' + x["id"] + '","label":"' + x["label"] + '"}'
	nodeStrList = list(map(map_fcn, nodelist))
	return "[\n" + (",\n".join(nodeStrList)) + "]"

def linksToStr(linklist):
	map_fcn = lambda x: '\t{"source":"' + x["from"] + '","target":"' + x["to"] + '"}'
	nodeStrList = list(map(map_fcn, linklist))
	return "[\n" + (",\n".join(nodeStrList)) + "]"

infilename = sys.argv[1]
outfilename = os.path.splitext(infilename)[0] + '.html'
templatename = "template.html"

parsedData = parsedot(infilename)

with open (outfilename, 'w') as f:
	with open (templatename, 'r') as tp:
		while True:
			line = tp.readline()
			if not line: break
			if "####" in line:
				nodeStr = nodesToStr(parsedData["nodes"])
				linkStr = linksToStr(parsedData["links"])
				f.write("var nodes = ")
				f.write(nodeStr + "\n")
				f.write(",\n links = ")
				f.write(linkStr + ";\n")
			else:
				f.write(line)

