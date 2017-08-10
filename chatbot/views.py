from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from chatbot.models import  pandora_settings, cbot, aiml_config, aiml_file
from chatbot.forms import chatbot_form, twitterbot_form 
import chatbot.script.pandora_actions as pa
# -*- coding: utf-8 -*-
from chatbot.script.process_manager import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.messages import constants as messages
import os.path
import re
import time
import json

from chatbot.script import log

from django.http import JsonResponse


################################################################
###################### CHATBOT PAGES ###########################

@login_required
def bot_hub(request):
    """ Display the bots owned by the viewing user """
    context = RequestContext(request)
    context['chatbots'] = cbot.chatbot_manager.user(request)
    context['twitterbots'] = cbot.twitterbot_manager.get_twitter_capable(request)
    return render_to_response('bot_hub.html', context)

@login_required
def add(request):
    """ Create a new chatbot """
    if request.method == 'POST':
        form = chatbot_form(request.POST)
        if form.is_valid():
            cbot = form.save(commit=False)
            cbot.author = request.user
            cbot.save()
            form.save_m2m()
            return HttpResponseRedirect(reverse('bot_hub'))
    else:
        form = chatbot_form()
    return render(request, 'cbotforms/add_chatbot.html', {'form': form})

@login_required
def chatbot_to_twitterbot(request):
    """ Display chatbots to transform into twitterbot """
    context = RequestContext(request)
    context['chatbots'] = cbot.chatbot_manager.user(request)
    return render_to_response('chatbot_to_twitterbot.html', context)
    
    
@login_required
def add_twitterbot(request, cbot_id):
    """ Chatbot settings edit """
    chatbot = get_object_or_404(cbot, id=cbot_id)
    if request.method == "POST":
        form = twitterbot_form(request.POST, instance=chatbot)
        if form.is_valid():
            form.author = request.user
            chatbot = form.save(commit=False)
            chatbot.twit_capable = True
            chatbot.save()
            form.save_m2m()
            return HttpResponseRedirect(reverse('bot_hub'))
        else:
            return HttpResponse("Sorry - there was an error the system could not handle.")
            #messages.error(request, "Error")
    else:
        form = twitterbot_form(instance=chatbot, initial={'twit_capable': True})
    return render(request, 'cbotforms/add_twitterbot.html', {'form': form, 'chatbot_id' : cbot_id })

@login_required
def edit(request, cbot_id):
    """ Chatbot settings edit """
    chatbot = get_object_or_404(cbot, id=cbot_id)
    if request.method == "POST":
        form = chatbot_form(request.POST, instance=chatbot)
        if form.is_valid():
            form.author = request.user
            chatbot = form.save(commit=False)
            chatbot.save()
            form.save_m2m()
            return HttpResponseRedirect(reverse('bot_hub'))
        else:
            return HttpResponse("Sorry - there was an error the system could not handle.")
            #messages.error(request, "Error")
    else:
        form = chatbot_form(instance=chatbot)
    return render(request, 'cbotforms/edit_chatbot.html', {'form': form, 'chatbot_id' : cbot_id })

@login_required
def cbot_management(request, cbot_id):
    """ Displays the information page for a single chatbot """
    context = {'chatbot' : cbot.chatbot_manager.get(pk=cbot_id),
               'pandora' : pa,
               'aiml_configs' : aiml_config.config_manager.user(request)}
    return render(request, 'chatbot_management.html', context)

def tbot_management(request, cbot_id):
    """ Displays the information page for a twitterbot """
    context = {'twitterbot' : cbot.twitterbot_manager.get(pk=cbot_id),
               'pandora'    : pa,
               'aiml_configs' : aiml_config.config_manager.user(request)}
    return render(request, 'twitterbot_management.html', context)

@login_required
def chatbot_add_setup(request, cbot_id, setup_id):
    """ Add a setup to the specified chatbot and redirect to next page up tree """
    chatbot = cbot.chatbot_manager.get(id=cbot_id)
    setup = aiml_config.config_manager.get(id=setup_id)
    chatbot.aiml_config.add(setup)
    return HttpResponseRedirect(reverse('cbot_manage', args=[cbot_id]))  

