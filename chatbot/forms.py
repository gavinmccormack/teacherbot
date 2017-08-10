from django.forms import ModelForm, Form, ModelChoiceField, Textarea, ModelMultipleChoiceField, ValidationError, FileField, CharField
from .models import cbot, aiml_config, aiml_file
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib import admin
from script.pandora_actions import create_bot

class chatbot_form(ModelForm):
	class Meta:
		model = cbot
		fields = ['title','pandora_name','aiml_config']
		exclude = ('author','uploaded_files','enabled','twit_hashtags', 'twit_token','twit_token_secret', 'twit_c_key', 'twit_c_secret')
		help_texts = {
		'title': 'A descriptive title that lets you identify your chatbot.',
		'pandora_name' : 'This is the name of your pandora bot. This name must be unique, and is only viewable to yourself; so picking a descriptive name is advised. The name should be all lowercase alphabetic characters - no spaces, underscores, dashes, or other characters will be accepted',
		'aiml_config': 'You will need to assign some of these to your chatbot in order for it to respond to queries',
	  }

class twitterbot_form(ModelForm):
	class Meta:
		model = cbot
		fields = ['twit_hashtags','twit_token',
		'twit_token_secret','twit_c_key','twit_c_secret']
		exclude = ('author','enabled','uploaded_files', 'title', 'pandora_name','aiml_config', 'twit_capable')
		help_texts = {
		'twit_hashtags': 'The hashtags and/or keywords you would like people to use on Twitter to address your chatbot. Hashtags have to be preceded by a "#", keywords can stand alone. You can use more than one hashtag/keyword or a combination of both. If you do so, separate them with a comma, e.g. "#teacherbot_edinburgh, #tb_edinburgh". Please note that keywords and hashtags should be pretty much unique; if you use a hashtag like "#chatbot", your chatbot will reply to all tweets with this hashtag and there will be a lot! Be careful not to spam the users or your application might be blocked by Twitter.',
		'twit_token': 'You receive the Access Token when you create your Twitter App. Paste it here.',
		'twit_token_secret': 'You receive the Access Token Secret when you create your Twitter App. Paste it here.',
		'twit_c_key': 'You receive the Consumer Key when you create your Twitter App. Paste it here.',
		'twit_c_secret': 'You receive the Consumer Secret when you create your Twitter App. Paste it here.',
	  }

		
	#def clean(self):
		#cleaned_data = super(chatbot_form, self).clean()
		#return cleaned_data

	#def clean_pandora_name(self):
		#data = self.cleaned_data['pandora_name']
		#if any(x.isupper() for x in data):
		#		raise ValidationError("The pandora name must be all lowercase alphabetic characters")
		#return data


class PandoraUploadForm(Form):
	upload_archive = FileField(label='Pandora Configuration',required=False, help_text="Upload an archive file in ZIP or RAR format")


class addFileForm(ModelForm):
    	filename = CharField(max_length=100)
    	
	class Meta:
		model = aiml_file
		fields = ['filename', 'docfile']
		labels = { 'docfile' : 'Content'}
		widgets = {
            'docfile': Textarea(attrs={'cols': 80, 'rows': 20}),
        }

	def save(self):
		data = super(ConfigFileForm, self).save(commit=commit)
		fileFormDataLog = open ("fileformlog.txt", "w")
		fileFormDataLog.write(data)
		fileFormDataLog.close()
		return data

