#!/usr/bin/python
# -*- coding: utf-8 -*-

# tweetcluster.py (C) Giles Richard Greenway 2013
# Search for tweets containing a given term, construct a word frequency table and attempt to cluster tweets by k-means, moderately nicely threaded using map-reduce...
# Usage:	tweetcluster <term> [count]
#		tweetcluster <term> <count> <outputFile>
#		tweetcluster  <inputFile>"

# Notes to self: Further reading.
# http://www.cs.sun.ac.za/~kroon/pubs/devilliers2012unsupervised/devilliers2012unsupervised.pdf
# http://www.idc-online.com/technical_references/pdfs/information_technology/Analysis%20of%20Social.pdf
# http://cs.stanford.edu/people/jure/pubs/memeshapes-wsdm11.pdf

import json
import os
import pickle
import random
import re
import sys
import time
import urllib

# Rather neat module for running map-reduce threads on a single machine.
# http://clouddbs.blogspot.co.uk/2010/10/googles-mapreduce-in-98-lines-of-python.html
from map_reduce import MapReduce
# Bubbling under: octopy and mincemeat:
# http://code.google.com/p/octopy/
# https://github.com/michaelfairley/mincemeatpy
# More geared to map-reduce on multiple machines over a network. Don't always give back sockets when they should.

# Quick-and-dirty-stopwords here:
# http://www.textfixer.com/resources/common-english-words-3letters-plus-with-contractions.txt
# http://www.textfixer.com/resources/common-english-words.php
try:
	stopWords = []
	stopWordFile = open('stopWords.txt','r')
	for line in stopWordFile:
		stopWords += line.split(',')
	stopWordFile.close()	
except:
	print "Can't find stopWords.txt!"
	stopWords = ['is', 'my', 'the','for','was', 'has', 'are', 'has', 'you', 'can', 'and', 'have', 'this', 'that', 'than', 'they', 'their', 'with', 'will', 'http']

class tweet(object):
	# Extract a tweet from the JSON returned by Twitter's search API.
	def __init__(self,tweet_dump):
		self.id = tweet_dump['id']
		self.user = tweet_dump['from_user']
		self.username = tweet_dump['from_user_name']
		self.when = time.strptime(tweet_dump['created_at'][:-6],'%a, %d %b %Y %H:%M:%S')
		# Quick clean-up of HTML entities.
		rawText = tweet_dump['text']
		for entity in  [('&quot','"'),('&apos;',"'"),('&amp;','&'),('&lt;','<'),('&gt;','>')]:
			rawText = re.sub(entity[0],entity[1],rawText)
		self.text = rawText.encode('ascii','ignore')	
	
		self.wordSet = set()
		self.centroidDist = 1.0        
		        
	def show(self):
		print self.username.encode('ascii','ignore')+" (@"+self.user+") tweeted on "+time.asctime(self.when)+":"
		print self.text
		
	def addWord(self,index):
		self.wordSet.add(index)

# A set of related tweets, their centroid and mean distances to it.
class tweetCluster(object):
	# Build a random centroid of wordCount word indices from a set of size dictSize.
	def __init__(self, wordCount, dictSize):
		self.wordSet = set() # Holds the word indices of the cluster centroid.
		self.tweetIDs = []
		self.meanDistance = 1.0	
		while len(self.wordSet) < wordCount:
			word = random.choice(range(dictSize))
			self.wordSet.add(word)	
	
	# Jaccard distance: Similarity is the size of the intersection of a tweet and the centroid over the size of their union.
	# Subtract the similairity from one to get the distance. 
	def distanceToTweet(self,tweet):
		return 1.0 - float(len(self.wordSet & tweet.wordSet)) / (1+len(self.wordSet | tweet.wordSet))

	# Add a dictionary to tweets to the cluster, use IDs as keys.
	def addTweets(self,tweetDict):
		self.tweetIDs = tweetDict.keys() # We might want to get the text of the cluster's tweets at some point.
		
		# Fraction of the cluster's tweets that must contain a word for it to be added to the centroid.
		# If the centroid were the true mean of its tweets this would be 0.5, but the centroids would nearly always be empty!
		threshold = 0.1
		
		tweetCount = len(self.tweetIDs)
		minTweets = int(float(tweetCount)*threshold) 
		
		allWords = set() # Union of all the words in the cluster's tweets.
		for tweet in tweetDict.values():
			allWords |= tweet.wordSet
		
		# Rebuild the centroid.
		self.wordSet = set()
		for word in allWords:
			if [ word in tweet.wordSet for tweet in tweetDict.values() ].count(True) > minTweets:
				self.wordSet.add(word)

		# Find the distance of each tweet in the cluster to the new centroid.
		for tweet in tweetDict.values():
			tweet.centroidDist = self.distanceToTweet(tweet)

		# Mean distance of the tweets to the new centroid.
		self.meanDistance = sum([ tweet.centroidDist for tweet in tweetDict.values() ]) / tweetCount

