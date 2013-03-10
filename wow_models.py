import re

from pymongo import *
from clusterer import *
from shoveTweets import getTweets

mhost = 'wowhack.alexbilbie.com'

# Grab texts from mongo
def getDocs(source_type=False,meta=False):

	conn = connection.Connection(mhost)
	db = conn.wowhack

	docs = []
	sources = []

	if source_type:
		if meta:
			cursor =  db.sources.find({'source':source_type, 'meta':meta})
		else:	
			cursor =  db.sources.find({'source':source_type})
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

# Extract clusters and word frequencies from a corpus and push it back to mongo
def pushClusters(corpus,source):
	
	rendered = corpus.render()
	rendered['source'] = source
	
	conn = connection.Connection(mhost)
	db = conn.wowhack
	
	try:
		cluster = collection.Collection('cluster')
	except:
		cluster = db.cluster
		
	newCluster = cluster.insert(rendered)

# Push tweet documents to mongo
def pushTweets(term,count):

	tweets = getTweets(term,count)
	
	conn = connection.Connection(mhost)
	db = conn.wowhack	

	for tweet in tweets:
		thisTweet = {'_id':tweet[0], 'text':tweet[1], 'source':'twitter', 'meta':{'term':term}}
		db.sources.insert(thisTweet)

# Grab texts from mongo, shove 'em back as clusters, optionally restricted to docs from a given source, generated from a given search-term.
def getAndPushClusters(source,minCount=1,term=False):
	if term:
		meta = {'term':term}
	else:
		meta = False
	corp = docCorpus(getDocs(source,meta))
	counter = WordCount(corp,minCount)
	counter.map_reduce()
	corp.prettyTable()
	doKmeans(corp,False)
	pushClusters(corp,source)

#getAndPushClusters('twitter',term='lady')

#pushTweets('lady',1000)



