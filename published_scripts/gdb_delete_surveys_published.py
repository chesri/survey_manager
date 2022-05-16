# Esri start of added imports
import sys, os, arcpy
# Esri end of added imports

# Esri start of added variables
g_ESRI_variable_1 = 'f\'{field} = {uids"0"}\''
g_ESRI_variable_2 = os.path.join(arcpy.env.packageWorkspace,'E:\\arcgisserver\\directories\\arcgissystem\\arcgisinput\\Surveys\\deletesurveydata.GPServer\\extracted\\p20\\Geodetics.sde\\Geodetics.DBO.surveys')
g_ESRI_variable_3 = 'lyr_surveys'
g_ESRI_variable_4 = os.path.join(arcpy.env.packageWorkspace,'\\\\ypgrw04xaaa0h57\\arcgisserver\\SurveyReports\\Geodetics.sde\\Geodetics.DBO.survey_points')
g_ESRI_variable_5 = 'lyr_survey_points'
g_ESRI_variable_6 = os.path.join(arcpy.env.packageWorkspace,'\\\\ypgrw04xaaa0h57\\arcgisserver\\SurveyReports\\Geodetics.sde\\Geodetics.DBO.stations')
g_ESRI_variable_7 = 'lyr_stations'
g_ESRI_variable_8 = os.path.join(arcpy.env.packageWorkspace,'\\\\ypgrw04xaaa0h57\\arcgisserver\\SurveyReports\\Geodetics.sde\\Geodetics.DBO.survey_lines')
g_ESRI_variable_9 = 'lyr_survey_lines'
g_ESRI_variable_10 = os.path.join(arcpy.env.packageWorkspace,'\\\\ypgrw04xaaa0h57\\arcgisserver\\SurveyReports\\Geodetics.sde\\Geodetics.DBO.orientation_sites')
g_ESRI_variable_11 = 'lyr_orientation_sites'
# Esri end of added variables

#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      chrism
#
# Created:     15/04/2019
# Copyright:   (c) chrism 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import arcpy
import os, sys
import configparser
class returnMessages:
    '''class to store messages that will be returned to user at end of run.'''
    def __init__(self):
        self.id = 0
        self.messages = []
    def addString(self,string):
        self.messages.append(string)
    def printString(self):
        return '\n'.join(self.messages)
def deleteFeatures(layer,field,uids):
    fn_dict = {'survey_uid':g_ESRI_variable_2,'st_uid':g_ESRI_variable_6,'sl_uid':g_ESRI_variable_8,'pt_uid':g_ESRI_variable_4}
    layer_name = fn_dict[field]
    
    if len(uids) == 1:
        del_expression = g_ESRI_variable_1
    elif len(uids) > 1:
        tupids = tuple(id for id in uids)
        del_expression = f'{field} in {tupids}'
    else:
        return
    
    return_message.addString(f"Deleting rows using expression: {del_expression}")
    #arcpy.AddMessage(f"Deleting rows using expression: {del_expression}")
    ## layer = arcpy.MakeFeatureLayer_management(web_layer,'tmp_layer')
    arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION", del_expression)
    recordCt = int(arcpy.GetCount_management(layer).getOutput(0))
    if recordCt > 0:
        arcpy.DeleteFeatures_management(layer)
        #arcpy.AddMessage("Deleted {} rows from {}".format(str(recordCt),layer_name))
        return_message.addString(f"Deleted {str(recordCt)} rows from {layer_name} (uid in {uids})")
    else:
        #arcpy.AddMessage("Deleted {} rows from {}".format(str(recordCt),layer_name))
        return_message.addString(f"Deleted {str(recordCt)} rows from {layer_name} (uid in {uids})")            
    #arcpy.Delete_management("tmp_layer")
    del layer
    return
# ##############################################################################
# START
arcpy.env.workspace = arcpy.env.packageWorkspace
surveys = arcpy.ListFeatureClasses("*surveys")
survey_points = arcpy.ListFeatureClasses("*survey_points")
stations = arcpy.ListFeatureClasses("*stations")
survey_lines = arcpy.ListFeatureClasses("*survey_lines")
orientation_sites = arcpy.ListFeatureClasses("*orientation_sites")
arcpy.MakeFeatureLayer_management(g_ESRI_variable_2,g_ESRI_variable_3)
arcpy.MakeFeatureLayer_management(g_ESRI_variable_4,g_ESRI_variable_5)
arcpy.MakeFeatureLayer_management(g_ESRI_variable_6,g_ESRI_variable_7)
arcpy.MakeFeatureLayer_management(g_ESRI_variable_8,g_ESRI_variable_9)
arcpy.MakeFeatureLayer_management(g_ESRI_variable_10,g_ESRI_variable_11)
survey_id = []
# if confirmation check-box not checked, then bail.
arcpy.AddMessage(f"Executable: {os.path.basename(sys.executable)}")
if os.path.basename(sys.executable) == 'ArcGISPro.exe' or os.path.basename(sys.executable) == 'ArcSOC.exe':
    survey_id = [int(num) for num in arcpy.GetParameter(0).split(',')] if arcpy.GetParameter(0) else [0]
    if not arcpy.GetParameter(1) or arcpy.GetParameter(1) == False:
        arcpy.AddMessage(f"Did not CONFIRM deletion for {survey_id}. Nothing deleted.")
        exit()
return_message = returnMessages()
for sid in survey_id:
    arcpy.AddMessage(f"Collecting information on survey data for survey_uid={sid}...")
    return_message.addString(f"Deleting survey data for survey_uid={sid}...")
    # use survey ids, to fetch stations, survey points, and survey lines
    expression = f"survey_fk = {sid}"
    station_rows = [row[0] for row in arcpy.da.SearchCursor(g_ESRI_variable_7,['st_uid'],expression)]
    ptrows = [row[0] for row in arcpy.da.SearchCursor(g_ESRI_variable_5,["pt_uid"],expression)]
    slrows = [row[0] for row in arcpy.da.SearchCursor(g_ESRI_variable_9,["sl_uid"],expression)]
       
    deleteFeatures('lyr_survey_lines', "sl_uid",slrows)
    deleteFeatures('lyr_survey_points', "pt_uid",ptrows)
    deleteFeatures('lyr_stations', 'st_uid',station_rows)
    deleteFeatures('lyr_surveys', 'survey_uid', [sid])