# A set of tweets, the clusters they belong to
class tweetCorpus(object):
  
	def __init__(self,term,requiredCount=10):

		self.term = term.lower()
		
		stopWords.append(self.term)
		
		self.tweets = {}
		self.freqTab = [] # List of (wordString,wordFrequency) tuples, most frequent words first.

		self.clusterSets = [] # Lists of clusters of increasing size.
		self.meanDistances = [1.0] # Mean centroid distance to each tweet for all cluster in a set.
		
		# Results per page can be a maximum of 100.	
		rpp = min([requiredCount,100])
		hrpp = rpp/2
		# Work backwards page by page, so's not to keep getting the same tweets as more come in for popular topics.
		page = requiredCount / rpp
		searching = True

		# Attempt to grab the required number of tweets.
		while searching and len(self.tweets.keys()) < requiredCount:
			results = self.getTweets(self.term,rpp,page)
			dudTweets = 0
			for result in results:
				if self.term in result.text.lower() and result.id not in self.tweets.keys():
					self.tweets[result.id] = result
					if len(self.tweets.keys()) == requiredCount:
						break
				else:
					dudTweets += 1
			if dudTweets:
				print dudTweets.__str__()+" tweets were duplicate or missing the search term."
			print (100*len(self.tweets.keys())/requiredCount).__str__()+"% done."
			if dudTweets > hrpp:
				# Give up if we've seen half of the tweets before.
				print "Too many dud tweets."
				searching = False
			if page > 1:		
				page -= 1

	# The bit that actually troubles Twitter's search API:
	def getTweets(self,term,count,page):
		params = urllib.urlencode([('q',term),('rpp',count),('page',page),('lang','en'),('result_type','recent')])
		gotTweets = []	
		
		try:
			print "Prodding Twitter..."
			results = json.loads(urllib.urlopen('http://search.twitter.com/search.json?'+params).read())['results']
		except:
			print "Couldn't access Twitter!"
			results = []
		print "Found "+len(results).__str__()+" tweets."
		for result in results:
			gotTweets.append(tweet(result))
		return gotTweets
	
	# Display all the tweets.
	def show(self):
		for tweet in self.tweets.values():
			tweet.show()
			print
	
	# Moderately decorous frequency table.
	def prettyTable(self):
		print 'Word frequencies for tweets containing: '+self.term
		# Jolly wheeze to get the terminal width. Wonder if it works on anything other than Linux...
		try:
			h, w = os.popen('stty size', 'r').read().split()
			w = int(w)
		except:
			w = 80
		colWidth = 9 + max([len(wrd[0]) for wrd in self.freqTab]) 
		cols = w / colWidth
		count = len(self.freqTab)
		rows = (count / cols)
		for row in range(rows):
			thisRow = ''
			for col in range(cols):
				index = col*rows + row
				if index < count:
					chunk = ' '.join([str(index),self.freqTab[index][0],'('+str(self.freqTab[index][1])+')'])
					thisRow += chunk + (colWidth-len(chunk))*' ' 
			print thisRow
	
	# Show the words in each cluster's centroid.
	def showClusters(self,index):
		clusters = sorted(self.clusterSets[index], key=lambda c: -len(c.tweetIDs))
		for i,cluster in  enumerate(clusters):
			print "Terms for cluster "+str(i)+", ("+str(len(cluster.tweetIDs))+" tweets) mean centroid distance: "+str(cluster.meanDistance)
			words =  [ self.freqTab[word][0] for word in sorted(cluster.wordSet) ]
			print ' '.join(words) # Will these be vaguely relevant, or one of the aphorisms of Gertrude Stein? http://www.bartleby.com/140/
			print


	def freqDump(self):
		outfile = open(self.term+'.tab','wb')
		for word in self.freqTab:
			outfile.write(word[0]+':'+str(word[1])+'\n')
		outfile.close()	
			
		

