
import os, sys, platform, importlib, arcpy
import subprocess

server_dict = {}
layer = arcpy.GetParameter(0)

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
arcpy.env.workspace = os.path.dirname(layer)
desc_ws = arcpy.Describe(arcpy.env.workspace)

server_dict['workspace'] = arcpy.env.workspace

if arcpy.Exists(arcpy.env.workspace):

    server_dict['dataElementType'] = desc_ws.dataElementType

    if desc_ws.dataElementType == 'DEWorkspace':
        server_dict['workspace_type'] = desc_ws.workspaceType
        fc_count = len(arcpy.ListFeatureClasses())

        if fc_count > 0:
            server_dict['fc_count'] = fc_count
            fcs = [fc for fc in arcpy.ListFeatureClasses()]
            server_dict['fcs'] = fcs
        else:
            server_dict['fc_count'] = fc_count
            server_dict['fcs'] = []
else:
    string = "{} not found.".format(arcpy.env.arcpy.env.workspace)
    arcpy.AddError("Unable to read Workspace input.")

# check layer access
if layer:
    arcpy.Exists(layer)
    desc = arcpy.Describe(layer)
    server_dict['layer_name'] = desc.name
    server_dict['layer_featureType'] = desc.datatype
# server_dict['layer_path_exists'] = arcpy.Exists(layer)

for line in server_dict.keys():
    print("{}: {}".format(line,server_dict[line]))
arcpy.SetParameter(1,server_dict)