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
import configparser

tool_home = os.path.dirname(__file__)
results = []

arcpy.env.workspace = arcpy.GetParameter(3)
if arcpy.env.workspace == None:
    #arcpy.env.workspace = os.path.join(tool_home,"cmcguirevm.sde")
    arcpy.env.workspace = R"\\ypgrw04xaaa0h57\arcgisserver\SurveyReports\Geodetics.sde"
    
if arcpy.Exists(arcpy.env.workspace):
    desc_ws = arcpy.Describe(arcpy.env.workspace)

    if desc_ws.dataElementType == 'DEWorkspace':
        results.append('workspace_type: {}'.format(desc_ws.workspaceType))
    elif desc_ws.dataElementType == 'DEFile':
        results.append('workspace_type: {}'.format(desc_ws.dataElementType))
        arcpy.AddError("Unable to read {} as a DEWorkspace".format(desc_ws.name))
else:
    results.append("{} not found.".format(arcpy.env.workspace))
    arcpy.SetParameter(1,results) # string messages
    arcpy.AddError("Unable to read Workspace input.")
    exit()

if len(arcpy.ListFeatureClasses("*surveys")) > 0:
    surveys = arcpy.ListFeatureClasses("*surveys")[0]
    surveys = os.path.join(arcpy.env.workspace,surveys)
    arcpy.MakeFeatureLayer_management(surveys,'lyr_surveys')
    #surveys = 'lyr_surveys'
    results.append('surveys st to {}'.format(surveys))
else:
    arcpy.AddError("Exiting tool. Could not access {}".format(os.path.join(arcpy.env.workspace,'surveys')))

if len(arcpy.ListFeatureClasses("*survey_points")) > 0:
    survey_points = arcpy.ListFeatureClasses("*survey_points")[0]
    survey_points = os.path.join(arcpy.env.workspace,survey_points)
    arcpy.MakeFeatureLayer_management(survey_points,'lyr_survey_points')
    #survey_points = 'lyr_survey_points'
    results.append('survey_points st to {}'.format(survey_points))
else:
    arcpy.AddError("Exiting tool. Could not access {}".format(os.path.join(arcpy.env.workspace,'survey_points')))

if len(arcpy.ListFeatureClasses("*stations")) > 0:
    stations = arcpy.ListFeatureClasses("*stations")[0]
    stations = os.path.join(arcpy.env.workspace,stations)
    arcpy.MakeFeatureLayer_management(stations,'lyr_stations')
    #stations = 'lyr_stations'
    results.append('stations st to {}'.format(stations))
else:
    arcpy.AddError("Exiting tool. Could not access {}".format(os.path.join(arcpy.env.workspace,'stations')))

if len(arcpy.ListFeatureClasses("*survey_lines")) > 0:
    survey_lines = arcpy.ListFeatureClasses("*survey_lines")[0]
    survey_lines = os.path.join(arcpy.env.workspace,survey_lines)
    arcpy.MakeFeatureLayer_management(survey_lines,'lyr_survey_lines')
    #survey_lines = 'lyr_survey_lines'
else:
    arcpy.AddError("Exiting tool. Could not access {}".format(os.path.join(arcpy.env.workspace,'survey_lines')))

if len(arcpy.ListFeatureClasses("*orientation_sites")) > 0:
    orientation_sites = arcpy.ListFeatureClasses("*orientation_sites")[0]
    orientation_sites = os.path.join(arcpy.env.workspace,orientation_sites)
    arcpy.MakeFeatureLayer_management(orientation_sites,'lyr_orientation_sites')
    orientation_sites = 'lyr_orientation_sites'
else:
     arcpy.AddError("Exiting tool. Could not access {}".format(os.path.join(arcpy.env.workspace,'orientation_sites')))

print_map           = R"\\cmcguirevm\custom\printed_map.aprx"

# Signature image - not a requirement but put this here as a placeholder.
signature_path       = R"\\cmcguirevm\custom\signatures"
yuma_logo_image = os.path.join(tool_home, 'ytc_small.png')
signatures_dict = {'Chris McGuire':'signature_cmcguire.png','':'signature_somebody_signature.PNG'}

