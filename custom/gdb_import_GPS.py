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


tool_path = os.path.dirname(sys.argv[0])
results = []

runfrom = os.path.basename(sys.executable)
arcpy.AddMessage('Executable: ' + os.path.basename(sys.executable))

arcpy.env.workspace = arcpy.GetParameter(4)
if arcpy.env.workspace == None:
    arcpy.env.workspace = os.path.join(tool_path, "cmcguirevm.sde")
desc_ws = arcpy.Describe(arcpy.env.workspace)
results.append(str(desc_ws.dataElementType))

if len(arcpy.ListFeatureClasses("*surveys")) > 0:
    surveys = arcpy.ListFeatureClasses("*surveys")[0]
    surveys = os.path.join(arcpy.env.workspace,surveys)
    arcpy.MakeFeatureLayer_management(surveys,'lyr_surveys')
    #surveys = 'lyr_surveys'
    results.append(f'surveys st to {surveys}')
else:
    arcpy.AddError(f"Exiting tool. Could not access {os.path.join(arcpy.env.workspace),'surveys'}")

if len(arcpy.ListFeatureClasses("*survey_points")) > 0:
    survey_points = arcpy.ListFeatureClasses("*survey_points")[0]
    survey_points = os.path.join(arcpy.env.workspace,survey_points)
    arcpy.MakeFeatureLayer_management(surveys,'lyr_survey_points')
    #survey_points = 'lyr_survey_points'
    results.append(f'survey_points st to {survey_points}')
else:
    arcpy.AddError(f"Exiting tool. Could not access {os.path.join(arcpy.env.workspace),'survey_points'}")

def getID(in_table, in_field):
    ''' increment by number of 1 to the largest number value in the table's
    field to derive a unique and sequence ID. Return ID.'''

    if not arcpy.Exists(in_table):
        arcpy.AddMessage("Table does not exist. Check workspace environment setting.")
        return None

    fields = arcpy.ListFields(in_table)
    for f in fields:
        if f.name == in_field:
            field = f

    if field.type == 'Integer':

        expression = '{} > 0'.format(field.name)
        sql_clause = (None,'ORDER BY {}'.format(field.name))

        rows = [row[0] for row in arcpy.da.SearchCursor(in_table, [field.name],where_clause=expression,sql_clause=sql_clause)]
        if len(rows) > 0:
            pid = max(rows) + 1
        else:
            pid = 1

        return pid

    arcpy.AddMessage("GetID returning {}".format(None))
    return None

