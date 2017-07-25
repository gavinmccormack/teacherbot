import subprocess
import sys
import os.path
import traceback

from chatbot.models import pandora_settings, cbot

### A bit rough at the moment. Ideally the view calls this script, it deploys the sub process, and additional
### continue to monitor it/ensure if stays live.


def deploy_cbot_process(cbot_id):
	try:
		pth = os.path.abspath(os.path.dirname(__file__))
		os.chdir(pth)
		pandora_host = pandora_settings.objects.get().host  #1
		pandora_app_id = pandora_settings.objects.get().app_id #2
		pandora_user_key = pandora_settings.objects.get().user_key #3
		pandora_bot_name = cbot.objects.get(pk=cbot_id).pandora_name # 10
		twitter_name = str(cbot_id)
		twitter_hashtags = cbot.objects.get(pk=cbot_id).twit_hashtags # 5
		twitter_token = cbot.objects.get(pk=cbot_id).twit_token # 6
		twitter_token_secret = cbot.objects.get(pk=cbot_id).twit_token_secret #7
		twitter_c_key = cbot.objects.get(pk=cbot_id).twit_c_key #8
		twitter_c_secret = cbot.objects.get(pk=cbot_id).twit_c_secret #9
		arguments = [pandora_host,pandora_app_id,pandora_user_key,twitter_name,
		twitter_hashtags,twitter_token,twitter_token_secret,twitter_c_key,twitter_c_secret, pandora_bot_name]
		
		### Open the chatbot script as a sub process
		pth = os.path.abspath(os.path.dirname(__file__))
		pth = os.path.join(pth, "twitter_bot.py") 

		chatproc = subprocess.Popen([sys.executable, pth] + arguments,
	                                    stdout=subprocess.PIPE, 
	                                    stderr=subprocess.STDOUT)

		return "Chatbot Process process started <br /> " + str(chatproc.communicate()).replace("\r\n","<br />")
	except NameError:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
		lines = '\n'.join('  + !! ' + line for line in lines)
		return ("Chatbot failed. Logs may contain more detail than is displayed below: " + lines)



### Not Currently in use
### Needs a proper process manager, or for twitter_bot.py to work continously
### It would be ideal to manage the process from this side - allowing it to run on a user defined timeline.
def cbot_process_watcher(cbot_id):
	while (cbot.objects.get(pk=cbot_id).enabled != False):
		if (cbot.objects.get(pk=cbot_id).active_process != False):
			deploy_cbot_process(cbot_id)