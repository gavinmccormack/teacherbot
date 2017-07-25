import tweepy
import re 
import os.path
import time
import datetime
import argparse
import sys
from pb_py import main as pandorabots_api
import unicodedata
from random import choice

#host = 'aiaas.pandorabots.com'
#app_id = '1409612214230'
#user_key = 'e8ac9b3afdae54d14e34ca5f63a11a64'
#botname = 'teacherbotlive'
#hashtag = '#teacherbot'
#access_token = '704320338902052864-DxXe34TJvTTa1TVzc1xeO5AUCSKm4Hv'
#access_token_secret = 'DXT8PLh9usFI0MtGcjG9JpKvMx6escLw9S5o7sQHJ7WPW'

#consumer_key = 'DplEsatofSCVpOaZVv4Xnwe17'
#consumer_secret = 'PImRysHCjxTBXZs8PRhjukTnMbiwkSulRiqiVfQXRjJ2iWqK5f'



sys.argv = [x.rstrip() for x in sys.argv] # Strip \r\n
host = sys.argv[1]
app_id =  sys.argv[2]
user_key = sys.argv[3]
botname =  sys.argv[4]      
hashtag =  sys.argv[5]
access_token =  sys.argv[6]
access_token_secret =  sys.argv[7]
consumer_key = sys.argv[8]
consumer_secret =  sys.argv[9]
pandora_botname =  sys.argv[10]

def tweeter(output,screen_name):
    status_update = output + ' @' + screen_name
    print 'Tweeting back: ' + status_update
    try:
        twitter_api.update_status(status_update)

    except tweepy.TweepError as e:
        tweetErrors = open(os.path.join(os.path.dirname(__file__),"chatlogs" , botname,'tweet-errors.txt'),'ab')
        tweetErrors.write(str(e) + "\n")
        tweetErrors.close()

def query_log (user_input, output):

    q2bot = open(os.path.join(os.path.dirname(__file__),"chatlogs" , botname,'queriestobot.txt'),'ab')
    currentTime = datetime.datetime.fromtimestamp(time.time()).strftime('%y/%m/%d %H:%M:%S')
    q2bot.write("<small>" + currentTime + "</small> \n")
    q2bot.write("<b> Query: </b>" + user_input + "\n")
    q2bot.write("<b> Response: </b>" + output + "\n\n")
    q2bot.close()

def query_bot(text, screen_name, cust_id):
    user_input = re.sub('(@|#)[a-zA-Z0-9_]{1,25}','',text).strip()  # Strip hashtags and usernames
    output = pandorabots_api.talk(user_key, app_id, host, pandora_botname, user_input, recent=False)["response"]
    query_log(user_input, output) # Create our logfile of queries and responses, to be loaded in the interface later
    return output
    
def process_hashtags(hashtags):
    """ Check if multiple tags and return as an array """
    if "," in hashtags:
        hashtags = hashtags.split(",")
        hashtagArray = hashtags[0]   
        if hashtags > 1:
            for n in hashtags[1:]:
                hashtagArray = hashtagArray + " OR " + n        # Create an "OR" query with each hashtag
        return [hashtagArray]
    else:
        return [hashtags]

def fetch_mentions(last_tweet_id):
    query = process_hashtags(hashtag)
    if last_tweet_id:
        results = twitter_api.search(q=query, count=30, since_id=last_tweet_id) ## Count changed to something small temporarily so that we don't accidentally spam 50 random people.
    else:
        results = twitter_api.search(q=query, count=30)
    if results:
        mentions = results
    #if list with hashtags is empty, get mentions based on Teacherbot username
    elif last_tweet_id:
        mentions = twitter_api.mentions_timeline(since_id=last_tweet_id)
    else:
        mentions = twitter_api.mentions_timeline()
    return mentions


def maintain_log(tweet_id, text, screen_name, author, user_id):
    pbots_cust_id = user_id
    tweet_list = [tweet_id, pbots_cust_id, author, user_id, text] 
    # add tweet to the tweet dict
    if screen_name in tweet_dict:
        tweet_dict[screen_name].append(tweet_list)
    else:
        tweet_dict[screen_name] = [tweet_list]
    # add tweet to log
    tweet_log.write(screen_name + ' ' + ' ' .join(tweet_list) + '\n')

    

def check_rate_limit_status():
    rate_limit = twitter_api.rate_limit_status()
    mentions_remaining = rate_limit['resources']['statuses']['/statuses/mentions_timeline']['remaining']
    if mentions_remaining != 0:      
        return True
    else:
        ### Log Rate Overflows
        ofile = open(os.path.join(os.path.dirname(__file__),"chatlogs" , botname,'tweet_log_test.txt'),'ab')
        ofile.write('Rate Limit overflow - \n')
        ofile.close()
        return False

