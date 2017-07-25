from django.contrib import admin
from .models import cbot, aiml_config, pandora_settings , aiml_file
from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from multiupload.fields import MultiFileField
from django.db import models
from teacherbot.settings import MEDIA_ROOT
from script import upload_processing
import os
import zipfile
import tempfile
import shutil

from chatbot.script import log


class cbot_admin(admin.ModelAdmin):
	exclude = ('author',)

	def response_delete(self, request, obj, post_url_continue=None):
		""" Redirect on delete actions """
		return HttpResponseRedirect("/")


class ConfigFileForm(forms.ModelForm):
	fields = ['attachments']
	model = aiml_config
	attachments = MultiFileField( max_file_size=1024*1024*20, content_types=('.zip', '.aiml', '.set', '.map', '.substitution', '.pdefaults', '.properties'), help_text="Upload files or drag and drop here. Max number of files in one upload is 65.") ## Create an additional field for multi-files

	# Config_instance added to allow easier use in ModelAdmin; may be bad practice.
	def __init__(self, *args, **kwargs):
		super(ConfigFileForm, self).__init__(*args, **kwargs)
		self.fields['attachments'].required = False
		self.fields['attachments'].label = "Upload Files To Setup"
		self.config_instance = self.instance.id		  ## Attempting to pass instance/ID
		
	def save(self, commit=True):
		return super(ConfigFileForm, self).save(commit=commit)




class config_admin(admin.ModelAdmin):
	exclude = ('author',)
	form = ConfigFileForm
	fieldsets = (
		(None, {
			'fields': ('title', 'aiml_files', 'attachments'),
		}),
	)


	### Redirections
	def response_add(self, request, obj, post_url_continue=None):
		""" Redirect on admin actions """
		return HttpResponseRedirect(reverse('aiml_wizard'))

	def response_change(self, request, obj, post_url_continue=None):
		""" Redirect on change actions """	
		return HttpResponseRedirect(reverse('aiml_wizard'))

	def response_delete(self, request, obj, post_url_continue=None):
		""" Redirect on delete actions """
		return HttpResponseRedirect(reverse('aiml_wizard'))



	# Save model. First method run on save action
	def save_model(self, request, obj, form, change):
		""" Ensure author is equal to user """		
		if not change:
			obj.author = request.user
		obj.save()


	# Save related - Create the config if not existing, and then add uploaded files to config
	def save_related(self, request, form, formsets, change):
		""" Save form data as aiml_file, then attach to aiml_config instance """
		super(config_admin, self).save_related(request, form, formsets, change)
		attachments = form.cleaned_data.get('attachments', None)  ## Taken from "ConfigFileForm"
		afile = []
		if not hasattr(form.instance, 'pk'):
			setup = aiml_config.config_manager.create(title=request.POST['title'])
		else:
			setup = aiml_config.config_manager.get(id=form.instance.pk)
		if attachments is not None:
			tempfile.tempdir = "/home/teacherdev/public_html/tb_development/teacherbot/files/temp"
			temp_location = tempfile.mkdtemp()
			processed_files = upload_processing.Process_Files(attachments, temp_location)
			upload_processing.Save_Aiml(processed_files, setup, request)
			shutil.rmtree(temp_location) # Cleanup temporary folder

	
	# Limit the queryset of the aiml_files available to only the user's
	def formfield_for_manytomany(self, db_field, request, **kwargs):
		if db_field.name == "aiml_files":
			 kwargs["queryset"] = aiml_file.file_manager.filter(author=request.user)
		return super(config_admin, self).formfield_for_foreignkey(db_field, request, **kwargs)


	# Function runs on individual object pages, and indexes. To cover this if there is no object(i.e index) then permissions are automatically granted.
	def has_change_permission(self, request, obj=None):
		if obj:
			if obj.author == request.user:
				return True
			else:
				return False
		else:
			return True 



class file_admin(admin.ModelAdmin):
	exclude = ('author','docfile',)

	def save_model(self, request, obj, form, change):
		""" If new then creator is owner """
		if not change:
			obj.author = request.user
		if change:
			filepath = os.path.join(MEDIA_ROOT, obj.docfile.name)
			newfile = open(filepath, 'w')
			newfile.write(request.POST['text_file'])
			newfile.close()
		obj.save()

	def queryset(self, request):
		if request.user.is_superuser:
			return Entry.objects.all()
		return Entry.objects.filter(author=request.user)

	### Redirections
	def response_add(self, request, obj, post_url_continue=None):
		""" Redirect on admin actions """
		return HttpResponseRedirect("/chatbot/file-manager/")

	def response_change(self, request, obj, post_url_continue=None):
		""" Redirect on change actions """	
		return HttpResponseRedirect("/chatbot/file-manager/")

	def response_delete(self, request, obj, post_url_continue=None):
		""" Redirect on delete actions """
		return HttpResponseRedirect("/chatbot/file-manager/")


class HideIndex(admin.ModelAdmin):
	def get_model_perms(self, request):
		"""
		Return empty perms dict thus hiding the model from admin index if you desire
		"""
		return {}


## Add to django admin menu
admin.site.register(cbot, cbot_admin)
admin.site.register(aiml_config, config_admin)
admin.site.register(pandora_settings)
admin.site.register(aiml_file, file_admin)
