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
    fn_dict = {'survey_uid':'surveys','st_uid':'stations','sl_uid':'survey_lines','pt_uid':'survey_points'}
    layer_name = fn_dict[field]
    
    if len(uids) == 1:
        del_expression = f'{field} = {uids[0]}'
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

    arcpy.Delete_management("tmp_layer")
    del layer
    return

# ##############################################################################
# START

arcpy.env.workspace = R"C:\Toolworkbench\survey_manager\custom\cmcguirevm.sde"
surveys = arcpy.ListFeatureClasses("*surveys")
survey_points = arcpy.ListFeatureClasses("*survey_points")
stations = arcpy.ListFeatureClasses("*stations")
survey_lines = arcpy.ListFeatureClasses("*survey_lines")
orientation_sites = arcpy.ListFeatureClasses("*orientation_sites")

arcpy.MakeFeatureLayer_management('surveys','lyr_surveys')
arcpy.MakeFeatureLayer_management('survey_points','lyr_survey_points')
arcpy.MakeFeatureLayer_management('stations','lyr_stations')
arcpy.MakeFeatureLayer_management('survey_lines','lyr_survey_lines')
arcpy.MakeFeatureLayer_management('orientation_sites','lyr_orientation_sites')

survey_id = []

# if confirmation check-box not checked, then bail.
arcpy.AddMessage(f"Executable: {os.path.basename(sys.executable)}")
if os.path.basename(sys.executable) == 'ArcGISPro.exe' or os.path.basename(sys.executable) == 'ArcSOC.exe':
    survey_id = [int(num) for num in arcpy.GetParameter(0).split(',')] if arcpy.GetParameter(0) else [0]

    if not arcpy.GetParameter(1) or arcpy.GetParameter(1) == False:
        arcpy.AddError(f"Did not CONFIRM deletion for {survey_id}. Nothing deleted.")
        exit()

return_message = returnMessages()

for sid in survey_id:

    arcpy.AddMessage(f"Collecting information on survey data for survey_uid={sid}...")
    return_message.addString(f"Deleting survey data for survey_uid={sid}...")

    # use survey ids, to fetch stations, survey points, and survey lines
    expression = f"survey_fk = {sid}"
    station_rows = [row[0] for row in arcpy.da.SearchCursor('lyr_stations',['st_uid'],expression)]
    ptrows = [row[0] for row in arcpy.da.SearchCursor('lyr_survey_points',["pt_uid"],expression)]
    slrows = [row[0] for row in arcpy.da.SearchCursor('lyr_survey_lines',["sl_uid"],expression)]
       
    deleteFeatures('lyr_survey_lines', "sl_uid",slrows)
    deleteFeatures('lyr_survey_points', "pt_uid",ptrows)
    deleteFeatures('lyr_stations', 'st_uid',station_rows)
    deleteFeatures('lyr_surveys', 'survey_uid', [sid])