@login_required
def chatbot_remove_setup(request, cbot_id, setup_id):
    """ Removes a setup to the specified chatbot and redirect to next page up tree """
    chatbot = cbot.chatbot_manager.get(id=cbot_id)
    setup = aiml_config.config_manager.get(id=setup_id)
    chatbot.aiml_config.remove(setup)
    return HttpResponseRedirect(reverse('cbot_manage', args=[cbot_id]))



################################################################
###################### Pandora Actions #########################
### These views are referenced via an ajax call from specific templates


def upload_pandora_config(request, cbot_id):
    """ Upload the attached aiml configurations from the internal Setup database """
    try:
        update_uploaded_filetimes(cbot_id)
        pa_name = cbot.bot_manager.get(pk=cbot_id).pandora_name
        configurations = cbot.bot_manager.get(pk=cbot_id).get_attached_configurations()
        file_list = []
        for n in configurations:
            file_list += n.get_file_paths()
        if not file_list:
            return HttpResponse("No files were found")
        
        success_response, errors = pa.bot_upload_files(pa_name, file_list)
        response = check_successful_upload(success_response, errors, len(file_list))
        pa.bot_compile(pa_name)
        return HttpResponse(response)
    except Exception, error:
        return HttpResponse("Error: " + str(error))

def update_uploaded_filetimes(cbot_id):
    bot_object = cbot.bot_manager.get(pk=cbot_id)
    files = get_time_dict(cbot_id)
    log.log_exception(get_time_dict(cbot_id), "get_time_dict.txt")
    jsonified_files = json.dumps(files)
    log.log_exception(json.dumps(files), "jsonified_dict.txt")
    bot_object.uploaded_files = jsonified_files
    bot_object.save()


def check_successful_upload(success_response, errors, num_files):
    successes = success_response
    response = "<b>" + str(successes) + " out of " + str(num_files) + " files successfully uploaded." + "</b><br>" #
    if successes < num_files:
        response += "<b>Failures with files:" + "</b><br>" 
        for filename in errors:
            response += "<b>" + str(filename) + ": " + str(errors[filename]) + "</b><br>"
    return response


@login_required
def create_pandora_bot(request, cbot_id):
    """ Creates or compiles a pandorabot using the currently specified name """
    pa_name = cbot.bot_manager.get(pk=cbot_id).pandora_name
    return HttpResponse(pa.create_bot(pa_name))

@login_required
def download_pandora_bot(request, cbot_id):
    """ Downloads a copy of the files on pandora to a directory and outputs a link """
    pa_name = cbot.bot_manager.get(pk=cbot_id).pandora_name
    return HttpResponse(pa.get_files_link(pa_name))

@login_required
def file_list_pandora_bot(request, cbot_id):
    """ Returns a list of the current files for a specific bot on pandora """
    pa_name = cbot.bot_manager.get(pk=cbot_id).pandora_name
    return HttpResponse(pa.get_filelist(pa_name))

@login_required
def talk_pandora_bot(request, cbot_id):
    """ Query the pandora bot """
    pa_name = cbot.bot_manager.get(pk=cbot_id).pandora_name
    context_instance=RequestContext(request)
    if request.method == 'POST':
        return HttpResponse( pa.bot_talk(pa_name, request.POST['askbot']) )
    return HttpResponse("A query was not correctly sent to the chatbot")

@login_required
def delete_pandora_file(request, cbot_id):
    """ Delete a specific file on the pandora bots system """
    pa_name = cbot.bot_manager.get(pk=cbot_id).pandora_name
    if request.method == 'POST':
        response = pa.bot_delete_file(pa_name, request.POST['filename'])
        return HttpResponse( response ) ### Name of post variable required
    return HttpResponse("We weren't able to retrieve a file instance.")

@login_required
def delete_all_pandora_files(request, cbot_id):
    """ Delete a specific file on the pandora bots system """
    pa_name = cbot.bot_manager.get(pk=cbot_id).pandora_name
    response = pa.bot_delete_all_files(pa_name)
    return HttpResponse(response)


@login_required
def compile_pandora_bot(request, cbot_id):
    """ Additional compilation method """
    pa_name = cbot.bot_manager.get(pk=cbot_id).pandora_name
    response = pa.bot_compile(pa_name)
    return HttpResponse(response)

