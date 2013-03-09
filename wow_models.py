import re

from pymongo import *
from clusterer import *

mhost = 'wowhack.alexbilbie.com'

conn = connection.Connection(mhost)
db = conn.wowhack

docs = []

for src in db.sources.find():
	text = re.sub('[\s]+',' ',src['text']).lower()
	
	docs.append((src['_id'],text))
	
	print text
	print

corp = docCorpus(docs)
counter = WordCount(corp,2)
counter.map_reduce()
corp.prettyTable()

corp = docCorpus(docs)
counter = WordCount(corp)
counter.map_reduce()
corp.prettyTable()
doKmeans(corp,False)