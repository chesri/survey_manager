#-------------------------------------------------------------------------------
# Name:        gpPrintSurveyMap.py
# Purpose:     Imports an Excel file with formatted GPS data. This ETL process
#              is hardcoded to specific file format.
#
# Author:      chrism
#
# Created:     08/30/2018, updated 5/10/2022
# Copyright:   Esri (c) chrism 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import arcpy, os, sys, tempfile
from arcgis.gis import GIS
import xlrd, re
from xlrd import open_workbook
import configparser

results = []

results.append(f"Running {__file__}; ")

arcpy.env.workspace = R"\\cmcguirevm\custom\cmcguirevm.sde"
desc = arcpy.Describe(arcpy.env.workspace)
ws_type = desc.workspaceType
results.append(f"Workspace set to {arcpy.env.workspace} ({ws_type})")

## Parameter 0 
results.append(f"Param 0 = {arcpy.GetParameterAsText(0)}")

##Parameter 1
results.append(f"Param 1 = {arcpy.GetParameterAsText(1)}")

##Parameter 2
arcpy.SetParameter(2,results) # string messages