class aSurvey:

    def __init__(self,table_source):
        desc = arcpy.Describe(table_source)
        self.name = desc.baseName
        #self.path = desc.catalogPath
        self.fieldnames = ['classification', 'program', 'site', 'date', 'poc', 'instrument_type', 'instrument_sn', 'surveyor', 'reference', 'grid', 'uom', 'source_file', 'source_status','review_status','reviewer','review_date']
        # field names load data into Survey object, fieldaliases print the data in the Excel (i.e., if you don't want the field data, then leave out of field alias)
        self.fieldaliases = ['Classification', 'Program', 'Site', 'Date', 'POC', 'Inst Type', 'Inst S/N', 'Surveyor Crew', 'Reference', 'Grid', 'Unit', 'source_file', 'source_status']


class aStation:
    def __init__(self,table_source):
        desc = arcpy.Describe(table_source)
        self.name = desc.baseName
        #self.path = desc.catalogPath
        self.fieldnames = ['st_uid','st_name','st_x','st_y','st_z','st_hi']
        self.fieldaliases = ['Station ID', 'X', 'Y', 'Z', 'HI (incl)']  # leave out "st_uid" so it isn't printed in report


class aSurveyLine:
    def __init__(self,table_source):
        desc = arcpy.Describe(table_source)
        self.name = desc.baseName
        #self.path = desc.catalogPath
        ##self.fieldnames = fetchFields(table_source)
        self.fieldnames = ['sl_name','sl_computed_az','sl_observed_az']
        ## self.fieldaliases = fetchFields(table_source,True)
        self.fieldaliases = ['Backsight', 'Computed Az', 'Observed Az']
        ##sendMessage(self.fieldaliases)

class aPoint:
    def __init__(self,table_source):
        desc = arcpy.Describe(table_source)
        self.name = desc.baseName
        #self.path = desc.catalogPath
        self.fieldnames = ['pt_name','ts_ha','ts_hd','ts_vd','ts_ht','ypg_x','ypg_y','ypg_z']
        ##self.fieldaliases = fetchFields(table_source,True)
        self.fieldaliases = ['Point ID', 'HA', 'HD', 'VD', 'HT (incl)', 'X', 'Y', 'Z']
        ##sendMessage(self.fieldaliases)

class textReport:

    def __init__(self):
        self.row_count = 0
        self.start_y = 6
        self.row_y = 6
        self.start_x = .25
        self.row_height = 0.15
        self.reset_y_min = 1.25  #if y gets below this value it will be reset for new page.
        self.st_data = []
        self.st_printcols = ['st_name','st_x','st_y','st_z','st_hi']
        self.st_header = ['Station', 'X', 'Y', "HI"]
        self.st_prtcol_starts = [0.25,1.3,2.3,3.3,4.3]
        self.bs_data = []
        self.bs_printcols = ['sl_name','sl_computed_az','sl_observed_az']
        self.bs_header = ['Backsight','Computed Az','Observed Az']
        self.bs_prtcol_starts = [.25,2.3,3.45]
        self.pt_data = []
        self.pt_printcols = ['pt_name','ts_ha','ts_hd','ts_vd','ts_ht','ypg_x','ypg_y','ypg_z']
        self.pt_header = ['Point ID','HA','HD','VD','HT (Incl)','X', 'Y', 'Z']

        self.pt_prtcol_starts = [.25,1.1,1.75,2.4,3.05,3.7,4.35,5]

    def nextRow(self):

        self.row_y -= self.row_height
        self.row_count += 1

        if self.row_y < self.reset_y_min:
            print("REACHED BOTTOM OF PAGE - resetting Y to top")
            self.newPage()

    def newPage(self):
        self.row_y = self.start_y


def sendMessage(message, indent=0):

    if indent == 0:
        string = message
    if indent > 0 :
        string = "{} {}".format(" " * indent,message)
    arcpy.AddMessage(string)
    print(string)

