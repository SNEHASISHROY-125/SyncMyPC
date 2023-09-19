
import shutil
import glob
import os

zip_file_name = 'sync_my_pc'
files_to_ignore = ['.git','test.py','test.rs','.gitignore','mkZIP.py','__pycache__','LICENSE','sync_my_pc.zip']
# Specify the source and destination directories
source_directory = './'
destination_directory = './folderZ/'
directory_to_zip = destination_directory 

if os.path.exists(destination_directory): 
    # def rec_():
    try:
        shutil.rmtree(destination_directory)
    except PermissionError: ...#shutil.rmtree(destination_directory)
if os.path.exists(file_path_:=os.path.join(zip_file_name,'.zip')): os.remove(file_path_)

# copy dir


# Define a function to ignore specific files or directories
def ignore_function(directory, contents):
    # print('dir',directory,'\n -c',contents)
    # ignored_items = []
    # if contents:print(os.path.isfile(os.path.join(directory,contents[0])))
    # for item in contents:
    #     if item in files_to_iignore:  
    #         ignored_items.append(item)
    return [item for item in contents if item in files_to_ignore] # Ignore files are in ignore list

# Use copytree with the ignore parameter
shutil.copytree(source_directory, destination_directory, ignore=ignore_function)

# Create the ZIP file
shutil.make_archive(zip_file_name, 'zip', directory_to_zip)