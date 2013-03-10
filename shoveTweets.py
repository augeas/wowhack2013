import twitter

from credentials import credentials

# Get your bloody own!
api = twitter.Api(consumer_key = credentials['consumer_key'], consumer_secret = credentials['consumer_secret'], access_token_key = credentials['access_token'],
access_token_secret = credentials['access_token_secret'])

def getTweets(term,count):
	tweets = []
	ids = []
	rpp = min([count,100])
	hrpp = rpp/2
	page = count / rpp
	searching = True	

	while searching and len(tweets) < count:
		dudTweets = 0
		try:
			newTweets = api.GetSearch(term, page=page, per_page=rpp)
		except:
			break
		for tweet in newTweets:
			if tweet.id not in ids:
				print tweet.text
				tweets.append((tweet.id,tweet.text))
				if len(tweets) > count:
					break
			else:
				dudTweets += 1
				
		if dudTweets:
			print dudTweets.__str__()+" tweets were duplicate."
			print (100*len(tweets)/count).__str__()+"% done."
			if dudTweets > hrpp:
				# Give up if we've seen half of the tweets before.
				print "Too many dud tweets."
				searching = False
			if page > 1:		
				page -= 1

	print "Found "+str(len(tweets))+' tweets...'
	return tweets
	
#print getTweets('female',50)