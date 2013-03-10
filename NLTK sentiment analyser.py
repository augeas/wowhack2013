#from _future_ import division
import nltk, re, pprint

pos_tweets = [('I love this car', 'positive'),
  		  ('This view is amazing', 'positive'),
			  ('I feel great this morning', 'positive'),
			  ('I am so excited about the concert', 'positive'),
			  ('He is my best friend', 'positive')]

neg_tweets = [('I do not like this car', 'negative'),
              ('This view is horrible', 'negative'),
              ('I feel tired this morning', 'negative'),
              ('I am not looking forward to the concert', 'negative'),
              ('He is my enemy', 'negative')]

tweets = []
for (words, sentiment) in pos_tweets + neg_tweets:
    words_filtered = [e.lower() for e in words.split() if len(e) >= 3]
    tweets.append((words_filtered, sentiment))

tweets = [
    (['love', 'this', 'car'], 'positive'),
    (['this', 'view', 'amazing'], 'positive'),
    (['feel', 'great', 'this', 'morning'], 'positive'),
    (['excited', 'about', 'the', 'concert'], 'positive'),
    (['best', 'friend'], 'positive'),
    (['not', 'like', 'this', 'car'], 'negative'),
    (['this', 'view', 'horrible'], 'negative'),
    (['feel', 'tired', 'this', 'morning'], 'negative'),
    (['not', 'looking', 'forward', 'the', 'concert'], 'negative'),
    (['enemy'], 'negative')]

test_tweets = [
    (['feel', 'happy', 'this', 'morning'], 'positive'),
    (['larry', 'friend'], 'positive'),
    (['not', 'like', 'that', 'man'], 'negative'),
    (['house', 'not', 'great'], 'negative'),
    (['your', 'song', 'annoying'], 'negative')]



def get_words_in_tweets(tweets):
    all_words = []
    for (words, sentiment) in tweets:
      all_words.extend(words)
    return all_words

def get_word_features(wordlist):
    wordlist = nltk.FreqDist(wordlist)
    word_features = wordlist.keys()
    return word_features

    FreqDist = {
    'this': 6,
    'car': 2,
    'concert': 2,
    'feel': 2,
    'morning': 2,
    'not': 2,
    'the': 2,
    'view': 2,
    'about': 1,
    'amazing': 1}

word_features = [
    'this',
    'car',
    'concert',
    'feel',
    'morning',
    'not',
    'the',
    'view',
    'about',
    'amazing',

]

word_features = get_word_features(get_words_in_tweets(tweets))

def extract_features(document):
    	document_words = set(document)
    	features = {}
    	for word in word_features:
        	features['contains(%s)' % word] = (word in document_words)
    	return features

#  	{'contains(not)': False,
#	'contains(view)': False,
#	'contains(best)': False,
#	'contains(excited)': False,
#	'contains(morning)': False,
#	'contains(about)': False,
#	'contains(horrible)': False,
#	'contains(like)': False,
#	'contains(this)': False,
#	'contains(friend)': False,
#	'contains(concert)': False,
#	'contains(feel)': False,
#	'contains(love)': False,
#	'contains(looking)': False,
#	'contains(tired)': False,
#	'contains(forward)': False,
#	'contains(car)': False,
#	'contains(the)': False,
#	'contains(amazing)': False,
#	'contains(enemy)': False,
#	'contains(great)': False,
#	}

training_set = nltk.classify.util.apply_features(extract_features, tweets)

#[({'contains(not)': False,
#	'contains(this)': False,
#	'contains(love)': False,
#	'contains(car)': False,
#	'contains(great)': False},
#	'positive'),
#  ({'contains(not)': False,
#  	'contains(view)': False,
#  	'contains(this)': False,
#  	'contains(amazing)': False,
#  	'contains(great)': False},
#   'positive'),
#  ]

classifier = nltk.NaiveBayesClassifier.train(training_set)

def train(labeled_featuresets, estimator=nltk.ELEProbDist):
    	# Place creation for P(label) distribution
    	label_probdist = estimator(label_freqdist)
   	 # Create the P(fval|label, fname) distribution
    	feature_probdist = {}
    	return NaiveBayesClassifier(label_probdist, feature_probdist)

	print label_probdist.prob('positive')

	print label_probdist.prob('negative')


	print feature_probdist
#{('negative', 'contains(view)'): <ELEProbDist based on 5 samples>,
# ('positive', 'contains(excited)'): <ELEProbDist based on 5 samples>,
# ('negative', 'contains(best)'): <ELEProbDist based on 5 samples>,   }
#print feature_probdist[('negative', 'contains(best)')].prob(True)
#0.076923076923076927

#print classifier.show_most_informative_features(32)
#Most Informative Features
#           contains(not) = False          positi : negati =      1.6 : 1.0
#        contains(tired) = False          positi : negati =      1.2 : 1.0
#      contains(excited) = False          negati : positi =      1.2 : 1.0
#         contains(great) = False          negati : positi =      1.2 : 1.0
#       contains(looking) = False          positi : negati =      1.2 : 1.0
#          contains(like) = False          positi : negati =      1.2 : 1.0
#          contains(love) = False          negati : positi =      1.2 : 1.0
#       contains(amazing) = False          negati : positi =      1.2 : 1.0
#         contains(enemy) = False          positi : negati =      1.2 : 1.0
#         contains(about) = False          negati : positi =      1.2 : 1.0
#          contains(best) = False          negati : positi =      1.2 : 1.0
#       contains(forward) = False          positi : negati =      1.2 : 1.0
#        contains(friend) = False          negati : positi =      1.2 : 1.0
#      contains(horrible) = False          positi : negati =      1.2 : 1.0

tweet = 'Larry is my friend'
print classifier.classify(extract_features(tweet.split()))
#positive

print extract_features(tweet.split())
#{'contains(not)': False,
# 'contains(view)': False,
# 'contains(best)': False,
# 'contains(excited)': False,
# 'contains(morning)': False,
# 'contains(about)': False,
# 'contains(horrible)': False,
# 'contains(like)': False,
# 'contains(this)': False,
# 'contains(friend)': True,
# 'contains(concert)': False,
# 'contains(feel)': False,
# 'contains(love)': False,
# 'contains(looking)': False,
# 'contains(tired)': False,
# 'contains(forward)': False,
# 'contains(car)': False,
# 'contains(the)': False,
# 'contains(amazing)': False,
# 'contains(enemy)': False,
# 'contains(great)': False}

def classify(self, featureset):
 #discard any feature names that are unseen
 #find the log probability of each label, based on the features
 #Add in the log probability of features given labels
 #Generate a probability distribution dictionary using the dict logprob
 #Return the sample with the greaest probability from the dictionary
 #distribution dictionary

# {'positive': -1.0, 'negative': -1.0}
# {'positive': -5.4785441837188511, 'negative': -14.784261334886439}

 DictionaryProbList(logprob, normalize=True, log=True)

tweet = 'Your song is annoying'
print classifier.classify(extract_features(tweet.split()))
# positive
