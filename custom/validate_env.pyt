# -*- coding: utf-8 -*-

import arcpy
import os, sys, platform, importlib, arcpy
import subprocess


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [ValidateWorkspace,ValidateConda]


class ValidateWorkspace(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Validate Workspace"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        '''https://pro.arcgis.com/en/pro-app/latest/arcpy/classes/parameter.htm'''
        ws = arcpy.Parameter(
            name='in_workspace',
            displayName='Input Workspace',
            datatype='DEWorkspace',
            direction='Input',
            parameterType='Required')

        params = [ws]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        arcpy.env.workspace = parameters[0].value
        workspace = parameters[0].value
        desc_ws = arcpy.Describe(workspace)

        if arcpy.Exists(workspace):
            string = "Workspace " + desc_ws.name + " exist."
            arcpy.AddMessage(string)
        
            string = "Workspace dataElementType = " + desc_ws.dataElementType
            arcpy.AddMessage(string)

            if desc_ws.dataElementType == 'DEWorkspace':
                if len(arcpy.ListFeatureClasses()) > 0:
                    string = "Found " + str(len(arcpy.ListFeatureClasses())) + " feature classes."
                    arcpy.AddMessage(string)
                    for fc in arcpy.ListFeatureClasses():
                        desc_fc = arcpy.Describe(fc)
                        arcpy.AddMessage(desc_fc.name)
                        out_fc = arcpy.ValidateTableName(fc, workspace)
                        arcpy.AddMessage(out_fc)
                else:
                    string = "Could not get list of Feature Classes. Check privileges on datasets."
                arcpy.AddMessage(string)


        else:
            string = "{} not found.".format(arcpy.env.workspace)
            arcpy.AddError("Unable to read Workspace input.")

        return


class ValidateConda(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Validate Conda Env"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        '''https://pro.arcgis.com/en/pro-app/latest/arcpy/classes/parameter.htm'''
        param0 = arcpy.Parameter(
            name='conda_path',
            displayName='Path to Conda',
            datatype='DEFolder',
            direction='Input',
            parameterType='Required')

        param0.value  = R"C:\Program Files\ArcGIS\Server\framework\runtime\ArcGIS\bin\Python\Scripts"
        params = [param0]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        conda_path = parameters[0].valueAsText
        conda_exe = os.path.join(conda_path,'conda.exe')
        if not os.path.exists(conda_path):
            arcpy.AddError("Invalid path. ")
        elif os.path.exists (conda_exe):
            
            # print conda info
            output = subprocess.check_output("conda list", shell=True, encoding='utf-8')
            #output = output.split("\n")[0].replace("# packages in environment at ",'')
            arcpy.AddMessage(output)
        else:
            arcpy.AddMessage("Did not find conda.exe at the path entered. {}".format(conda_exe))

        return

