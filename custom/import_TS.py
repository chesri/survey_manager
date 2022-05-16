#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      chrism
#
# Created:     29/04/2019
# Copyright:   (c) chrism 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os, sys, re, tempfile
import collections, csv
import datetime
import arcpy

from math import radians, sin, cos
import math
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