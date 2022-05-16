#-------------------------------------------------------------------------------
# Name:        WriteSurveyProjectToExcel.py
# Purpose:
#
# Author:      chrism
#
# Python References:
#              https://xlsxwriter.readthedocs.io/
# Created:     21/03/2019
# Copyright:   (c) chrism 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from importlib.util import resolve_name
import arcpy, os, sys, re, pathlib
import xlsxwriter, uuid

results = []

## Parameter 0 
results.append(f"Running {__file__}; ")
results.append(f"Param 0 = {arcpy.GetParameterAsText(0)}")

arcpy.env.workspace = R"\\cmcguirevm\custom\cmcguirevm.sde"
desc = arcpy.Describe(arcpy.env.workspace)
ws_type = desc.workspaceType
results.append(f"Workspace set to {arcpy.env.workspace} ({ws_type})")

arcpy.SetParameter(1,results) # string messages