def writeSurvey(project):

    # set-up formatting
    title_format = myXLS.add_format({'font_name':'Arial','font_size':10,'bold': True, 'underline':False,'font_color':'black','align':'left'})
    class_format = myXLS.add_format({'font_name':'Arial','font_size':14,'bold': True, 'underline':False,'font_color':'red','align':'left'})
    label_format = myXLS.add_format({'font_name':'Arial','font_size':10,'bold': True, 'underline':False,'font_color':'black','align':'right'})
    data_format = myXLS.add_format({'font_name':'Arial','font_size':10,'bold': True, 'underline':False,'font_color':'black','align':'left','num_format':'mm/dd/yy'})

    # write(row,col,string)
    sheet_a.insert_image(0,0,yuma_logo_image,{'object_position': 3,'x_scale': 0.80, 'y_scale': 0.80})
    sheet_a.write(0,1,"Classification")
    sheet_a.write(4,1,'US ARMY YUMA PROVING GROUND GEODETICS',title_format)

    classification_dict = {'fouo':'For Official Use Only','cui':'Controlled Unclassified Information','secret':'SECRET','':'Unknown'}
    rIndex=5
    for r in project.fieldaliases:
        idx = project.fieldaliases.index(r)
        label = r + ":"
        data = project.data[idx]

        if r.lower() == 'classification':
            sheet_a.write(1,1,data,class_format)
            classification = classification_dict[data.lower()]
            sheet_a.write(2,1,classification)


        elif not r.lower() in ['source_file','source_status']:
            sheet_a.write(rIndex,0,label,label_format)  # write label (col 0)
            sheet_a.write(rIndex,1,data,data_format)    # write value (col 1)
            sendMessage("writing row ({})  as {}: {}".format(rIndex,label,data))


        rIndex +=1

    return rIndex


def writeTable(title,begin_row,header,data):
    # set up formatting
    border_color = '#B8B8B8'
    lefdata_format = myXLS.add_format({'font_name':'Arial','font_size':10,'bold': False, 'underline':False,'font_color':'black','align':'left','border':1, 'border_color':border_color})
    ctrdata_format = myXLS.add_format({'font_name':'Arial','font_size':10,'bold': False, 'underline':False,'font_color':'black','align':'center','border':1, 'border_color':border_color})
    date_format = myXLS.add_format({'font_name':'Arial','font_size':10,'bold': False, 'underline':False,'font_color':'black','align':'left','num_format':'mm/dd/yyyy hh:mm','border':1, 'border_color':border_color})
    headerLeft_format = myXLS.add_format({'font_name':'Arial','font_size':9,'bold': True, 'underline':False,'font_color':'black','align':'left','border':1, 'border_color':border_color})
    headerCenter_format = myXLS.add_format({'font_name':'Arial','font_size':9,'bold': True, 'underline':False,'font_color':'black','align':'center','border':1, 'border_color':border_color})

    rIndex = begin_row
    sheet_a.write (rIndex,0,'')
    rIndex += 1

    start_col = 0
    date_cols = []

    for col,heading in enumerate(header):
        if col == 0:
            sheet_a.write(rIndex,( col - start_col ),heading,headerCenter_format) #change first column formatting if necessary
        elif col > start_col:
            sheet_a.write(rIndex,( col - start_col ),heading,headerCenter_format)
            
        if heading.upper().find('DATE') >= 0:
            date_cols.append(col)

    rIndex += 1
    for i, l in enumerate(data):
        for col,dayta in enumerate(l.data):
            if col > 0 and col not in date_cols:
                sheet_a.write(rIndex,( col - start_col ),dayta,ctrdata_format)
            elif col in date_cols:
                sheet_a.write(rIndex,( col - start_col ),dayta,date_format)
            else:
                sheet_a.write(rIndex,( col - start_col ),dayta,lefdata_format)

        rIndex += 1

    return rIndex

def fixText(row):
    new_string = []
    for item in row:
        if isinstance(item,str) or isinstance(item,unicode):
            new_string.append(item)
        elif isinstance(item,float) or isinstance(item,int):
            new_string.append(str(item))
    return new_string

