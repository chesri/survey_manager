
import os, sys, platform, importlib, arcpy
import subprocess

server_dict = {}

# Print the version number for python
arcpy.AddMessage('Python version: ' + platform.python_version())
#arcpy.SetParameter(0,'Python version: ' + platform.python_version())
arcpy.AddMessage("PYTHONPATH:" + os.environ.get('PYTHONPATH'))
# print("PATH:", os.environ.get('PATH'))
server_dict['python_version'] = platform.python_version()
server_dict['python_path'] = os.environ.get('PYTHONPATH')
server_dict['path'] = os.environ.get('PATH')

# print conda info
output = subprocess.check_output("conda list", shell=True, encoding='utf-8')
output = output.split("\n")[0].replace("# packages in environment at ",'')
arcpy.AddMessage(output)
# arcpy.SetParameter(1,output)
server_dict['conda_info'] = output

# Print the Executable that is running the script
arcpy.AddMessage('Executable: ' + sys.executable)
arcpy.AddMessage('Running file'+ __file__)
# arcpy.SetParameter(2,'Executable: ' + sys.executable + "\n" + __file__)
server_dict['executable'] = sys.executable
server_dict['running_file'] = __file__

isXlsxWriter = False if importlib.util.find_spec('xlsxwriter') == None else True
# print('xlswriter Installed: ' + str(isXlsxWriter))
# arcpy.SetParameter(3,'xlswriter Installed: ' + str(isXlsxWriter))
server_dict['xlswriter_installed'] = str(isXlsxWriter)

arcpy.AddMessage('USERNAME: ' + os.environ['USERNAME'])
# arcpy.SetParameter(4,'USERNAME: ' + os.environ['USERNAME'])
server_dict['username'] = os.environ['USERNAME']

# # 5 web
# arcpy.env.workspace = R"C:\arcgisserver\custom\cmcguirevm.sde"
# ws_exists = arcpy.Exists(str(arcpy.env.workspace))
# string=f"Workspace: {arcpy.env.workspace} (exist={ws_exists})"
# arcpy.AddMessage(string)
# # arcpy.SetParameter(5,string)
# server_dict['workspace'] = arcpy.env.workspace
# server_dict['workspace_exists'] = arcpy.Exists(str(arcpy.env.workspace))

# #6 fq
# layer = os.path.join(arcpy.env.workspace,'Yuma22.DBO.survey')
# string=f"{layer} (exists={arcpy.Exists(layer)})"
# arcpy.AddMessage(string)
# # arcpy.SetParameter(6,string)
# server_dict['layer_path'] = layer
# server_dict['layer_path_exists'] = arcpy.Exists(layer)

# #7 not fq
# layer = os.path.join(arcpy.env.workspace,'survey')
# string=f"{layer} (exists={arcpy.Exists(layer)})"
# arcpy.AddMessage(string)
# # arcpy.SetParameter(6,string)
# server_dict['layer_path_fq'] = layer
# server_dict['layer_path_fq_exists'] = arcpy.Exists(layer)
# print(server_dict)

# layer = arcpy.GetParameter(1)
# arcpy.AddMessage(f"layer: {layer} (exists={arcpy.Exists(layer)})")
# server_dict['input_layer'] = layer
# server_dict['input_layer_exist'] = str(arcpy.Exists(layer))
# arcpy.SetParameter(0,server_dict)