import re

from pymongo import *
from clusterer import *

mhost = 'wowhack.alexbilbie.com'


def getDocs(source_type=False):

	conn = connection.Connection(mhost)
	db = conn.wowhack

	docs = []
	sources = []

	if source_type:
		cursor =  db.sources.find(source=source_type)
	else:
		cursor =  db.sources.find()

	for src in cursor:
		text = re.sub('[\s]+',' ',src['text']).lower()
	
		docs.append((src['_id'],text))
	
		if src['source'] not in sources:
			sources.append(src['source'])
	
		#print text
		#print
		#print sources

	return docs
		
corp = docCorpus(getDocs('timesonline'))
counter = WordCount(corp,20)
counter.map_reduce()
corp.prettyTable()
doKmeans(corp,False)