def writeQAQC(the_survey, review_status_idx, reviewer_idx, review_date_idx):
    # Insert the QA/QC Status information in Cell L2
    review_format = myXLS.add_format({'font_name':'Arial','font_size':14,'bold': True, 'underline':False,'font_color':'red','align':'right'})
    if the_survey.data[review_status_idx] == None:
        sheet_a.write(1,11,'No data',review_format)
    elif the_survey.data[review_status_idx] == 'approved':
        sheet_a.write(1,11,'FINAL DATA - QA/QC RELEASED',review_format)
    else:
        sheet_a.write(1,11,'DRAFT',review_format)

    # write reivewer name and date below the QA/QC status
    reviewer_format = myXLS.add_format({'font_name':'Arial','font_size':10,'bold': False, 'underline':False,'font_color':'black','align':'left'})
    date_format = myXLS.add_format({'font_name':'Arial','font_size':10,'bold': False, 'underline':False,'font_color':'black','align':'left','num_format':'mm/dd/yyyy'})
    right = myXLS.add_format({'align':'right','bold':True})

    if the_survey.data[reviewer_idx] in signatures_dict.keys():
        signature_image = os.path.join(signature_path,signatures_dict[the_survey.data[reviewer_idx]])
        sheet_a.insert_image(2,11,signature_image,{'object_position': 3})

    sheet_a.write(2,10,'Processor:',right)
    # name printed
    approver_name = the_survey.data[reviewer_idx] if the_survey.data[reviewer_idx] != None else 'No data'
    sheet_a.write(5,11,approver_name,reviewer_format)
    approval_date = the_survey.data[review_date_idx] if the_survey.data[review_date_idx] != None else 'No data'
    sheet_a.write(6,11,approval_date,date_format)
    
    print(the_survey.data)


# ##############################################################################
# ##############################################################################

run_uuid = uuid.uuid1()
survey_id = 12


# Parameter 0 - the PROJECT_UID
if os.path.basename(sys.executable) in ['ArcGISPro.exe', 'ArcSOC.exe']:
    survey_id = arcpy.GetParameter(0) if arcpy.GetParameter(0) != '' or arcpy.GetParameter(0) != None else 2
    results.append("Executable: {}".format(os.path.basename(sys.executable)))
    results.append("Processing Project UID: {}".format(survey_id))

# Parameter 1 - output message - collect info during run and send it at end. 
# loading strings into the results list to return.

# set-up space to create dependency items (map png, Pro project, and output)
scratchFolder = arcpy.env.scratchFolder
arcpy.AddMessage("Creating scratch folder at: {}".format(scratchFolder))
results.append("Creating scratch folder at: {}".format(scratchFolder))

# Parameter 2 is OUTPUT File - written at end with SetParameter
output = os.path.join(scratchFolder, f"export_{survey_id}.xlsx")
string = "output filename: {}".format(pathlib.Path(output))
arcpy.AddMessage(string)

# Open Excel Object.
myXLS = xlsxwriter.Workbook(output)

# surveys = arcpy.ListFeatureClasses("*surveys")
# survey_points = arcpy.ListFeatureClasses("*survey_points")
# stations = arcpy.ListFeatureClasses("*stations")
# survey_lines = arcpy.ListFeatureClasses("*survey_lines")
# orientation_sites = arcpy.ListFeatureClasses("*orientation_sites")

if os.path.exists(print_map):
    aprx = arcpy.mp.ArcGISProject(print_map)
elif os.path.exists(os.path.join(tool_home, "printed_map.aprx")):
    aprx = arcpy.mp.ArcGISProject(os.path.join(tool_home, "printed_map.aprx"))
else:
    aprx = None
arcpy.AddMessage("Using ArcGIS Pro project {} for survey map.".format(aprx.filePath))


# Grab the survey information via the aSurvey class object and a SearchCursor
survey = aSurvey(surveys)
expression = "{} = {}".format('survey_uid',survey_id) 
count = [row for row in arcpy.da.SearchCursor(surveys,survey.fieldnames,where_clause=expression)]
if len(count) == 0:
    arcpy.AddWarning("Project ID not found in survey table. Cancelling export process.")
    results.append("\nProject ID not found in survey table. Cancelling export process.")
    arcpy.SetParameter(1,results)
    exit()

p_cursor =  arcpy.da.SearchCursor(surveys,survey.fieldnames,where_clause=expression)
survey.data = list(p_cursor.next())
del p_cursor

# Set the Excel worksheet name to be the project name
# _format the worksheet before writing
sheet_a = myXLS.add_worksheet(survey.data[0])
sheet_a.hide_gridlines(2)
# source: https://xlsxwriter.readthedocs.io/page_setup.html
sheet_a.set_landscape()
sheet_a.set_paper(1)
sheet_a.set_margins(left=.3, right=.3, top=0.5, bottom=.5)
sheet_a.fit_to_pages(1, 2)
for row in range(3,100):
    sheet_a.set_row(row,12.75)

