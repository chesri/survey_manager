
import os, sys, platform, importlib, arcpy
import subprocess

server_dict = {}

# Print the version number for python
arcpy.AddMessage('Python version: ' + platform.python_version())
server_dict['python_version'] = platform.python_version()
arcpy.AddMessage("PYTHONPATH: " + str(os.environ.get('PYTHONPATH')))
server_dict['python_path'] = os.environ.get('PYTHONPATH')
#server_dict['path'] = os.environ.get('PATH')

# print conda info
output = subprocess.check_output("conda list", shell=True, encoding='utf-8')
output = output.split("\n")[0].replace("# packages in environment at ",'')
arcpy.AddMessage(output)
server_dict['conda_info'] = output

# Print the Executable that is running the script
arcpy.AddMessage('Executable: ' + sys.executable)
arcpy.AddMessage('Running file'+ __file__)
server_dict['executable'] = sys.executable
server_dict['running_file'] = __file__

# Test for xlsxwriter in python env
isXlsxWriter = False if importlib.util.find_spec('xlsxwriter') == None else True
server_dict['xlswriter_installed'] = str(isXlsxWriter)

# show user name that is running the tool
arcpy.AddMessage('USERNAME: ' + os.environ['USERNAME'])
server_dict['username'] = os.environ['USERNAME']

# check workspace
arcpy.env.workspace = R"cmcguirevm.sde"
server_dict['workspace'] = arcpy.env.workspace
if os.path.exists(arcpy.env.workspace):
    server_dict['workspace_type'] = arcpy.Describe(arcpy.env.workspace).workspaceType
else:
    server_dict['workspace_type'] = f"{arcpy.env.workspace} not found."

# check layer access
layer = arcpy.GetParameter(1)
if layer:
    arcpy.Exists(layer)
    desc = arcpy.Describe(layer)
    server_dict['layer_name'] = desc.name
    server_dict['layer_featureType'] = desc.datatype
# server_dict['layer_path_exists'] = arcpy.Exists(layer)

for line in server_dict.keys():
    print(f"{line}: {server_dict[line]}")
arcpy.SetParameter(0,server_dict)