def readSource(input_book):
    book = open_workbook(filename=input_book)

    for name in book.sheet_names():
        if name == 'Data':
            sheet = book.sheet_by_name(name)

            # validate that the worksheet has necessary columns using correct headers
            # first, find the header column by searching for 'POINT ID'
            # (added 8/3/2020)
            search_pointID = [sheet.row(row)[0].value for row in range(sheet.nrows)]
            rowindex = search_pointID.index("POINT ID")
            start_gps_data_row = rowindex + 1

            bail = False
            headers = ['POINT ID','NORTHING','EASTING','ORTHO HT','LATITUDE','LONGITUDE','ELLIP HT','X','Y','3D CQ','DATE / TIME','COMMENTS']
            cols = ['A', 'B','C','D','E','F','G','H','I','J','K','L','M']
            for c,head in enumerate(headers):
                if c == sheet.ncols:
                    break
                if sheet.cell_value(rowx=rowindex,colx=c) != head:
                    arcpy.AddError("GPS Excel doesn't have expected column headers or formatting.")
                    arcpy.AddError("Expected {} in column {}".format(head,cols[c]))
                    bail = True
            if bail:
                exit()

            #
            #
            # pull mission metadata from first rows; applies to all data in sheet
            #
            classification    = sheet.cell_value(rowx=1, colx=0)      ## sheet.row(1)[0].value
            title             = sheet.cell_value(rowx=4, colx=0)      ## sheet.row(4)[0].value
            report_status     = sheet.row(1)[sheet.ncols - 1].value
            project           = sheet.cell_value(rowx=6, colx=1)      ## sheet.row(6)[1].value
            site              = sheet.cell_value(rowx=7, colx=1)      ## sheet.row(7)[1].value
            poc               = sheet.cell_value(rowx=8, colx=1)      ## sheet.row(8)[1].value
            date              = sheet.cell_value(rowx=9, colx=1)      ## sheet.row(9)[1].value
            survey_crew       = sheet.cell_value(rowx=10, colx=1)     ## sheet.row(10)[1].value
            grid              = sheet.cell_value(rowx=11, colx=1)     ## sheet.row(11)[1].value
            unit              = sheet.cell_value(rowx=12, colx=1)
            source_file       = os.path.basename(input_book)
            source_status     = sheet.cell_value(rowx=1, colx=sheet.ncols - 1)     ## sheet.row(1)[11].value
            addl_contacts     = 'No Additional Contacts'

            if sheet.row(7)[sheet.ncols - 1].value != '':
                addl_contacts = sheet.row(7)[sheet.ncols - 1].value + '; ' + sheet.row(8)[sheet.ncols - 1].value + '; ' + sheet.row(9)[sheet.ncols - 1].value + '; ' + sheet.row(10)[sheet.ncols - 1].value

            surveyID = getID(fc_surveys,'survey_uid')
            arcpy.AddMessage(f"getPID returning ID {surveyID} for {fc_surveys}")
            survey_info = (surveyID, project, title, classification, site, poc, date, survey_crew, grid, unit, source_file, source_status, addl_contacts)

            #
            # set-up to loop through data
            #

            data = []      # an empty list to collect the point data in.
            point_pid = getID(fc_points,'pt_uid')  # get the starting unique ID for the Points.
            

            headers = []   # collect a list of headers to determine if user is importing a file with extra columns
            # ("for" modified 8/3/2020)
            for header in sheet.row(rowindex):
                headers.append(header.value)

            # we read through entire file, but when we reach "start_gps_data_row", we start reading in as "data"
            while rowindex < sheet.nrows:
                cells = sheet.row(rowindex)
                row = []
                b = []

                # Only collect data if in the data section, there is a value in "POINT ID" column (0), and YPG X/Y coords (col 7 & 8), otherwise skip.
                if rowindex >= start_gps_data_row and cells[0].value != "" and cells[7].value != "" and cells[8].value != "":

                    pt_uid          = point_pid                            ## Increments at end of loop, by 1, for each data row
                    pt_name         = sheet.row(rowindex)[0].value         ## Excel Col "A"
                    northing        = sheet.row(rowindex)[1].value         ## Excel Col "B"
                    easting         = sheet.row(rowindex)[2].value         ## Excel Col "C"
                    ortho_ht        = sheet.row(rowindex)[3].value if isinstance(sheet.row(rowindex)[3].value, float) else 0.0         ## Excel Col "D"
                    wgs84_y         = re.sub('[^A-Za-z0-9.]+', ' ', sheet.row(rowindex)[4].value) ## Excel Col "E"
                    if wgs84_y[-2:] == ' N':
                        wgs84_y     = wgs84_y[:-2]
                    wgs84_x = re.sub('[^A-Za-z0-9.]+', ' ', sheet.row(rowindex)[5].value) ## Excel Col "F"
                    if wgs84_x[-2:] == ' W':
                        wgs84_x     = '-' + wgs84_x[:-2]
                    ellip_ht        = sheet.row(rowindex)[6].value if isinstance(sheet.row(rowindex)[6].value, float) else 0.0          ## Excel Col "G"
                    ypg_x           = sheet.row(rowindex)[7].value         ## Excel Col "H"
                    ypg_y           = sheet.row(rowindex)[8].value         ## Excel Col "I"
                    cq3d            = sheet.row(rowindex)[9].value         ## Excel Col "J"
                    # dtg - modified 8/3/2020
                    dtg             = sheet.row(rowindex)[10].value if sheet.row(rowindex)[10].ctype != 0 else None
                    comments        = sheet.row(rowindex)[11].value        ## Excel Col "L"

                    # If user enters data beyond column "L", the aggregate the data and add it to Comments.
                    if len(headers) > 11:
                        for hIndex in range(12, len(headers)):
                            print(hIndex, sheet.row(rowindex)[hIndex])
                            if str(sheet.row(rowindex)[hIndex].value) != '':
                                if comments == '':
                                    comments += headers[hIndex] + ': ' + str(sheet.row(rowindex)[hIndex].value)
                                else:
                                    comments += '; ' + headers[hIndex] + ': ' + str(sheet.row(rowindex)[hIndex].value)


                    # next, with the values stored in variables, create a variable with the field values in the order we'll use to load into database.
                    point_data = (surveyID, pt_uid, 'gps', pt_name, dtg, ypg_x, ypg_y, wgs84_x, wgs84_y, northing, easting, ortho_ht, ellip_ht, cq3d, comments)

                    # write the new row of data to our data object with append method
                    data.append(point_data)

                    arcpy.AddMessage(f"getPID returning ID {point_pid} for {fc_points}")
                    point_pid += 1
                rowindex = rowindex + 1

    return survey_info, data

