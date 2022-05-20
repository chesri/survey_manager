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

tool_path = os.path.dirname(__file__)

arcpy.env.workspace = R"\\ypgrw04xaaa0h57\arcgisserver\SurveyReports\Geodetics.sde" #R"\\cmcguirevm\custom\cmcguirevm.sde"  #

if arcpy.Exists(arcpy.env.workspace):
    desc_ws = arcpy.Describe(arcpy.env.workspace)

    if desc_ws.dataElementType == 'DEWorkspace':
        arcpy.AddMessage('workspace_type: {}'.format(desc_ws.workspaceType))
    elif desc_ws.dataElementType == 'DEFile':
        arcpy.AddMessage('workspace_type: {}'.format(desc_ws.dataElementType))
        arcpy.AddError("Unable to read {} as a DEWorkspace".format(desc_ws.name))
else:
    arcpy.AddMessage("{} not found.".format(arcpy.env.workspace))
    arcpy.AddError("Unable to read Workspace input.")
    exit()

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

    
    return_message.addString("Deleting rows using expression: {}".format(del_expression))
    #arcpy.AddMessage(f"Deleting rows using expression: {del_expression}")

    ## layer = arcpy.MakeFeatureLayer_management(web_layer,'tmp_layer')
    arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION", del_expression)
    recordCt = int(arcpy.GetCount_management(layer).getOutput(0))
    if recordCt > 0:
        arcpy.DeleteFeatures_management(layer)
        #arcpy.AddMessage("Deleted {} rows from {}".format(str(recordCt),layer_name))
        return_message.addString("Deleted {} rows from {} (uid in {})".format(str(recordCt),layer_name,uids))
    else:
        #arcpy.AddMessage("Deleted {} rows from {}".format(str(recordCt),layer_name))
        return_message.addString("Deleted {} rows from {} (uid in {})".format(str(recordCt),layer_name,uids))            

    # arcpy.Delete_management("tmp_layer")
    del layer
    return

# ##############################################################################
# START
survey_id = []

# if confirmation check-box not checked, then bail.
arcpy.AddMessage("Executable: {}".format(os.path.basename(sys.executable)))
if os.path.basename(sys.executable) == 'ArcGISPro.exe' or os.path.basename(sys.executable) == 'ArcSOC.exe':
    survey_id = [int(num) for num in arcpy.GetParameter(0).split(',')] if arcpy.GetParameter(0) else [0]

    if not arcpy.GetParameter(1) or arcpy.GetParameter(1) == False:
        arcpy.AddMessage("*"*80)
        arcpy.AddMessage("Did not CONFIRM deletion for {}. Nothing deleted.".format(survey_id))
        arcpy.AddMessage("*"*80)
        exit()

return_message = returnMessages()

for sid in survey_id:

    arcpy.AddMessage("Collecting information on survey data for survey_uid={}...".format(sid))
    return_message.addString("Deleting survey data for survey_uid={}...".format(sid))

    # use survey ids, to fetch stations, survey points, and survey lines
    expression = "survey_fk = {}".format(sid)
    station_rows = [row[0] for row in arcpy.da.SearchCursor('lyr_stations',['st_uid'],expression)]
    ptrows = [row[0] for row in arcpy.da.SearchCursor('lyr_survey_points',["pt_uid"],expression)]
    slrows = [row[0] for row in arcpy.da.SearchCursor('lyr_survey_lines',["sl_uid"],expression)]
       
    deleteFeatures('lyr_survey_lines', "sl_uid",slrows)
    deleteFeatures('lyr_survey_points', "pt_uid",ptrows)
    deleteFeatures('lyr_stations', 'st_uid',station_rows)
    deleteFeatures('lyr_surveys', 'survey_uid', [sid])

    del station_rows, ptrows, slrows
    arcpy.Delete_management('lyr_survey_lines')
    arcpy.Delete_management('lyr_survey_points')
    arcpy.Delete_management('lyr_stations')
    arcpy.Delete_management('lyr_surveys')

    arcpy.SetParameter(2,return_message.printString())