def setup():
    try:
        tweet_log = open(os.path.join(os.path.dirname(__file__),"chatlogs" , botname,'tweet_log_test.txt'),'rb')
    except:
        ofile = open(os.path.join(os.path.dirname(__file__),"chatlogs" , botname,'tweet_log_test.txt'),'wb')
        ofile.write('screen_name 478595937619542017 pbots_cust_id name user_id text\n')
        ofile.close()
        tweet_log = open(os.path.join(os.path.dirname(__file__),"chatlogs" , botname,'tweet_log_test.txt'),'rb')
    tweet_dict = {}
    last_tweet_id = ''
    #verify your credentials with twitter
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    #create api handler
    twitter_api = tweepy.API(auth)
    #initialize self
    me = twitter_api.me()
    my_id = me.id
    my_screen_name =  me.screen_name
    for line in tweet_log:
        split_line = line.split()
        screen_name = split_line[0]
        #create dict from log
        if screen_name in tweet_dict:
            tweet_dict[screen_name].append(split_line[1:])
        else:
            tweet_dict[screen_name] = [split_line[1:]]
        tweet_id = split_line[1]
        #get most recent tweet replied to
        if tweet_id > last_tweet_id:
            last_tweet_id = tweet_id
    tweet_log.close()
    tweet_log = open(os.path.join(os.path.dirname(__file__),"chatlogs" , botname,'tweet_log_test.txt'),'ab')
    return tweet_dict, auth, twitter_api, me, my_id, my_screen_name, tweet_log


############################################################################################
### Twitter_bot script adaptions for multiple processes
try:
    tweet_dict, auth, twitter_api, me, my_id, my_screen_name, tweet_log = setup()
except Exception,e:
    # We log to a file in the scripts directory if there is a syntax or setup problem
    textlog = open("Setup Problem.txt", "w")
    import traceback
    var = traceback.format_exc()
    currentTime = datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')
    textlog.write(currentTime)
    textlog.write( "\n" + str(var) )
    textlog.write(str(e))
    textlog.close()


log_directory = os.path.join(os.path.dirname(__file__),"chatlogs" , botname)
try:
    os.mkdir(log_directory)
except:
    pass


def follow(tweetAuthor, userID):
    if not tweetAuthor.following and not my_id == userID:
        twitter_api.create_friendship(id=userID)

def main(last_tweet_id):
    # open tweet_log for appending
    tweet_log = open(os.path.join(os.path.dirname(__file__),"chatlogs" , botname,'tweet_log_test.txt'),'ab')
    if (check_rate_limit_status()):
        mentions = fetch_mentions(last_tweet_id)
        tweet_id_list = []
        main_tweet_dict = {}
        for tweet in reversed(mentions):
            is_following = tweet.author.following
            user_id = tweet.author.id
            author = tweet.author.name.encode('UTF-8')
            text= u''.join(c for c in tweet.text if not unicodedata.category(c).startswith('C')).encode('utf-8').strip()
            print "Tweet Text: "
            screen_name = tweet.author.screen_name.encode('UTF-8')
            main_tweet_dict[tweet.id] = [text,screen_name,author,str(user_id)]
            # follow the tweet author if not already
            if not is_following and not my_id==user_id:
                twitter_api.create_friendship(id=user_id)
                print "you are now following: " + screen_name 
            if screen_name != my_screen_name and str(tweet.id) not in tweet_id_list:
                print "User " + author + ' @' + screen_name + ' tweeted: "' + text + '"'
                # get the bot's response to the query
                response = query_bot(text, screen_name, user_id).encode('utf-8')
                if response:
                    tweeter(response,screen_name)


            tweet_id_list.append(str(tweet.id))
        # make sure entries are added to log in corrrect order
        for key in sorted(main_tweet_dict.keys()):
            value = main_tweet_dict[key]
            maintain_log(str(key), value[0], value[1], value[2], str(value[3]))
        if tweet_id_list != []:
            last_tweet_id = max(tweet_id_list)
    tweet_log.close()
    return last_tweet_id
    

def run():
    last_tweet_id = open(os.path.join(os.path.dirname(__file__),"chatlogs" , botname,'tweet_log_test.txt'),'rb').readlines()[-1].split()[1]
    last_tweet_id = main(last_tweet_id)

def Main():
      run()

if __name__ == "__main__":
    try:
        Main()
    except Exception,e:
        ## Print a traceback to a file if anything goes wrong.
        efile = open(os.path.join(os.path.dirname(__file__),"chatlogs" , botname,'error_log.txt'),'wb')
        efile.write(str(my_screen_name) + "\n")
        import traceback
        var = traceback.format_exc()
        efile.write( "\n" + str(var) )
        efile.close()




