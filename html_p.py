
def getHTML(doc):
	
	pmid = doc['docId']
	title=''
	sents=[]
	entities=[]

	for item in doc['sentence']:
		if 'index' not in item:
			title=doc['text'][0:item['charEnd']+1]
		else:
			sents.append(doc['text'][item['charStart']:item['charEnd']+1])


	html=''
	html+= "<br><table style='border:1px solid black; border-collapse:collapse;' width='65%' align='center' cellpadding='8'>"
	html+= "<tr><td style='border:1px solid'><b>PMID</b></td><td style='border:1px solid'><b><a href='http://www.ncbi.nlm.nih.gov/pubmed/"+pmid+"' target='_blank'>"+pmid+"</a></b></td></tr>"
	#html+= "<tr><td style='border:1px solid'><font size=2.5>Sent-0</font></td><td style='border:1px solid'><font size=2.5>"+title+"</font></td></tr>"
	x=0
	for sent in sents:
		x+=1		
		html+= "<tr><td style='border:1px solid'><font size=2.5>Sent-"+str(x)+"</font></td><td style='border:1px solid'><font size=2.5>"+sent+"</font></td></tr>"
	html+= "</table><br>"

	doc['html'] =html.encode('utf-8')

	return doc['html']

# doc is the json object returned from MongoDB
#doc = getHTML(doc)
#print (doc['html'].decode('utf-8'))