@login_required
def file_sync_status(request, cbot_id):
    """ Method to determine if files in setup are synced with uploaded files """
    pa_name = cbot.bot_manager.get(pk=cbot_id).pandora_name
    pandora_file_times = get_uploaded_filetimes(cbot_id)
    bot_file_times = get_time_dict(cbot_id)
    response = True
    for key in pandora_file_times:
        if key in bot_file_times:
            if pandora_file_times[key] == bot_file_times[key]:
                pass
            else:
                response = False
                break
        else:
            response = False
            break
    return HttpResponse(response)

def get_uploaded_filetimes(cbot_id):
    bot_object = cbot.bot_manager.get(pk=cbot_id)
    jsonified_files = bot_object.uploaded_files
    log.log_exception(jsonified_files, "retrieve_jsonified.txt")
    file_dictionary = json.loads(jsonified_files)
    log.log_exception(file_dictionary, "unjsonified_dict.txt")
    return file_dictionary



def extract_namelist(file_list):
    """ Extracts names from bot file list """
    namelist = []
    for file in file_list:
        file = os.path.basename(file)
        namelist.append(file)
    return namelist


def extract_timelist(file_list):
    """ Extracts file last modified times from bot file list """
    timelist = []
    for file in file_list:
        time_seconds = os.path.getmtime(file)
        time_struct = time.gmtime(time_seconds)
        #Get time in format Year-Month-Day, Hour:Minutes:Second
        time_formatted = time.strftime("%Y-%m-%d,%H:%M:%S", time_struct)
        timelist.append(time_formatted)
    return timelist

def get_time_dict(cbot_id):
    """ Gets dictionary with keys: file-names, values: file last modified times """
    name_time_dict = {}
    file_list, name_list, time_list = [], [], []

    configurations = cbot.bot_manager.get(pk=cbot_id).get_attached_configurations()
    for n in configurations:
        file_list += n.get_file_paths()
    name_list = extract_namelist(file_list)
    time_list = extract_timelist(file_list)
    for i in range(len(name_list)):
        name_time_dict[name_list[i]] = time_list[i]
    return name_time_dict





################################################################
###################### Debugging Views #########################
### Gavin's views to debug the pandorabots API while it is changed over to a JSON format.


@login_required
def list_pandora_bots(request):
    """ Returns a list obj of all the bots on pandora"""
    response = pa.get_bot_list()
    output = "<br />".join(response)
    return HttpResponse( output )

@login_required
def get_active_files(request, cbot_id):
    """ Returns a list of the current files for a specific bot on pandora """
    pa_name = cbot.bot_manager.get(pk=cbot_id).pandora_name
    response = pa.get_attached_files(pa_name)
    return JsonResponse( response , safe=False)

@login_required
def get_active_files_debug(request, cbot_id):
    """ Returns a list of the current files for a specific bot on pandora """
    pa_name = cbot.bot_manager.get(pk=cbot_id).pandora_name
    response = pa.get_attached_files(pa_name)
    return JsonResponse( response , safe=False)

@login_required
def debug_pandora_bot(request, cbot_id):
    """ Runs the debugging function in the pandora library; simulating a quick talk event """
    pa_name = cbot.bot_manager.get(pk=cbot_id).pandora_name
    response = pa.pandora_debug_bot(pa_name)
    output = ""
    for key in response:
        output += '<li> %s = %s </li>' % (key, response[key])
    return HttpResponse( output )

################################################################
###################### Internal Actions ########################

@login_required
def chatbot_activate_toggle(request, cbot_id): #toggle_chatbot
    """ Toggles the "Enabled" state of chatbot, i.e whether it should be run with cron """
    try:
        chatbot = cbot.twitterbot_manager.get(pk=cbot_id)
        chatbot.enabled = not cbot.twitterbot_manager.get(pk=cbot_id).enabled
        chatbot.save()
        active = cbot.twitterbot_manager.get(pk=cbot_id).enabled
        if active:
            response = "activated"
        else:
            response = "deactivated"
        # And we'll compile here also, just to reduce the onus of responsibility on the user
        pa_name = cbot.twitterbot_manager.get(pk=cbot_id).pandora_name
        pa.bot_compile(pa_name)
        return HttpResponse("Chatbot has been " + response)
    except Exception, e:
        return HttpResponse("The system was unable to toggle bot activity; please contact a system administrator with these details: " + str(e))