# Write the survey project information to the sheet first and return the last row number
last_row = writeSurvey(survey)
results.append("\nWriting survey project information to Excel.")
map_row = last_row

if survey.data[5] == 'GPS':
    # Format worksheet for GPS data
    # GPS columns: Point ID,NORTHING,EASTING,ORTHO HT,LATITUDE,LONGITUDE,ELLIP HT,YPG X,YPG Y,3D CQ,DATE/TIME,COMMENTS
    gps_col_widths = [21,13,13,10,16,16,10,10,10,10,15,50]
    for c,w in enumerate(gps_col_widths):
        sheet_a.set_column(c,c,w)

    # set-up a merge format for placing headers holding coordinate system information
    merge_format = myXLS.add_format({'font_name':'Arial','font_size':9,'bold': True, 'underline':False,'font_color':'black','align':'center','bottom':0})

    # fetch survey points
    points_list = []
    expression = "{} = {} and pt_type = 'gps'".format('survey_fk',survey_id)
    p_cursor =  arcpy.da.SearchCursor(survey_points,['pt_name','gps_northing','gps_easting','gps_ortho_ht','wgs84_y','wgs84_x','gps_ellip_ht','ypg_x','ypg_y','gps_cq3d','date_time','comments'],where_clause=expression)

    for p_row in p_cursor:
        pts = aPoint(survey_points)
        pts.fieldnames = ['pt_name','gps_northing','gps_easting','gps_ortho_ht','wgs84_y','wgs84_x','gps_ellip_ht','ypg_x','ypg_y','gps_cq3d','date_time','comments']
        pts.fieldaliases = ['Point ID', 'NORTHING', 'EASTING', 'ORTHO HT', 'LATITUDE', 'LONGITUDE', 'ELLIP HT', 'YPG X', 'YPG Y', '3D CQ', 'DATE/TIME', 'COMMENTS']

        pts.data = list(p_row)
        points_list.append(pts)

    ######   Write Survey Point Data to Excel
    # insert the coordinate system headers
    coord_label = 'WGS84 / UTM Z11N' if points_list[0].data[2] > 500000 else "WGS 84 / UTM Z12N"
    sheet_a.merge_range(last_row,1,last_row,2,coord_label,merge_format)
    sheet_a.merge_range(last_row,4,last_row,5,'WGS84',merge_format)
    sheet_a.merge_range(last_row,7,last_row,8,'YPG GRID',merge_format)

    # write the table (headers and data) below the coordinate system headers
    last_row = writeTable('POINT',last_row,pts.fieldaliases,points_list)
    results.append("\nWriting GPS points to Excel.")

    # sheet_a.write(4,13, "no Map for GPS")