class WordCount(MapReduce):
	def __init__(self,corpus):		
        	MapReduce.__init__(self)	
		self.corpus = corpus
		self.data = corpus.tweets
	
	# Return a list of tuples: (tweetID,tweetText)
	def parse_fn(self, data):
		return [(key,data[key].text) for key in data.keys()] 	
	
	# Recieves a tweet's ID and it's text. Returns a list of (word,tweedID) tuples.
	def map_fn(self, key, val):
		words = []
		for word in val.split():
			if len(word) > 2:
				URLs = re.findall("http://[^\s^,]+",word)
				if URLs: # Don't mangle the "word" if its a URL...
					cleanWord = URLs[0]
				else:
					cleanWord = re.sub('[#\.,:!*+?"]+',"",word.lower()) # ...or strip punctuation.
				if len(cleanWord) and cleanWord not in stopWords:
					words.append((cleanWord, (1,key)))
				
		return words
	
	# Receive all the IDs of tweets containing a given word. Return the word, its frequency and a list of unique tweet IDs. 
	def reduce_fn(self, word, values):
		count = 0
    		docs = []
    		for val in values:
        		count += val[0]
        		if val[1] not in docs:
				docs.append(val[1])
		
        	return [(word, count, docs)]
	
	# Build the corpus' frequency table and give each tweet the indices of its words.
	def output_fn(self, output_list):
		for i,word in enumerate(sorted(output_list,key = lambda wrd: -wrd[1])):
			self.corpus.freqTab.append((word[0],word[1]))
			for tweet in word[2]:
				self.corpus.tweets[tweet].addWord(i)

# Run a single iteration of k-means on the given tweet corpus, and update the centroids of the clusters.
class kMeansIter(MapReduce):
	def __init__(self,corpus):
		MapReduce.__init__(self)	
		self.corpus = corpus
		self.data = corpus.tweets
		self.totalTweets = len(self.data)
	
	# Return a list of (ID,tweet) tuples.
	def parse_fn(self, data):
		return [ (key,data[key]) for key in data.keys() ] 	
	
	# Given an ID and its tweet, return the index of the nearest cluster and the ID. 
	def map_fn(self, key, tweet):
		minDistance = 1.0
		nearestCluster = 0
		for i,cluster in enumerate(self.corpus.clusterSets[-1]):
			distance = cluster.distanceToTweet(tweet)
			if distance < minDistance:
				minDistance = distance
				nearestCluster = i
		
		tweet.centroidDist = minDistance
		
		return [(nearestCluster,key)]		
	
	# Given all the tweet IDs for a given cluster index, add thoses tweets to the cluster.
	def reduce_fn(self,clusterIndex,tweetIDs):
		tweetDict = dict([ (ID,self.corpus.tweets[ID]) for ID in tweetIDs ]) # Send the tweets as a dictionary: {<tweetID>:<tweet>}
		thisCluster = self.corpus.clusterSets[-1][clusterIndex] # The given cluster in the latest set. 
		thisCluster.addTweets(tweetDict)

		return []

	def output_fn(self, output_list):
		
		meanDist = sum([ tweet.centroidDist for tweet in self.corpus.tweets.values() ]) / self.totalTweets
		self.corpus.meanDistances[-1] = meanDist
		
		print "K-means iteration for "+str(len(self.corpus.clusterSets[-1]))+" centroids. Mean distance to centroids: "+str(meanDist)		