@login_required 
def chatbot_get_chatlog(request, cbot_id): #get_chatlog
    try:
        file_location = os.path.join(os.path.dirname(__file__),"script", "chatlogs" , cbot_id,'queriestobot.txt')
        queryfile = open(file_location)
        lines = queryfile.read().replace('\n','<br />')
        return HttpResponse( str( lines) ) 
    except Exception, e:
        return HttpResponse("Chatlog for this bot wasn't found. Check that the chatbot has had active conversations.")


################################################################
###################### Twitter Actions #########################
### Most actions executed in subprocess

@login_required
def check_twitter_auth(request, cbot_id):
    """ Return a user readable response on whether twitter details are active """
    twitter_tk = cbot.twitterbot_manager.get(pk=cbot_id).twit_token
    twitter_tk_s = cbot.twitterbot_manager.get(pk=cbot_id).twit_token_secret
    twitter_c_k = cbot.twitterbot_manager.get(pk=cbot_id).twit_c_key
    twitter_c_s = cbot.twitterbot_manager.get(pk=cbot_id).twit_c_secret
    try:
        import tweepy
        auth = tweepy.OAuthHandler(twitter_c_k, twitter_c_s)
        auth.set_access_token(twitter_tk, twitter_tk_s)
        twitter_api = tweepy.API(auth)
        twitter_api.me()
        return HttpResponse("Success: Your twitter details are valid")
    except Exception,e:
        return HttpResponse("There was a problem; please check the twitter access details. The following may help: \n" + str(e))


################################################################
###################### AIML Wizard #############################

@login_required
def aiml_wizard(request):
    context = { 'aimls' : aiml_file.file_manager.user(request),
                'setup_files' : aiml_config.config_manager.user(request) 
                }
    return render(request, "aimlwizard/aiml_wizard_home.html", context)

@login_required
def file_delete(request, file_id):
    """ Deletes a file """
    try:
        file = aiml_file.file_manager.get(id=file_id)
        filename = aiml_file.file_manager.get(id=file_id).get_simplename
        #Delete from database
        file.delete()
        #Delete from server
        filepath = file.get_path()
        log.log_exception(filepath, "filepath.txt")
        os.remove(filepath)
        #Updating file info on page
        return HttpResponse("File Deleted: " + filename + ".")
    except Exception,e: 
        return HttpResponse("We were unable to delete the file due to an error: " + str(e))

@login_required
def file_delete_all(request):
    """ Deletes all files """
    try:
        #delete files off database
        file = aiml_file.file_manager.user(request).delete()
        #delete files from local server storage
        files = aiml_file.file_manager.user(request).all()
        for file in files:
            os.remove(file.get_path())
        #Updating file info on page
        return HttpResponse("All files deleted.")
    except Exception,e: 
        return HttpResponse("We were unable to delete the files due to an error: " + str(e))


# Not Currently Needed as file management done through admin pages
@login_required
def file_add_new(request):
    """ Adds a new file via text entry """
    if request.method == 'POST':
        form = addFileForm(request.POST)
        if form.is_valid():
            #cbot = form.save(commit=False)
            #cbot.author = request.user
            #cbot.save()
            #form.save_m2m()
            return HttpResponseRedirect('/')
    else:
        form = addFileForm()
    return render(request, 'filemanagement/add_file.html', {'form': form})

################################################################
###################### STATIC PAGES ############################

@log.profile_runspeed
def index(request):
    return render(request, 'index.html')

def twitter_guide(request):
    return render(request, 'information/twitter_guide.html')

def pandora_guide(request):
    return render(request, 'information/what_is_pandora.html')

def playground_guide(request):
    return render(request, 'information/playground_editor.html')

def first_setup_guide(request):
    return render(request, 'information/teacherbot_for_dummies.html')

def get_started(request):
    return render(request, 'information/getting_started.html')

def get_started_old(request):
    return render(request, 'information/getting_started_old.html')

