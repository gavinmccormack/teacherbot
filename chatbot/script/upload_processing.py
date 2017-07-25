import os
from . import zipfile
import tempfile
import shutil
from django.core.files import File
from django.http import HttpRequest
from chatbot.models import aiml_file
from . import log
from django.core import management

####################################################################
## Process Archive File - Used in admin.py 
## For uploading setup configurations
## Takes a list of files and returns a list of only chatbot files


# Ensure all files extracted from zip file are of the appropriate chatbot type
def Validate(files):
    valid_files = []
    acceptable_filetypes = ('.aiml', '.set', '.map', '.substitution', '.pdefaults', '.properties')
    for file in files:
        filename, file_extension = os.path.splitext(file)
        if file_extension in acceptable_filetypes:
            valid_files.append(file)
    return valid_files



def get_file_list(parent_dir):
    file_list = []
    for root, directories, filenames in os.walk(parent_dir):
        for filename in filenames:
            file_list.append(os.path.join(root,filename))
    return file_list


# Process any zip files and return a list of all processed files
def Process_Files(files, temp_directory):
    file_list = []
    for file in files:
        filename, file_extension = os.path.splitext(str(file))
        if(file_extension == '.zip'):
            Extract_Zip(file, temp_directory)
        else:
            file_name = filename + file_extension
            file_on_disk = os.path.join(temp_directory, file_name)
            os.chdir(temp_directory)
            with open(file_on_disk, 'w') as f_o_d:
                f_o_d.write(file.read())
        file_list = get_file_list(temp_directory)
        file_list = Validate(file_list)
    return file_list



# Extract zipfiles into temporary directory
def Extract_Zip(file, temp_directory):
    archive = zipfile.ZipFile(file, 'r')
    archive.extractall(temp_directory)

        
# Same functionality as above but casts to django File-object before saving
def Save_Aiml(files, setup, request):
    if(files): # In case archive is filled with innappropriate files
        for file in files:
            with open(file, 'r') as f:
                upload_file = File(f)
                afile = aiml_file(docfile=upload_file, text_file=upload_file.read(), author=request.user)   
                afile.save()
                setup.aiml_files.add(afile)
                upload_file.close()
                os.remove(f.name)
        setup.save()
        


            
        
    
    
    
            

    