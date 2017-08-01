### ATM copied from pandora scripts.

import sys
import os
import fnmatch
import pa_py_api as API
import urllib2
import re
from chatbot.models import pandora_settings
from teacherbot.settings import ENV_PATH
import time
import datetime
import zipfile
import shutil
import os
import json
import log

import pb_api_json as pbAPI

### Call from Django Database
app_id = pandora_settings.objects.get().app_id
user_key = pandora_settings.objects.get().user_key
host = pandora_settings.objects.get().host
botname = 'Notabot' ### Temp variable for dev

###############
### List all bots
### Deployed from /chatbot/list-all/
def get_bot_list():
	return pbAPI.list_bots(user_key, app_id, host)

###############
### Create Bot
### Deployed from ajax get call to /chatbot/[ID]/pa-create/
def create_bot(pa_botname):
	API.create_bot(user_key, app_id, host, pa_botname)
	create = API.compile_bot(user_key, app_id, host, pa_botname) ## Also compile here, to minimize front end
	return str(create)

###############
### Download Files
def get_files_link(pa_botname):
	try:
		file_path, pth = os.path.split( ENV_PATH )
		file_path, pth = os.path.split( file_path )   ## A clunky but environment safe way of navigating to the right static dir
		file_path = os.path.join(file_path, 'static', "chatbot-archives", "tbarchive-")
		download = API.download_bot(user_key, app_id, host, pa_botname, file_path)
		download_link = """: <a href="/static/chatbot-archives/tbarchive-""" + pa_botname + """.zip"> Download Here </a>"""  
		return download + download_link
	except Exception, error:
	    return str(error)


###############
### Download Files
def get_attached_files(pa_botname):
	filelist = pbAPI.list_files(user_key, app_id, host, pa_botname)
	return filelist


def pandora_debug_bot(pa_botname):
	result = pbAPI.debug_bot(user_key, app_id, host, pa_botname)
	return result

###########################################################################################################
### File listing + Light html parsing 

def get_filelist(pa_botname):
	filelist = pbAPI.list_files(user_key, app_id, host, pa_botname)
	filelist = extract_filenames(filelist)
	return filelist

def extract_filenames(filelist_object):
	# Takes json file list and sits out list of file names
	filenames = []
	file_types = ['files', 'maps', 'properties', 'pdefaults', 'sets', 'substitutions']
	for dict_element in filelist_object:
		if dict_element in file_types:
			for i in range(len(filelist_object[dict_element])):
				filenames.append(filelist_object[dict_element][i]['name'] + '\n')
	return filenames

def get_filetimes(pa_botname):
	filetimes_dict = {}
	filelist = pbAPI.list_files(user_key, app_id, host, pa_botname)
	filetimes = extract_filetimes(filelist)
	filelist = extract_filenames(filelist)
	for i in range(len(filelist)):
		filetimes_dict[filelist[i]] = filetimes[i]
	return filetimes_dict

def extract_filetimes(filelist_object):
	filetimes = []
	file_types = ['files', 'maps', 'properties', 'pdefaults', 'sets', 'substitutions']
	for dict_element in filelist_object:
		if dict_element in file_types:
			for i in range(len(filelist_object[dict_element])):
				filetimes.append(filelist_object[dict_element][i]['modified'] + '\n')
	return filetimes


### PandoraBot Talk
def bot_talk(pa_botname, input_string):
	""" Talks to the bot. API returns a dict with response (along with sessionid and others for debugging purposes) """
	return API.talk(user_key, app_id, host, pa_botname, input_string)['response']


def bot_compile(pa_botname):
	""" Compiles bot with files already on pandorabots """
	return API.compile_bot(user_key, app_id, host, pa_botname)



def bot_delete_file(pa_botname, filename):
	delete = API.delete_file(user_key, app_id, host, pa_botname, filename)
	return delete


def bot_delete_all_files(pa_botname):
	try:
		filelist = API.list_files(user_key, app_id, host, pa_botname).split('\n')
		for n in filelist:
			delete = API.delete_file(user_key, app_id, host, pa_botname, n)
		return "All files deleted"      # Not the most explanitory return function as only related to the last delete
	except Exception, e:
		deletelog = open(os.path.join(os.path.dirname(__file__),'deletefilelog.txt'),'ab')
		currentTime = datetime.datetime.fromtimestamp(time.time()).strftime('%y/%m/%d %H:%M:%S')
		deletelog.write(currentTime + ":\n")
		deletelog.write(str(e))
		deletelog.close()
		return "Delete failed."


###############################################################################################
### Pandora Upload File Actions
### Could definitely be cleaned up; the ideal would be more small functions with clear purpose.


###############
def bot_upload_files(pa_botname, file_list):
	""" Upload single files from an array of paths """
	# Counter for successful uploads
	success_response = 0
	# Keys: File_name, Value: error
	file_errors = {}
	bot_delete_all_files(pa_botname)
	for n in file_list:
		nt, name = os.path.split(n)
		name = re.sub(r'\(v[0-9]+\)', '', name)
		try:
			pbAPI.upload_file(user_key, app_id, host, pa_botname, n)
			success_response += 1
		except Exception, error:
			file_errors[name] = error
	return success_response, file_errors




