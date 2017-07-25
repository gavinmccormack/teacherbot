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

### Call from Django Database
app_id = pandora_settings.objects.get().app_id
user_key = pandora_settings.objects.get().user_key
host = pandora_settings.objects.get().host
botname = 'Notabot' ### Temp variable for dev





###############
### Create Bot
### Deployed from ajax get call to /chatbot/[ID]/pa-create/
def create_bot(pa_botname):
	API.create_bot(user_key, app_id, host, pa_botname)
	create = API.compile_bot(user_key, app_id, host, pa_botname) ## Also compile here, to minimize front end
	return str(create)



###############
### Download Files
def pandora_download(pa_botname):
	try:
		file_path, pth = os.path.split( ENV_PATH )
		file_path, pth = os.path.split( file_path )   ## A clunky but environment safe way of navigating to the right static dir
		file_path = os.path.join(file_path, 'static', "chatbot-archives", "tbarchive-")
		download = API.download_bot(user_key, app_id, host, pa_botname, file_path)
		download_link = """: <a href="/static/chatbot-archives/tbarchive-""" + pa_botname + """.zip"> Download Here </a>"""  
		return download + download_link
	except Exception, error:
	    return str(error)




###########################################################################################################
### File listing + Light html parsing 
### This function is probably pretty poorly conceived, and takes some of the HTML language away from the template due to API handling

def pandora_list_files_short(pa_botname):
	filelist = API.list_files(user_key, app_id, host, pa_botname)
	filelist = filelist.split('\n')
	output = "<div class='file-list'>"
	for a in filelist[:-1]:
			output = (output +" <div class='file-block'><span>" + a + "</span></div>")
	return output + "</div>"


### PandoraBot Talk
def pandora_talkto_bot(pa_botname, input_string):
	""" Talks to the bot. API returns a dict with response (along with sessionid and others for debugging purposes) """
	return API.talk(user_key, app_id, host, pa_botname, input_string)['response']


def pandora_compile_bot(pa_botname):
	""" Compiles bot with files already on pandorabots """
	return API.compile_bot(user_key, app_id, host, pa_botname)



def pandora_delete_file(pa_botname, filename):
	delete = API.delete_file(user_key, app_id, host, pa_botname, filename)
	return delete


def pandora_delete_all_files(pa_botname):
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

def flatten(directory):
    if (os.path.exists(directory)):
        for root, subdirs, files in os.walk(directory):
            for file in files:
                print file
                print os.path.join(directory, file)
                os.path.join(root,file)
                os.rename(os.path.join(root,file), os.path.join(directory, file))
            if len(os.listdir(root)) == 0:
            	os.rmdir(root)
    if len(os.listdir(directory)) == 0:
            	os.rmdir(directory)


def pandora_upload_single_file(pa_botname, path):
	""" Uploads a single file, used internally from view by Django files """
	API.upload_file(user_key, app_id, host, pa_botname, path)

def pandora_upload_files_from_path(pa_botname, file_list):
	""" Upload single files from an array of paths """
	# Counter for successful uploads
	success_response = 0
	# Keys: File_name, Value: error
	file_errors = {}
	pandora_delete_all_files(pa_botname)
	for n in file_list:
		nt, name = os.path.split(n)
		name = re.sub(r'\(v[0-9]+\)', '', name)
		try:
			API.upload_file(user_key, app_id, host, pa_botname, n)
			success_response += 1
		except Exception, error:
			file_errors[name] = error
	return success_response, file_errors

def pandora_upload(pa_botname, directory):
	""" Uploads a directory of files to pandora """
	patterns=['*.aiml','*.set','*.map','*.substitution','*.pdefaults','*.properties']
	
	pandora_delete_all_files(pa_botname)
	for p in patterns:
	    for filenames in os.listdir(directory):
	        if fnmatch.fnmatch(filenames, p):
	        	path = os.path.join(directory,filenames)
	        	result = API.upload_file(user_key, app_id, host, pa_botname, path)
	        else:
	        	flatten(directory) # If not a file then a folder, or whoever put the zip together was a meathead.

	result = API.compile_bot(user_key, app_id, host, pa_botname)
	if 'successfully' in result:
	    for root, subdirs, filenames in os.walk(directory):
	        for filename in filenames:
	            path = os.path.join(directory,filename)
	            os.remove(path)



### Upload wrapper function. First to be referenced on URL request.
def upload_archive(pa_name, f):
	"""Extracts files, performs the API upload for single files, but otherwise passes to pandora_upload(x,y)"""
	filename, file_type = os.path.splitext(f.name)
	pth = os.path.abspath(os.path.dirname(__file__))
	pa_file_types = ['.aiml', '.substitutions', '.maps', '.sets', '.properties', '.pdefaults'] ## File types that should be uploaded immediately.	
	### Open the file object passed, write it to a file in the temporary directory, and then pass that path to the python pb api call.
	if file_type in pa_file_types:
		single_file = os.path.join(pth, filename + file_type)
		pth = os.path.join(pth,"temporaryfiles" , pa_name , f.name)
		tempFile = open(pth, 'w')
		tempFile.write(f.read())
		result = API.upload_file(user_key, app_id, host, pa_name, pth)
		API.compile_bot(user_key, app_id, host, pa_name)
		return result
	### If file is archive. Only handles zips at the moment.
	if file_type == ".zip":
		pth = os.path.join(pth,"temporaryfiles" , pa_name,  "")
		archive = zipfile.ZipFile(f)
		with zipfile.ZipFile(f) as out:
			out.extractall(pth)

	pandora_upload(pa_name, pth) 

