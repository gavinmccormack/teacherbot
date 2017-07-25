from django.core.exceptions import ValidationError
import string

def validate_pandora_length(name):
	if(len(name) < 3 or len(name) > 64):
		raise ValidationError("Botnames must be between 3 and 64 characters long")

