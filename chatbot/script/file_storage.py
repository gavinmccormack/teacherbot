from django.core.files.storage import FileSystemStorage
import re

class MyFileStorage(FileSystemStorage):

	# Redefine method
	def get_available_name(self, name):
		# Update files to appropriate 'version', version incremented for each file of same name
		version_number = 0
		while(super(MyFileStorage, self).exists(name)):
			version_number += 1   
			version = '(v' + str(version_number) + ')'
			if(name.find('(') == -1):
				seperator_index = name.rfind('.')
				# Places version number at the end of filename
				name = name[:seperator_index] + str(version) + name[seperator_index:]
			else:
				name = re.sub(r'\(v[0-9]+\)', version, name)
		return name