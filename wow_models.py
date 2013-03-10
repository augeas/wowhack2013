import re

from pymongo import *
from clusterer import *
from shoveTweets import getTweets

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

def pushClusters(corpus,source):
	
	rendered = corpus.render()
	rendered['source'] = source
	
	conn = connection.Connection(mhost)
	db = conn.wowhack
	
	try:
		cluster = collection.Collection(db,'cluster',create=True)
	except:
		cluster = db.cluster
		
	newCluster = cluster.insert(rendered)

def pushTweets(term,count):

	tweets = getTweets(term,count)
	
	conn = connection.Connection(mhost)
	db = conn.wowhack	

	for tweet in tweets:
		thisTweet = {'_id':tweet[0], 'text':tweet[1], 'source':'twitter', 'meta':{'term':term}}
		db.sources.insert(thisTweet)


pushTweets('woman',1000)

#corp = docCorpus(getDocs('twitter'))
#counter = WordCount(corp,1)
#counter.map_reduce()
#corp.prettyTable()
#doKmeans(corp,False)
#pushClusters(corp,'twitter')