class aSurvey:
    def __init__(self,prj_data):
        self.id              = prj_data[0]   ## survey ID
        self.name            = prj_data[1]   ## survey name
        self.classification  = prj_data[3]   ## classification
        self.title           = prj_data[2]   ## title
        self.program         = prj_data[1]   ## project
        self.site            = prj_data[4]   ## site
        self.date            = prj_data[6]   ## date
        self.poc             = prj_data[5]   ## poc
        self.instrument_type = 'GPS'
        self.instrument_sn   = 'NA'
        self.surveyor        = prj_data[7]   ## survey_crew
        self.reference       = ''
        self.grid            = prj_data[8]   ## grid
        self.uom             = prj_data[9]   ## unit
        self.source_file     = prj_data[10]  ## source_file
        self.source_status   = 'Draft'  ## source_status
        self.assignment_fk   = -999
        self.review_status   = 'draft'
        self.reviewer        = ''
        self.review_date     = None
        self.addl_contacts   = prj_data[12]  ## addl_contacts
        self.path            = ''
        self.table_fields    = ['survey_uid', 'name', 'classification', 'program', 'site', 'date', 'poc', 'instrument_type', 'instrument_sn', 'surveyor', 'reference', 'grid', 'uom', 'source_file', 'source_status', 'assignment_fk', 'review_status', 'reviewer', 'review_date','SHAPE@']
        self.points = []

    def listSurvey(self):
        '''returns a list object containing an order list of data to be loaded into database table '''
        # create an ordered list of project metadata - ordered according to the database schema/columns
        listAttributes = [self.id,
            self.name,
            self.classification,
            self.program,
            self.site,
            self.date,
            self.poc,
            self.instrument_type,
            self.instrument_sn,
            self.surveyor,
            self.reference,
            self.grid,
            self.uom,
            self.source_file,
            self.source_status,
            self.assignment_fk,
            self.review_status,
            self.reviewer,
            self.review_date
            ]
        return listAttributes

    def createSurveyRectangle(self):
        tmp_name = 'xxPrj_' + os.path.basename(tempfile.mktemp())
        output = os.path.join("in_memory",tmp_name)
        arcpy.MinimumBoundingGeometry_management(self.points,output,"ENVELOPE")
        rows = [row for row in arcpy.da.SearchCursor(output,['SHAPE@'])]
        self.shape = rows[0][0]

        return self.shape

# ##############################################################################
# START
# ##############################################################################

# Parameter 0: is the "Input Total Station File" or source file for the GPS data.
# tool expects an Excel file.
source = arcpy.GetParameterAsText(0)
if arcpy.GetParameterAsText(0) == None or arcpy.GetParameterAsText(0) == '':
    source = R"C:\ToolWorkbench\yuma-range-survey\sample_data\GP15_PGM4_23APR2018.xls"

# Parameter 1: Assignment ID captures an assignment number and includes it with
#              the survey file to link an assignment with the resulting survey.
assignment_id = arcpy.GetParameter(1)
if assignment_id == '' or assignment_id == None:
    assignment_id = -421

# Parameter 2 = Result messages (set at end with SetParameter)
# Parameter 3 = zoom-to/output polygon (set at end with SetParameter)

fc_surveys = surveys  # 'lyr_surveys'
fc_points  = survey_points  # 'lyr_survey_points'

#output_string = str("Workspace: {}".format(arcpy.env.workspace))
results.append(str(f"fc_surveys: {fc_surveys}"))
results.append(str(f"fc_points: {fc_points}"))

  # Set Tool Environment
arcpy.env.overwriteOutput = True
dirty_laundry = []   # throw intermediate items in here for laundering at end.

# Read the file to obtain Project Metadata into aSurvey class object.
survey_info, data = readSource(source)
the_survey = aSurvey(survey_info)