def doKmeans(corpus):
	
	# How similiar do successive mean cluster distances have to be before we declare convergence?
	nearlyOne = 0.999995
	
	totalWords = sum([len(tweet.wordSet) for tweet in corpus.tweets.values()]) # Total word-count for the corpus.
	meanWords = totalWords / len(corpus.tweets.values()) # Mean words per tweet.
	
	corpusWords = len(corpus.freqTab) # Unique words in the corpus.
	
	bestCount = 2 # How many clusters yield the lowest mean centroid distance?
	clusterCount = 2
	getMoreClusters = True
	maxCount = max(len(corpus.tweets) / 3, 3) # Don't let things degenerate to one tweet per cluster!
	
	# Try increasingly large cluster sets until convergence doesn't improve.
	while getMoreClusters and clusterCount <= maxCount:
	
		countMean = corpus.meanDistances[-1]
	
		# Start a new cluster set.
		corpus.clusterSets.append([])
		corpus.meanDistances.append(1.0)
	
		# Initialise the clusters to have similar numbers of words to the tweets.
		# Would making the initial clusters less sparse do any good/harm?
		for i in range(clusterCount):	
			corpus.clusterSets[-1].append(tweetCluster(meanWords,corpusWords))

		moreIterations = True
	
		# Run k-means iterations for the current cluster set until convergence.	
		while moreIterations:
		#for i in range(10):
			lastMean = corpus.meanDistances[-1]
			k = kMeansIter(corpus)
			k.map_reduce()		
			if corpus.meanDistances[-1] > nearlyOne * lastMean:
				moreIterations = False
		
		# Do we have a new winner?
		if corpus.meanDistances[-1] < countMean:
			bestCount = clusterCount

		# Have we finished?
		if clusterCount > 2 and corpus.meanDistances[-1] > nearlyOne * countMean:
			getMoreClusters = False
		else:
			clusterCount += 1
			print	
	print
	print "Best results for "+str(bestCount)+" clusters."
	print
	corpus.showClusters(bestCount-2)

# Start here....

outFile = False
allTheTweets = False

# Has a number of tweets been specified? Default to ten.
argCount = len(sys.argv)
if argCount > 2:
	try:
		count = int(sys.argv[2])
	except:
		count = 10
	
	# Do we want to pickle the tweets in a file?
	if argCount == 4:
		outFile = sys.argv[3]
else:
	count = 10
    
if argCount > 1:
	
	if argCount == 2:
		# Are we trying to load previously pickled tweets...
		try:
			pickleFile = open(sys.argv[1],'r')
			allTheTweets = pickle.load(pickleFile)
			pickleFile.close()
		# ...no, probably not.	
		except:
			allTheTweets = False
	
	term = sys.argv[1].lower()
	# If the first argument wasn't a filename, it's a search-term. Grab tweets from Twitter.
	if not allTheTweets:
		allTheTweets = tweetCorpus(term,count)
		if outFile:
			try:
				pickleFile = open(outFile,'w')
				pickle.dump(allTheTweets,pickleFile)
				pickleFile.close()
			except:
				print "Couldn't write to: "+outFile
	else:
		print "loaded "+str(len(allTheTweets.tweets))+" from "+sys.argv[1]
	print
	allTheTweets.show()
	print
	raw_input("Hit return for a word frequency table.")
	print
	counter = WordCount(allTheTweets)
	counter.map_reduce()
	allTheTweets.prettyTable()			
	print
	raw_input("Hit return to attempt k-means clustering.")
	print
	doKmeans(allTheTweets)
	allTheTweets.freqDump()
				
else:
	print "Usage:   tweetcluster <term> [count]"
	print "         tweetcluster <term> <count> <outputFile>"
	print "         tweetcluster  <inputFile>"