elif survey.data[5] != 'GPS':

    # Define column widths for Total Station
    ts_col_widths =[21,13,13,10,10,10,10,10,3,10,10,12]
    for c,w in enumerate(ts_col_widths):
        sheet_a.set_column(c,c,w)

    # fetch Station Information
    stations_list = []
    expression = "{} = {}".format('survey_fk',survey_id)
    try:
        s_cursor =  arcpy.da.SearchCursor(stations,['st_uid','st_name','st_x','st_y','st_z','st_hi'],where_clause=expression)
    except:
        results.append("arcpy.da.SearchCursor({},['st_uid','st_name','st_x','st_y','st_z','st_hi'],where_clause={})".format(stations,expression))
        arcpy.SetParameter(1,results)
        
    # Loop through each station via CURSOR rows
    for row in s_cursor:
        stations_list = []
        sta = aStation(stations)
        sta.survey_id = survey_id
        sta.id = row[0]
        sta.data = list(row[-5:])  # skip the record id (st_uid) and grab the 5 fields at end of list
        stations_list.append(sta)

        # Write Station Information to Excel
        last_row = writeTable('STATION',last_row,sta.fieldaliases,stations_list)
        results.append("\nWriting Station points to Excel.")

        # fetch BACKSIGHT information
        backsight_list = []
        expression = "{} = {} AND ( sl_type = 'backsight' or sl_type = 'backsight_as_pt')".format('station_fk',sta.id)
        b_cursor =  arcpy.da.SearchCursor(survey_lines,['sl_name','sl_computed_az','sl_observed_az'],where_clause=expression)
        for b_row in b_cursor:
            bs = aSurveyLine(survey_lines)
            bs.data = fixText(b_row)
            backsight_list.append(bs)

        # Write Backsights Information to Excel
        last_row = writeTable('BACKSIGHT',last_row,bs.fieldaliases,backsight_list)
        results.append("\nWriting Backsights to Excel.")

        # fetch SURVEY_POINTS information
        points_list = []
        expression = "{} = {} and pt_type <> 'backsight_as_pt'".format('station_fk',sta.id)
        p_cursor =  arcpy.da.SearchCursor(survey_points,['pt_name','ts_ha','ts_hd','ts_vd','ts_ht','ypg_x','ypg_y','ypg_z'],where_clause=expression)        
        for p_row in p_cursor:
            pts = aPoint(survey_points)
            pts.data = list(p_row)
            points_list.append(pts)
           
        # Write Survey Point Information to Excel
        last_row = writeTable('POINT',last_row,pts.fieldaliases,points_list)
        results.append("\nWriting survey points to Excel.")
        
    #if the ArcGIS Pro project exists, then include a map, otherwise leave the map out
    if aprx:
        # Get the map view
        m = aprx.listMaps()[0]
        mv = m.defaultView
        layers = m.listLayers()

        for lyr in m.listLayers("Assignments*"):
            lyr.visible = False

        lyr_survey_point     = m.listLayers("Survey Point")[0]
        #lyr_survey_point.definitionQuery = f"(pt_type = 'survey_point' OR pt_type = 'gps') and survey_fk = {survey_id}"
        lyr_survey_point.definitionQuery = f"pt_type IN ('survey_point', 'gps') And survey_fk = {survey_id}"

        lyr_station          = m.listLayers("Station")[0]
        lyr_station.definitionQuery = f"survey_fk = {survey_id}"

        lyr_survey_line      = m.listLayers("Survey Line")[0]
        lyr_survey_line.definitionQuery = f"sl_type = 'survey_point' and survey_fk = {survey_id}"

        lyr_orientation_line = m.listLayers("Orientation Line")[0]
        lyr_orientation_line.definitionQuery = f"sl_type = 'station_line' and survey_fk = {survey_id}" 

        lyr_LOF              = m.listLayers("LOF")[0]
        lyr_LOF.definitionQuery = f"sl_type = 'lof' and survey_fk = {survey_id}"

        lyr_backsight_line   = m.listLayers("Backsight Line")[0]
        lyr_backsight_line.definitionQuery = f"sl_type IN ('backsight' ,'backsight_as_pt') And survey_fk = {survey_id}"

        lyr_surveys          = m.listLayers("Surveys")[0]
        lyr_surveys.definitionQuery = f"survey_uid = {survey_id}"       
            
        # This will just leave the vector layers from the template
        for lyr in m.listLayers("World Imagery"):
            m.removeLayer(lyr)

        aprx_name = os.path.join(scratchFolder, f"APrj_{run_uuid}")
        aprx.saveACopy(aprx_name)
        arcpy.AddMessage("\nSaved {}".format(aprx_name))

        expression = "survey_uid = {}".format(survey_id)
        arcpy.SelectLayerByAttribute_management(in_layer_or_view=lyr_surveys, selection_type="NEW_SELECTION", where_clause=expression)
        result = arcpy.GetCount_management(lyr_surveys)

        # Change the extent of the map view
        lyt = aprx.listLayouts()[0]
        mf = lyt.listElements("MAPFRAME_ELEMENT")[0]
        ext = mf.getLayerExtent(lyr_surveys,True,True)
        results.append("mf extent: " + str(ext))
        ext.XMin = ext.XMin - 2
        ext.XMax = ext.XMax + 2
        ext.YMin = ext.YMin - 2
        ext.YMax = ext.YMax + 2
        mv.camera.setExtent(ext)

        m.clearSelection()

        # Use the uuid module to generate a GUID as part of the output name
        # This will ensure a unique output name
        Output_File = 'WebMap_{}.png'.format(str(run_uuid))
        Output_File = os.path.join(scratchFolder, Output_File)
        arcpy.AddMessage("Creating temporary PNG file: {}".format(Output_File))

        #aprx.saveACopy(os.path.join(scratchFolder, f"APrj_{run_uuid}"))

        # Export the web map
        mv.exportToPNG(Output_File, width=1800, height=1800, resolution=300, color_mode='32-BIT_WITH_ALPHA')

        # Clean up
        del mv, m, aprx

        # map_row = 4  --> Determined from last_row above
        map_col = 9
        if Output_File != '':
            sheet_a.insert_image(map_row,map_col,Output_File,{'x_offset': 1, 'y_offset': 10})
        
        # Draw a border around map area in spreadsheet
        #draw_frame_border(myXLS, sheet_a, 5, 10, 10, 10,thickness=1)
        thickness = 1
        first_row = map_row
        first_col = map_col
        cols_count = 9
        rows_count = 38
        # top left corner
        sheet_a.conditional_format(first_row, first_col, first_row, first_col, {'type': 'formula', 'criteria': 'True', 'format': myXLS.add_format({'top': thickness, 'left': thickness})})
        # top right corner
        sheet_a.conditional_format(first_row, first_col + cols_count - 1, first_row, first_col + cols_count - 1,{'type': 'formula', 'criteria': 'True','format': myXLS.add_format({'top': thickness, 'right': thickness})})
        # bottom left corner
        sheet_a.conditional_format(first_row + rows_count - 1, first_col, first_row + rows_count - 1, first_col, {'type': 'formula', 'criteria': 'True', 'format': myXLS.add_format({'bottom': thickness, 'left': thickness})})
        # bottom right corner
        sheet_a.conditional_format(first_row + rows_count - 1, first_col + cols_count - 1, first_row + rows_count - 1, first_col + cols_count - 1, {'type': 'formula', 'criteria': 'True','format': myXLS.add_format({'bottom': thickness, 'right': thickness})})
        # top
        sheet_a.conditional_format(first_row, first_col + 1, first_row, first_col + cols_count - 2, {'type': 'formula', 'criteria': 'True', 'format': myXLS.add_format({'top': thickness})})
        # left
        sheet_a.conditional_format(first_row + 1, first_col, first_row + rows_count - 2, first_col, {'type': 'formula', 'criteria': 'True', 'format': myXLS.add_format({'left': thickness})})
        # bottom
        sheet_a.conditional_format(first_row + rows_count - 1, first_col + 1, first_row + rows_count - 1, first_col + cols_count - 2, {'type': 'formula', 'criteria': 'True', 'format': myXLS.add_format({'bottom': thickness})})
        # right
        sheet_a.conditional_format(first_row + 1,first_col + cols_count - 1, first_row + rows_count - 2, first_col + cols_count - 1, {'type': 'formula', 'criteria': 'True', 'format': myXLS.add_format({'right': thickness})})

    else:
        arcpy.AddWarning("No ArcGIS Pro project found at {}. Map will not be included in report.".format(aprx.filePath))

# Add QA/QC markings: Approval Status, Approver Name, Approved Date

if survey.data[5] == 'GPS':
    rev_stat_idx = 13
    rev_name_idx = 14
    rev_date_idx = 15
else:
    rev_stat_idx = 13
    rev_name_idx = 14
    rev_date_idx = 15

writeQAQC(survey, rev_stat_idx,rev_name_idx,rev_date_idx)
results.append("\nWriting QA/QC status to Excel.")

myXLS.close()
results.append("\nClosing and delivering Excel to widget.")
results.append("output: {}".format(output))

notes = open(os.path.join(scratchFolder,f"Notes_{run_uuid}.txt"), "w")
for line in results:
    notes.write(line)
    notes.write("\n")
notes.close()

arcpy.SetParameter(2,output)  # Excel file
arcpy.SetParameter(1,results) # string messages

# When all said and done, examine the scratch folder and clean out older artifacts. 
import time
now = time.time()

for filename in os.listdir(scratchFolder):

    if os.path.getmtime(os.path.join(scratchFolder, filename)) < now - .5 * 86400:

        if os.path.isfile(os.path.join(scratchFolder, filename)):
            os.remove(os.path.join(scratchFolder, filename))