# Set Spatial Reference based on grid value.
# probably don't need to establish Spatial Reference since the target feature class is already YPG grid and we'll use YPG grid coordinates to place the points.
datum = the_survey.grid
ypg_sr = R"PROJCS['NAD27_YUMA_PROVING_GROUND',GEOGCS['GCS_North_American_1927',DATUM['D_North_American_1927',SPHEROID['Clarke_1866',6378206.4,294.9786982]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',84738.012],PARAMETER['False_Northing',-175814.044],PARAMETER['Central_Meridian',-113.75],PARAMETER['Scale_Factor',0.999933333],PARAMETER['Latitude_Of_Origin',31.0],UNIT['Meter',1.0]];-6100292.49622249 -14607719.0234388 409368153.975199;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision"
sr = arcpy.SpatialReference()
sr.loadFromString(ypg_sr)
use_x = 5
use_y = 6
# #########################################
# Add the Survey Data the survey_points feature class.
try:

    point_fields = ["survey_fk", "pt_uid", "pt_type", "pt_name", "date_time", "ypg_x", "ypg_y", "wgs84_x", "wgs84_y", "gps_northing", "gps_easting", "gps_ortho_ht",  "gps_ellip_ht", "gps_cq3d","comments","SHAPE@"]

    d_cursor =  arcpy.da.InsertCursor(fc_points,point_fields)
    for row in data:
        point = arcpy.Point(row[use_x],row[use_y])
        ptGeometry = arcpy.PointGeometry(point)
        the_survey.points.append(ptGeometry)
        r = list(row)
        r.append(point)

        d_cursor.insertRow(r)

    del d_cursor
    results.append("; " +  "Survey Data added to tmp_survey.")

except RuntimeError as e:
    results.append("; " + str(e))
    arcpy.AddMessage(output_string)
except arcpy.ExecuteError as e:
    results.append("; " + arcpy.GetMessage(2))
    results.append("; " + str(e))
    arcpy.AddMessage(output_string)
except Exception as e:
    results.append("; Exception Error =" + str(e))
    arcpy.AddMessage(output_string)

# #########################################
# Add the Survey Record to the Survey table
try:

    # use the aSurvey class method "createSurveyRectangle" method to return an envelop based on points in the project.
    survey_area = the_survey.createSurveyRectangle()

    # open Edit session for writing the Survey Polygon/Record.
    edit = arcpy.da.Editor(arcpy.env.workspace)
    edit.startEditing(False, False)
    ### logger.info("\nInserting Survey record to {}".format(fc_surveys))

    p_cursor =  arcpy.da.InsertCursor(fc_surveys,the_survey.table_fields)

    # add assignment ID if included as input parameter
    the_survey.assignment_fk = assignment_id if assignment_id else -1

    r = the_survey.listSurvey()
    r.append(survey_area)

    p_cursor.insertRow(r)

    del p_cursor
    ### logger.info("Survey polygon created. (id={})".format(the_survey.id))
    edit.stopEditing(True)
    results.append("; Survey polygon created.")
except RuntimeError as e:
    results.append(f"; RuntimeError when adding survey ({e}).")
    results.append("survey_fields: {}".format(the_survey.table_fields))
    ### logger.error("data: {}".format(r))
    results.append("; " + str(e))
except arcpy.ExecuteError as e:
    ### logger.error("Failed adding survey data to temporary survey table. {}".format(e))
    results.append("; " + arcpy.GetMessage(2))
    results.append("; " + str(e))
except Exception as e:
    ### logger.error("{} ".format(e))
    results.append("; Exception Error =" + str(e))

try:
    for wash in dirty_laundry:
        ### logger.debug("Deleting {}".format(wash))
        arcpy.Delete_management(wash)
        del wash
except:
    ### logger.error('Failed while cleaning up temporary files')
    results.append("; Failed while cleaning up temporary files.")

### logger.debug("Creating zoom-to polygon and passing back to Web Map.")
expression = "{} = {}".format('survey_uid',the_survey.id)
arcpy.AddMessage("Expression: {}".format(expression))
#'layer = arcpy.management.MakeFeatureLayer(fc_surveys, 'lyr')
rs = arcpy.SelectLayerByAttribute_management(fc_surveys, "NEW_SELECTION", expression)
feature_set = arcpy.FeatureSet()
feature_set.load(rs)

arcpy.SetParameterAsText(2,results)
arcpy.SetParameter(3,feature_set)