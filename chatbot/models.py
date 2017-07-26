# -*- coding: utf-8 -*-
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib import admin
from django.core.files.base import ContentFile
import os
import re
from teacherbot.settings import MEDIA_ROOT
from .managers import botManager, cbotManager, tbotManager, fileManager, configManager
import random, string
from django.contrib.auth.models import User
from tinymce.models import HTMLField
from script import file_storage
from script import pa_py_api as API
from django.core.validators import RegexValidator
from .validators import validate_pandora_length


mfs = file_storage.MyFileStorage()
class aiml_file(models.Model):
    docfile = models.FileField(storage=mfs, max_length=500)
    text_file = models.TextField(default='', blank=True, verbose_name="File Contents")
    author = models.ForeignKey(User, default=1, related_name='aiml', blank=True)
    file_manager = fileManager()

    def get_path(self):
        """ Return full system path """
        return os.path.join(MEDIA_ROOT, self.docfile.name)

    def __str__(self):              # __unicode__ on Python 2
        return self.docfile.name

    def is_owner(self):
        return self.author

    @property
    def get_filetype(self):
        filename, file_extension = os.path.splitext(self.get_path())
        return file_extension[1:]

    @property
    def get_simplename(self):
        """ The pathless version of the filename with all version numbers stripped"""
        simple_name = os.path.basename(self.docfile.name) 
        simple_name = re.sub(r'\(v[0-9]+\)', '', simple_name)
        return simple_name

    class Meta:
        verbose_name = 'File'

# To do for aiml_file type - on edit, text file should transfer it's content to the docfile.


### AIML Configurations for chatbot
class aiml_config(models.Model):
    title = models.CharField(max_length=100, default='', blank=False)
    last_modified = models.DateTimeField(auto_now_add=True)
    aiml_files = models.ManyToManyField(aiml_file, blank=True,  related_name='AIML_File', verbose_name="Current Setup Files")
    is_public = models.BooleanField('Should be public?', default=False)

    author = models.ForeignKey(User, default=1, related_name='configs', blank=True)
    config_manager = configManager()

    def __str__(self):              # __unicode__ on Python 2
        return self.title

    @property
    def file_counts(self):
        """ Returns a count of all active attached files"""
        return self.aiml_files.count()

    def get_files(self):
        """ Returns all attached files as arrays of files """
        files = self.aiml_files.all()
        return files

    def get_file_paths(self):
        """ Create an archive of the attached files and return the OS path """
        filelist = self.get_files()
        filepaths = []
        for n in range(len(filelist)):
            filepaths = filepaths +  [filelist[n].get_path()]
        return filepaths

    class Meta:
        verbose_name = 'Setup'
        verbose_name_plural = 'Setups'


### The base chatbot model. 
class cbot(models.Model):
    created = models.DateTimeField('Date created',auto_now_add=True)
    title = models.CharField(max_length=100, blank=False, default='')
    pandora_name = models.CharField(max_length=70, default='', unique=True, validators=[
        validate_pandora_length,   
        RegexValidator(regex='^[a-z0-9]+$', message="Only (lowercase) characters a-z and 0-9 are allowed", code="Pandora name can only consist of characters a-z and 0-9.")
        ])
    aiml_config = models.ManyToManyField(aiml_config,related_name='mlconfig',blank=True  ,verbose_name="Active Chatbot Setups") 
    enabled = models.BooleanField('Is enabled?', default=False)
    active_process = False
    author = models.ForeignKey(User, default=1, related_name='chatbots', blank=True)
    twit_hashtags = models.CharField(max_length=200, blank=True, default='',  verbose_name="Hashtags and Keywords")       # Placeholder 
    twit_token = models.CharField(max_length=200, blank=False, default='',  verbose_name="Twitter Access Token", help_text="Stuff")
    twit_token_secret = models.CharField(max_length=200, blank=False, default='',  verbose_name="Twitter Access Token Secret")
    twit_c_key = models.CharField(max_length=200, blank=False, default='',  verbose_name="Twitter Consumer Key")
    twit_c_secret = models.CharField(max_length=200, blank=False, default='',  verbose_name="Twitter Consumer Secret")
    twit_capable = models.BooleanField('Is twitter capable?', default=False)
    

    bot_manager = botManager() # Manager returning all bot objects owned by the user
    
    chatbot_manager = cbotManager() # Manager returning chatbot objects owned
    
    twitterbot_manager = tbotManager() # Manager returning all twitter-capable bots owned
    
    def get_attached_configurations(self):
        """ Get config objects """
        return self.aiml_config.all()

    def save(self, *args, **kwargs):
        super(cbot, self).save(*args, **kwargs)
        app_id = pandora_settings.objects.get().app_id
        user_key = pandora_settings.objects.get().user_key
        host = pandora_settings.objects.get().host
        name = self.pandora_name
        try:
            API.compile_bot(user_key, app_id, host, name)
        except KeyError:
            # If bot is not yet created, keyerror thrown; bot created and compiled
            API.create_bot(user_key, app_id, host, name)

        """ Upload upon saving (possible not needed)

        def get_attached_files(self):
        attached_files = []
        for config in self.get_attached_configurations():
            attached_files += config.get_file_paths()
        return attached_files

        IN save method:
        for file in self.get_attached_files():
            API.upload_file(user_key, app_id, host, name, file)
        API.compile_bot(user_key, app_id, host, name)
        """    
        
        
    def get_attached_config_names(self, join=True):
        """ Get config object title """
        return self.aiml_config.all().values_list('title', flat=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Chatbot Instance'
        verbose_name_plural = 'Chatbots'

def validate_only_one_instance(obj):
    """ Raise validation error if more than one is created """
    model = obj.__class__
    if (model.objects.count() > 0 and
            obj.id != model.objects.get().id):
        raise ValidationError("Can only create 1 %s instance. Please edit the already existing entry. " % model.__name__)


### Singular connection configuration for pandorabots
class pandora_settings(models.Model):
    app_id = models.CharField(max_length=1000)
    user_key = models.CharField(max_length=1000)
    host = models.CharField(max_length=1000)
    def clean(self):
        validate_only_one_instance(self)
    class Meta:
        verbose_name = 'Pandora Settings'
        verbose_name_plural = 'Pandora Settings'

