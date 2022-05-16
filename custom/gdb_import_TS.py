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
#import logging, logging.handlers
from math import radians, sin, cos
import math
import configparser

runfrom = os.path.basename(sys.executable)

tool_path = os.path.dirname(__file__)

arcpy.env.workspace = arcpy.GetParameter(4)
if arcpy.env.workspace == None:
    arcpy.env.workspace = os.path.join(tool_path, "cmcguirevm.sde")
desc_ws = arcpy.Describe(arcpy.env.workspace)

if not os.path.exists(arcpy.env.workspace):
    arcpy.AddError(f'workspace does not exists: {arcpy.env.workspace}')
    exit()

if len(arcpy.ListFeatureClasses("*surveys")) > 0:
    surveys = arcpy.ListFeatureClasses("*surveys")[0]
    surveys = os.path.join(arcpy.env.workspace,surveys)
    arcpy.MakeFeatureLayer_management(surveys,'lyr_surveys')
    #surveys = 'lyr_surveys'
else:
    arcpy.AddError(f"Exiting tool. Could not access {os.path.join(arcpy.env.workspace),'surveys'}")

if len(arcpy.ListFeatureClasses("*survey_points")) > 0:
    survey_points = arcpy.ListFeatureClasses("*survey_points")[0]
    survey_points = os.path.join(arcpy.env.workspace,survey_points)
    arcpy.MakeFeatureLayer_management(surveys,'lyr_survey_points')
    #survey_points = 'lyr_survey_points'
else:
    arcpy.AddError(f"Exiting tool. Could not access {os.path.join(arcpy.env.workspace),'survey_points'}")

if len(arcpy.ListFeatureClasses("*stations")) > 0:
    stations = arcpy.ListFeatureClasses("*stations")[0]
    stations = os.path.join(arcpy.env.workspace,stations)
    arcpy.MakeFeatureLayer_management(surveys,'lyr_stations')
    #stations = 'lyr_stations'
else:
    arcpy.AddError(f"Exiting tool. Could not access {os.path.join(arcpy.env.workspace),'lyr_stations'}")

if len(arcpy.ListFeatureClasses("*survey_lines")) > 0:
    survey_lines = arcpy.ListFeatureClasses("*survey_lines")[0]
    survey_lines = os.path.join(arcpy.env.workspace,survey_lines)
    arcpy.MakeFeatureLayer_management(surveys,'lyr_survey_lines')
    #survey_lines = 'lyr_survey_lines'
else:
    arcpy.AddError(f"Exiting tool. Could not access {os.path.join(arcpy.env.workspace),'lyr_survey_lines'}")

if len(arcpy.ListFeatureClasses("*orientation_sites")) > 0:
    orientation_sites = arcpy.ListFeatureClasses("*orientation_sites")[0]
    orientation_sites = os.path.join(arcpy.env.workspace,orientation_sites)
    arcpy.MakeFeatureLayer_management(orientation_sites,'lyr_orientation_sites')
    orientation_sites = 'lyr_orientation_sites'
else:
    arcpy.AddError(f"Exiting tool. Could not access {os.path.join(arcpy.env.workspace),'lyr_orientation_sites'}")

def formatDateTime(in_date,in_time):
    r_date = datetime.datetime(int(in_date.split("/")[2]),int(in_date.split("/")[0]),int(in_date.split("/")[1]),int(in_time.split(":")[0]),int(in_time.split(":")[1]),int(in_time.split(":")[2]))
    return str(r_date.strftime('%m/%d/%Y %H:%M:%S'))

def getID(in_table, in_field):
    ''' increment by number of 1 to the largest number value in the table's
    field to derive a unique and sequence ID. Return ID.'''

    fields = arcpy.ListFields(in_table)

    for f in fields:
        if f.name == in_field:
            field = f
            continue

    if field.type == 'Integer':

        expression = f'{field.name} > 0'
        sql_clause = (None,'ORDER BY {}'.format(field.name))

        rows = [row[0] for row in arcpy.da.SearchCursor(in_table, [field.name],where_clause=expression,sql_clause=sql_clause)]
        if len(rows) > 0:
            pid = max(rows) + 1    # pid = rows[-1][0] + 1
        else:
            pid = 1

        return pid
    return None

def DMStoDD(inDMS):
    dd = -1
    dms_list = re.findall("[0-9]+", inDMS) # find only numbers (strip out °'")

    if len(dms_list) >= 1 and len(dms_list) <= 3:
        if len(dms_list) == 3:
            dd = (float(dms_list[0])/1) + (float(dms_list[1])/60) + (float(dms_list[2])/3600)
        elif len(dms_list) == 2 and dms_list[0] != '99999':
            dd = (float(dms_list[0])/1) + (float(dms_list[1])/60)
        elif len(dms_list) == 1 and dms_list[0] != '99999':
            dd = (float(dms_list[0])/1)
    return dd

def makeDistAngleLineArray(origin_x, origin_y, distance, angle):
    ''' returns a two-point line using a origin XY, distance, and angle. The
    math determines the XY coordinate of the end point.'''

    # calculate offsets with trig
    (disp_x, disp_y) = (distance * sin(radians(angle)), distance * cos(radians(angle)))
    (end_x, end_y) = (origin_x + disp_x, origin_y + disp_y)
    lineArray = arcpy.Array()
    # start point
    start = arcpy.Point()
    (start.ID, start.X, start.Y) = (1, origin_x, origin_y)
    lineArray.add(start)

    # end point
    end = arcpy.Point()
    (end.ID, end.X, end.Y) = (2, end_x, end_y)
    lineArray.add(end)

    return lineArray

def convertCoordinates(in_xy, from_sr, to_sr):
    '''in_xy a list, from_sr spatial ref, to_sr spatial ref'''
    pt = arcpy.Point()
    pt.X = in_xy[0]
    pt.Y = in_xy[1]
    ptg = arcpy.PointGeometry(pt,from_sr)

    tmp_table_name = 'xxtbl_' + os.path.basename(tempfile.mktemp())
    table = os.path.join(r'in_memory',tmp_table_name)

    arcpy.ConvertCoordinateNotation_management(ptg, table, "#", "#", "SHAPE", "DD_2", "#", to_sr)

    rows = [row for row in arcpy.da.SearchCursor(table,['SHAPE@X','SHAPE@Y'])]
    out_xy = [rows[0][0],rows[0][1]]

    del tmp_table_name
    del table
    del rows

    return out_xy

def DDtoDMS(inDD,withSymbols=False,rounding=2):

    degrees = int(inDD)
    minutes = (inDD - degrees)
    seconds = abs((minutes*60 - int(minutes*60)) * 60)
    minutes = abs(int((inDD-degrees)*60))

    degrees = format(degrees, '03')
    minutes = format(minutes, '02')
    seconds = "{:.{}f}".format(seconds,rounding)

    if withSymbols:
        d = u"\u00b0"
        sendback = str(degrees) + d + " " + str(minutes) + "' " + str(seconds) + '"'
    else:
        sendback = str(degrees) + " " + str(minutes) + " " + str(seconds)
    return sendback

def calcInverseComputedAzimuth(the_station, bs_name, orientation_data):

    x1 = the_station.x
    y1 = the_station.y

    # find the orientation site and pull coordinates
    results = []

    for row in orientation_data:
        row_no = row[0] - 1
        search_list = row[1].upper() +',' + row[2].upper()

        #if bs_name.strip().upper() in ['MIDDLE','1199','CTRAV', 'BS S', 'BS N', 'HAWK']:
        #    pass

        for item in search_list.split(','):

            if re.search(r'\b' + bs_name.strip().upper() + r'\b', item):
                if len(results) == 0:
                    results.append(row)
                elif results[0][0] != row[0]:
                    results.append(row)

    if len(results) == 0:
        arcpy.AddWarning("Orientation Name {} not found.".format(bs_name.strip().upper()))
        return '-- -- --'
    elif len(results) > 1:
        arcpy.AddWarning("Searching orientation_sites for {}".format(bs_name.strip().upper()))
        arcpy.AddWarning("Orientation Name had multiple matches, using 1st match.")
        for rs in results:
            arcpy.AddWarning("\t{}".format(rs[1]+rs[2]))
    elif len(results) == 1:
        arcpy.AddMessage("Orientation Name {} matched to {}".format(bs_name.strip().upper(),results[0][1]))

    x2 = float(results[0][3])
    y2 = float(results[0][4])

    del results

    # with all four coordinations, apply Yuma's formula to derive Computed Az

    # col E, solve for "D"
    # =SQRT((C2-A2)^2+(D2-B2)^2)   =SQRT((X2-X1)^2+(Y2-Y1)^2)
    D = math.sqrt((x2-x1)**2 + (y2-y1)**2)
    ##print D

    # -----col F, solve for "AZ Deg. Dec"
    # =(ATAN((C2-A2)/(D2-B2))*180/(4*ATAN(1)))  =(ATAN((X2-X1)/(D-Y1))*180/(4*ATAN(1)))
    F = math.atan( (x2-x1) / ( y2-y1 ) )*180/(4 * math.atan(1) )
    ##print F

    if F < 0 and (x2 - x1) < 0:
        return DDtoDMS((360 - abs(F)),True,0)
    elif F > 0 and (x2 - x1) < 0:
        return DDtoDMS((180 + abs(F)), True,0)
    elif F < 0 and (y2 - y1) < 0:
        return DDtoDMS(180 + F,True,0)
    else:
        return DDtoDMS(F,True,0)

class FieldMapping:
    ''' takes a list of 'key:values' pairs and provides ordered lookup capabilities '''
    # before the ":" is the field name for the data. After the ":" is a list of alternate names/aliases that may be in Total Station file.

    count = 0
    # !! Don't put leading/training spaces in these!  (e.g., " Inst S/N"; should be w/o leading/training spaces "Inst S/N")
    field_mapping = ('name:Project,Project Name',
            'classification:Classification',
            'program:Program,Program Name',
            'site:Site',
            'date:Date',
            'poc:POC,Test Officer',
            'instrument_type:Intrument Type,Inst Type,Instrument Type',
            'instrument_sn:Instrument S/N,Inst S/N',
            'surveyor:Surveyor',
            'reference:REF,Reference',
            'grid:Grid,YPG Grid',
            'uom:Unit,Units'
            )


    def __init__(self):
        # instantiates the object with an ordered dictionary of column name mapping.
        self.a_dict = collections.OrderedDict()
        for i in self.field_mapping:
            self.a_dict[i.split(":")[0]] = i.split(":")[1].split(",")
            self.count += 1

    def as_keylist(self):
        output = []
        for k in iter(self.a_dict.keys()):       #self.a_dict.iterkeys():
            output.append(k)
        return output

    def as_valuelist(self):
        '''returns list of values that may be labeled in Total Station File'''
        output = []
        for v in iter(self.a_dict.values()):    # self.a_dict.itervalues():
            if len(v) > 1:
                for sm in v:
                    output.append(''.join(sm))
            else:
                output.append(''.join(v))
        return output

    def return_key(self,search_value):
        output = []
        for k,v in list(self.a_dict.items()):   # self.a_dict.items():
            if search_value in v:
                output.append(k)
        return output

    def key_index(self,search_key):
        return self.as_keylist().index(search_key)

    def return_value(self,search_key):
        output = []
        for k,v in list(self.a_dict.items()):   #self.a_dict.items():
            if search_key in k:
                return v

class aSurvey:

    sr = arcpy.SpatialReference()
    source_fc = 'lyr_surveys'   # surveys
    table_fields = ['survey_uid', 'name', 'classification', 'program', 'site', 'date', 'poc', 'instrument_type', 'instrument_sn', 'surveyor', 'reference', 'grid', 'uom', 'source_file', 'source_status','review_status','assignment_fk','SHAPE@']

    def __init__(self,source,file_name=''):

        arcpy.AddMessage("----------")
        arcpy.AddMessage("getting ID from {} {}".format(self.source_fc,'survey_uid'))
        self.id              = getID(self.source_fc,'survey_uid')
        arcpy.AddMessage(f"getPID returning ID {self.id} for table {self.source_fc}")

        self.name            = source['Program'].strip() + '-' + source['Site'].strip()
        arcpy.AddMessage('Instantiating {} {} (id={})'.format(self.__class__.__name__,self.name,self.id))

        self.classification  = ''
        self.program         = source['Program'].strip()
        self.site            = source['Site'].strip()
        self.date            = source['Date'].strip()

        if 'POC' in source:
            self.poc = source['POC'].strip()
        elif 'Test Officer' in source:
            self.poc = source['Test Officer'].strip()

        if 'Inst Type' in source:
            self.instrument_type = source['Inst Type'].strip()
        elif 'Intrument Type' in source:
            self.instrument_type = source['Intrument Type'].strip()
        elif 'Instrument Type' in source:
            self.instrument_type = source['Instrument Type'].strip()
        else:
            self.instrument_type = ''

        if 'Instrument S/N' in source:
            self.instrument_sn = source['Instrument S/N'].strip()
        elif 'Inst S/N' in source:
            self.instrument_sn = source['Inst S/N'].strip()
        else:
            self.instrument_sn = ''

        self.surveyor = source['Survey Crew'].strip() if 'Survey Crew' in source else ''
        self.reference = source['Reference'].strip() if 'Reference' in source else ''
        self.grid = source['Grid'].strip() if 'Grid' in source else 'YPG'
        self.uom = source['Unit'].strip() if 'Unit' in source else ''
        self.source_file = os.path.basename(file_name)
        self.source_status = 'Draft'
        self.review_status = 'draft'
        self.assignment_fk = assignment_uid
        self.points = []
        self.shape = ''

    def createSurveyRectangle(self):
        arcpy.AddMessage('{}: create envelope for survey {} (id={}) to {}'.format(sys._getframe().f_code.co_name, self.name, self.id,self.source_fc))

        try:
            tmp_name = 'xxPrj_' + os.path.basename(tempfile.mktemp())
            output = os.path.join("in_memory",tmp_name)
            arcpy.MinimumBoundingGeometry_management(self.points,output,"ENVELOPE")
            rows = [row for row in arcpy.da.SearchCursor(output,['SHAPE@'])]
            self.shape = rows[0][0]

        except arcpy.ExecuteError as e:
            arcpy.AddError(arcpy.GetMessage(2))

        except Exception as e:
            arcpy.AddError("{} running calcConvergenceAngle ({}).".format(e,self.name))

        finally:
            if arcpy.Exists(output):
                arcpy.Delete_management(output)

        return self.shape

    def writeToDB(self):
        ''' write: ['survey_uid', 'name', 'classification', 'program', 'site', 'date', 'poc', 'instrument_type', 'instrument_sn', 'surveyor', 'reference', 'grid', 'uom', 'source_file', 'source_status','SHAPE@'] '''

        # grab project GUID from assignment record and add that to survey
        ## delete ? expression = "assignment_uid = {}".format(self.assignment_fk)
        line_data = [self.id,self.name,self.classification,self.program,self.site,self.date,self.poc,self.instrument_type,self.instrument_sn,self.surveyor,self.reference,self.grid,self.uom,self.source_file,self.source_status,self.review_status, self.assignment_fk,self.shape]

        try:

            edit = arcpy.da.Editor(arcpy.env.workspace)
            edit.startEditing(False, False)
            arcpy.AddMessage("Editing Workspace: {}".format(edit.workspacePath))
            cursor = arcpy.da.InsertCursor(self.source_fc,self.table_fields)
            cursor.insertRow(line_data)
            del cursor
            edit.stopEditing(True)
            del edit

##            with arcpy.da.Editor(arcpy.env.workspace) as edit:
##                cursor = arcpy.da.InsertCursor(self.source_fc,self.table_fields)
##                cursor.insertRow(line_data)
##            del cursor
        except RuntimeError as e:
            arcpy.AddError("RuntimeError when adding feature ({}).".format(self.__class__.__name__))
            arcpy.AddError(e)
            arcpy.AddMessage("table_fields: {}".format(self.table_fields))
            arcpy.AddMessage("line_data = {}".format(line_data))
        except arcpy.ExecuteError as e:
            arcpy.AddError(arcpy.GetMessage(2))
        except Exception as e:
            arcpy.AddError("{} when adding feature ({}).".format(e,self.__class__.__name__))
            arcpy.AddMessage("table_fields: {}".format(self.table_fields))
            arcpy.AddMessage("line_data = {}".format(line_data))

class aStation:

    count = 0
    survey_uid = -1
    cols = []
    allObjs = []
    sr = arcpy.SpatialReference()

    source_fc = 'lyr_stations'  # stations
    table_fields = ['st_uid','survey_fk','st_name','st_x','st_y','st_z','st_hi','st_ca','SHAPE@']

    def __init__(self,aname,read_x,read_y,read_z,read_hi):
        self.id = getID(self.source_fc,'st_uid') + aStation.count
        arcpy.AddMessage(f"getPID returning ID {self.id} for table {self.source_fc}")
        self.name = aname
        arcpy.AddMessage('Importing {} {} (id={})'.format(self.__class__.__name__,self.name,self.id))
        self.x = float(read_x.strip())
        self.y = float(read_y.strip())
        self.z = float(read_z.strip())
        self.hi = float(read_hi.strip())
        self.shape = self.getShape()
        self.ca = self.calcConvergenceAngle()

        aStation.count += 1
        aStation.allObjs.append(self)

    def getShape(self):
        pointXY = arcpy.Point(self.x, self.y)
        return arcpy.PointGeometry(pointXY)

    def calcConvergenceAngle(self):
        '''in_xy, sr to calculate the converegence angle'''
        tmp_cca = 'xxtbl_' + os.path.basename(tempfile.mktemp())
        table = os.path.join(r'in_memory',tmp_cca)

        try:
            arcpy.CreateFeatureclass_management("in_memory",tmp_cca,"POINT",'','','',self.sr)
            if arcpy.Exists(tmp_cca):
                arcpy.Delete_management(tmp_cca)
            layer = arcpy.MakeFeatureLayer_management(table,tmp_cca)
            arcpy.AddField_management(layer,'st_ca',"DOUBLE")
            cursor = arcpy.da.InsertCursor(table,['SHAPE@'])
            cursor.insertRow(self.shape)
            del cursor
            arcpy.env.cartographicCoordinateSystem = coordinate_system = (self.sr)
            arcpy.CalculateGridConvergenceAngle_cartography(layer,"st_ca","GRAPHIC")
            ## GEOGRAPHIC —Angle is calculated clockwise with 0 at top. This is the default.  (seems to get B.S. in closer to features)
            ## ARITHMETIC —Angle is calculated counterclockwise with 0 at right.
            ## GRAPHIC —Angle is calculated counterclockwise with 0 at top.
            rows = [row for row in arcpy.da.SearchCursor(layer,["st_ca"])]

        except arcpy.ExecuteError as e:
            arcpy.AddError(arcpy.GetMessage(2))
        except Exception as e:
            arcpy.AddError("{} running calcConvergenceAngle ({}).".format(e,self.name))

        del layer

        return rows[0][0]

    def writeToDB(self):

        line_data = [self.id, self.survey_uid,self.name,self.x, self.y, self.z, self.hi, self.ca, self.shape]

        try:
            edit = arcpy.da.Editor(arcpy.env.workspace)
            edit.startEditing(False, False)
            cursor = arcpy.da.InsertCursor(self.source_fc,self.table_fields)
            cursor.insertRow(line_data)
            del cursor
            edit.stopEditing(True)
            del edit

#  below didn't work with relationship classes
##            with arcpy.da.Editor(arcpy.env.workspace) as edit:
##                cursor = arcpy.da.InsertCursor(aStation.source_fc,aStation.table_fields)
##                cursor.insertRow(line_data)
##            del cursor
        except RuntimeError:
            arcpy.AddError("RuntimeError when adding feature ({}).".format(self.__class__.__name__))
            arcpy.AddError("table_fields: {}".format(self.table_fields))
            arcpy.AddError("line_data = {}".format(line_data))
        except arcpy.ExecuteError as e:
            arcpy.AddError(arcpy.GetMessage(2))
        except Exception as e:
            arcpy.AddError("{} when adding feature ({}).".format(e,self.__class__.__name__))
            arcpy.AddError("table_fields: {}".format(self.table_fields))
            arcpy.AddError("line_data = {}".format(line_data))


    @staticmethod
    def fetch(station_id):
        for s in aStation.allObjs:
            if station_id == s.id:
                return s
        return None

    @classmethod
    def fromRow(cls, row_data):
        station_name = row_data[cols[0]].strip()
        station_x = row_data[cols[1]]
        station_y = row_data[cols[2]]
        station_z = row_data[cols[3]]
        station_hi = row_data[cols[4]]
        return cls(station_name, station_x, station_y, station_z, station_hi)

    @classmethod
    def set_survey_uid(cls,pid):
        cls.survey_uid = pid

    @classmethod
    def set_columns_list(cls,cols):
        cls.cols = cols

    @classmethod
    def set_sr(cls,sr):
        cls.sr = sr

    @classmethod
    def returnID(cls,station_name):
        return [s.id for s in cls.allObjs if s.name.strip() == station_name.strip()][0]



class aSurveyLine:

    count = 0
    survey_uid = -1
    cols = []
    allObjs = []
    lof_length = 20
    backsight_distance = 50

    source_fc = 'lyr_survey_lines' # survey_lines
    sr = arcpy.SpatialReference()
    table_fields = ['sl_uid','survey_fk','station_fk','sl_type','sl_name','sl_computed_az','sl_observed_az','tmp_ob_cv_DD','tmp_ob_cv_DMS','tmp_conv_angle','SHAPE@']

    def __init__(self,aname,computed_az,observed_az=0,distance=backsight_distance,astation=None,sl_type='backsight'):
        self.id = getID(self.source_fc,'sl_uid') + aSurveyLine.count
        self.name = aname
        self.computedAz = ''
        self.observedAz = observed_az
        self.distance = float(distance)
        self.station = astation.strip()
        self.station_fk = aStation.returnID(astation.strip())
        self.type = sl_type
        self.ob_az_DD = DMStoDD(observed_az)
        station = aStation.fetch(self.station_fk)
        self.ob_cv_DD = self.ob_az_DD + station.ca
        self.ob_cv_DMS = DDtoDMS(self.ob_cv_DD,True)
        self.ca = station.ca
        # derive x1,y1,x2,y2 using "aname" variable lookup on the orientation_sites
        #  feature class using the alternate_names field and pull coords from that
        self.computedAz = ''
        if sl_type in ['backsight', 'backsight_as_pt']:
            self.computedAz = calcInverseComputedAzimuth(station,aname,orientation_data)
        self.shape = self.createLineArray()

        aSurveyLine.count += 1
        aSurveyLine.allObjs.append(self)

    @classmethod
    def fromRow(cls, row_data, station_name):
        backsight_name = row_data[cols[0]].strip()
        computed_az = row_data[cols[1]].strip()
        observed_az = row_data[cols[2]].strip()
        backsight_distance = cls.backsight_distance

        return cls(backsight_name, computed_az, observed_az, backsight_distance, station_name)

    @classmethod
    def fromPtRow(cls, ptobj):
        ''' creates 'survey_lines' lines between the station and the point XY '''
        sl_name = ptobj.name.strip()
        sl_az = ptobj.ha
        if ptobj.type == 'lof' and isinstance(ptobj.ha,str):
            sl_az = ptobj.ha.split('\'')[0] + '\''    ## format the string DMS to only show degrees and minutes.
        sl_distance = ptobj.hd
        if ptobj.type in ['backsight', 'backsight_as_pt']:
            sl_distance = cls.backsight_distance
        sl_origin_st = ptobj.station
        sl_type = ptobj.type
        sl_survey_fk = ptobj.survey_uid
        if ptobj.name[:3].lower() == 'lof':   # if Line of Fire line/point, set to lof_length meters
            sl_distance = cls.lof_length
            sl_type = 'lof'
        return cls(sl_name, '', sl_az, sl_distance,sl_origin_st,sl_type)

    @classmethod
    def set_survey_uid(cls,pid):
        cls.survey_uid = pid

    @classmethod
    def set_columns_list(cls,cols):
        cls.cols = cols

    @classmethod
    def set_sr(cls,sr):
        cls.sr = sr

    def createLineArray(self):
        '''origin_x, origina_y, distance, angle - creates a temporary table and passes it to arcpy.BearingDistanceToLine_management'''
        st = aStation.fetch(self.station_fk)
        angle = self.ob_az_DD + st.ca

        outFC = os.path.join("in_memory",'line_ypg_nad27_BDTL')
        if arcpy.Exists(outFC):
            arcpy.Delete_management(outFC)

        # make a fGDB table
        tmp = os.path.join("in_memory", 'tmpBDTLdata')
        if arcpy.Exists(tmp):
            arcpy.Delete_management(tmp)
        tmp = arcpy.CreateTable_management("in_memory", 'tmpBDTLdata')
        table_path = arcpy.Describe(tmp).catalogPath
        arcpy.AddField_management(tmp,'ypg_x',"Double",0,0,8,"YPG_X","NULLABLE","NON_REQUIRED")
        arcpy.AddField_management(tmp,'ypg_y',"Double",0,0,8,"YPG_Y","NULLABLE","NON_REQUIRED")
        arcpy.AddField_management(tmp,'distance',"Double",0,0,8,"Distance","NULLABLE","NON_REQUIRED")
        arcpy.AddField_management(tmp,'bearing',"Double",0,0,8,"Bearing","NULLABLE","NON_REQUIRED")

        # open the table and write to the fGDB table using cursor
        cursor = arcpy.da.InsertCursor(tmp,['ypg_x','ypg_y','distance','bearing'])
        cursor.insertRow([st.x, st.y, self.distance, angle])
        del cursor

        # use the table data to generate the arc
        #arcpy.management.BearingDistanceToLine(in_table, out_featureclass, x_field, y_field, distance_field, {distance_units}, bearing_field, {bearing_units}, {line_type}, {id_field}, {spatial_reference}, {attributes})
        arcpy.BearingDistanceToLine_management(tmp, outFC, 'ypg_x', 'ypg_y', 'distance', 'METERS', 'bearing', 'DEGREES', 'GEODESIC', '', self.sr)

        # get line data and put in polyline object
        rows = [row for row in arcpy.da.SearchCursor(outFC, ['SHAPE@'])]
        l_shape = rows[0][0]   # one/first row, first/only field is SHAPE

        lineArray = arcpy.Array()
        lineArray.add(l_shape.firstPoint)
        lineArray.add(l_shape.lastPoint)

        del tmp
        del outFC
        del rows
        del l_shape

        return [[lineArray[0].X,lineArray[0].Y],[lineArray[1].X,lineArray[1].Y]]

    def writeToDB(self):
        print('Writing record for aSurveyLine ID: {}'.format(self.id))
        line_data = [self.id, self.survey_uid,self.station_fk, self.type, self.name, self.computedAz, self.observedAz, self.ob_cv_DD, self.ob_cv_DMS, self.ca, self.shape]

        try:

            edit = arcpy.da.Editor(arcpy.env.workspace)
            edit.startEditing(False, False)
            cursor = arcpy.da.InsertCursor(self.source_fc,self.table_fields)
            cursor.insertRow(line_data)
            del cursor
            edit.stopEditing(True)
            del edit

            '''with arcpy.da.Editor(arcpy.env.workspace) as edit:
                cursor = arcpy.da.InsertCursor(aSurveyLine.source_fc,aSurveyLine.table_fields)
                cursor.insertRow(line_data)
            del cursor'''

        except RuntimeError:
            arcpy.AddError("RuntimeError when adding feature ({}).".format(self.__class__.__name__))
            arcpy.AddError("table_fields: {}".format(self.table_fields))
            arcpy.AddError("line_data = {}".format(line_data))
        except arcpy.ExecuteError as e:
            arcpy.AddError(arcpy.GetMessage(2))
        except Exception as e:
            arcpy.AddError("{} when adding feature ({}).".format(e,self.__class__.__name__))
            arcpy.AddError("table_fields: {}".format(self.table_fields))
            arcpy.AddError("line_data = {}".format(line_data))

class aSurveyPoint:

    count = 0
    survey_uid = -1
    cols = []
    allObjs = []
    lof_length = 20
    backsight_distance = 50

    source_fc = 'lyr_survey_points'   # survey_points

    sr = arcpy.SpatialReference()
    table_fields = ['survey_fk','station_fk', 'pt_uid', 'pt_type', 'pt_name', 'ts_ha', 'ts_hd', 'ts_vd', 'ts_ht', 'ts_edm_type', 'ts_edm_mode', 'ts_prism_type', 'ts_prism_const', 'date_time', 'ypg_x', 'ypg_y', 'ypg_z', 'wgs84_x', 'wgs84_y', 'wgs84_z','SHAPE@']

    def __init__(self,aname,ha, hd, vd, ht, edm_type, edm_mode, prism_type, prism_const, adate, read_x, read_y, read_z, astation=None,pttype='survey_point'):
        self.id = getID(self.source_fc,'pt_uid') + aSurveyPoint.count
        arcpy.AddMessage(f"getPID returning ID {self.id} for table {self.source_fc}")
        self.name = aname
        self.ha = ha
        self.hd = hd
        self.vd = vd
        self.ht = ht
        self.edm_type = edm_type
        self.edm_mode = edm_mode
        self.prism_type = prism_type
        self.prism_const = prism_const
        self.date = adate
        self.coord_x = read_x
        self.coord_y = read_y
        self.coord_z = read_z
        if pttype not in ['backsight_as_pt', 'backsight']:
            wgs84_sr = arcpy.SpatialReference(104013)
            wgs84_xy = convertCoordinates([read_x,read_y],self.sr,wgs84_sr)
            self.wgs84_x = wgs84_xy[0]
            self.wgs84_y = wgs84_xy[1]
            self.wgs84_z = read_z
        else:
            self.wgs84_x = 0
            self.wgs84_y = 0
            self.wgs84_z = 0
        self.station = astation.strip()
        self.station_fk = aStation.returnID(astation.strip())
        self.type = pttype
        self.shape = self.getShape()

        aSurveyPoint.count += 1
        aSurveyPoint.allObjs.append(self)

    def getShape(self):
        '''returns point geometry object for Survey Point'''
        if self.type in ['backsight','backsight_as_pt','lof']:
            for s in aStation.allObjs:
                if self.station_fk == s.id:
                    st = s
            ha_as_DD = DMStoDD(self.ha) + st.ca
            twoPtLineArray = makeDistAngleLineArray(st.x, st.y,200,ha_as_DD)
            # use the end of the line (origin is station loc, end is angle + HD) for location
            coord_x = twoPtLineArray[1].X
            coord_y = twoPtLineArray[1].Y
        else:
            coord_x = self.coord_x
            coord_y = self.coord_y

        pointXY = arcpy.Point(coord_x, coord_y)
        ptGeometry = arcpy.PointGeometry(pointXY)
        return ptGeometry

    @classmethod
    def fromRow(cls, row_data, station_name):
        '''reads and parses total station data from file data row and loads values in to the class properties'''
        name = row_data[cols[0]]
        if name == 'HD CAM1':
            print("HD CAM1")
        ha = row_data[cols[1]]
        hd = float(row_data[cols[2]].strip())
        vd = float(row_data[cols[3]].strip())
        ht = float(row_data[cols[4]].strip())
        edm_type = row_data[cols[5]]
        edm_mode = row_data[cols[6]]
        prism_type = row_data[cols[7]]
        prism_const = row_data[cols[8]]
        date = formatDateTime(row_data[cols[9]],row_data[cols[10]])
        coord_x = float(row_data[cols[11]].strip())
        coord_y = float(row_data[cols[12]].strip())
        coord_z = float(row_data[cols[13]].strip())
        pttype = 'survey_point'
        # if we're dealing with a backsight, use horizontal angle (ha), and
        # station XY to draw a 1000 meter line, and plot a point at the end.
        if hd == 99999 and coord_x == 99999 and coord_y == 99999:
            pttype = 'backsight_as_pt'
        if name[:3].lower() == 'lof' or name[:2].lower() == 'lf':   # if Line of Fire line/point, set to 200 meters
            pttype = 'lof'
            if hd == 99999:
                hd = cls.lof_length
        station = station_name
        station_fk = aStation.returnID(station_name.strip())

        return cls(name,ha,hd,vd,ht,edm_type,edm_mode,prism_type,prism_const,date, coord_x, coord_y,coord_z, station,pttype)

    @classmethod
    def set_survey_uid(cls,pid):
        cls.survey_uid = pid

    @classmethod
    def set_columns_list(cls,cols):
        cls.cols = cols

    @classmethod
    def set_sr(cls,sr):
        cls.sr = sr

    def writeToDB(self):

        line_data = [self.survey_uid, self.station_fk, self.id, self.type, self.name,self.ha,self.hd,self.vd,self.ht,self.edm_type,self.edm_mode,self.prism_type,self.prism_const,self.date,self.coord_x, self.coord_y, self.coord_z, self.wgs84_x, self.wgs84_y, self.wgs84_z, self.shape]

        #
        # May want to write Pt ID points only (i.e., filter writing to self.type in ['survey_point', 'station_line']
        #
        try:
            edit = arcpy.da.Editor(arcpy.env.workspace)
            edit.startEditing(False, False)
            cursor = arcpy.da.InsertCursor(self.source_fc,self.table_fields)
            cursor.insertRow(line_data)
            edit.stopEditing(True)
            del edit
        except RuntimeError:
            arcpy.AddError("RuntimeError when adding feature ({}).".format(self.__class__.__name__))
            arcpy.AddError("table_fields: {}".format(self.table_fields))
            arcpy.AddError("line_data = {}".format(line_data))
        except arcpy.ExecuteError as e:
            arcpy.AddError(arcpy.GetMessage(2))
        except Exception as e:
            arcpy.AddError("{} when adding feature ({}).".format(e,self.__class__.__name__))
            arcpy.AddError("table_fields: {}".format(self.table_fields))
            arcpy.AddError("line_data = {}".format(line_data))


class startHere:
    pass

# ##############################################################################
# ##############################################################################

# Parameter 0: take input Total Station file; read it into file_data list object
ts_file = arcpy.GetParameterAsText(0)
if os.path.basename(sys.executable) not in ['ArcGISPro.exe', 'ArcSOC.exe']:
    ts_file = r"C:\Toolworkbench\yuma-range-survey\web_map_configuration\ArcGISPro_Projects\sample_data\SITE9_KTM_17JAN2019.asc"
    arcpy.AddWarning(f"Running outside of Esri software. Using file {ts_file} for DEBUGGING")

arcpy.AddMessage(f"importing file: {ts_file}")
file_data = list(line for line in csv.reader(open(ts_file, 'rt'), delimiter='\t') if line)

# Parameter 1: Assignment ID captures an assignment number and includes it with
#              the survey file to link an assignment with the resulting survey.
assignment_uid = arcpy.GetParameter(1)
if assignment_uid == '' or assignment_uid == None:
    assignment_uid = -9999

# Parameter 2 = Result messages (set at end with SetParameter)
# Parameter 3 = zoom-to/output polygon (set at end with SetParameter)

##arcpy.management.MakeFeatureLayer(orientation_sites, 'orientation_layer')
orientation_data = [row for row in arcpy.da.SearchCursor('lyr_orientation_sites',["*"])]

# set default spatial reference. if correct spatial reference designation is written in file, it will be over-written when reading the file.
ypg_sr = r"PROJCS['NAD27_YUMA_PROVING_GROUND',GEOGCS['GCS_North_American_1927',DATUM['D_North_American_1927',SPHEROID['Clarke_1866',6378206.4,294.9786982]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',84738.012],PARAMETER['False_Northing',-175814.044],PARAMETER['Central_Meridian',-113.75],PARAMETER['Scale_Factor',0.999933333],PARAMETER['Latitude_Of_Origin',31.0],UNIT['Meter',1.0]];-6100292.49622249 -14607719.0234388 409368153.975199;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision"
sr = arcpy.SpatialReference()
sr.loadFromString(ypg_sr)
aStation.sr, aSurveyLine.sr, aSurveyPoint.sr = sr,sr,sr

section = ''
survey_dict = {}

prj_attributes = FieldMapping()

rIndex = 0
# Loop through file, line by line (variable "r" set to equal text in current line).
for r in file_data[:-1]:

    # if first column contains word "classification", then grab the value of the following line (not column) before proceeding.
    if r[0].lower() == 'classification':
        classification = file_data[rIndex + 1][0]
        survey_dict[r[0]] = classification

    # Look for keyword (listed in FieldMapping() class) stored in object
    # "prj_attributes". When a match is found, store the data in survey_dict object.
    if r[0].strip(":") in prj_attributes.as_valuelist():

        if len(r) == 2:    # if row "r" has two items (columns of data, then fetch then create a dict key and value.
            survey_dict[r[0].strip(":")] = r[1].strip()


        elif len(r) == 1:  # if row "r" has one item (label), then create dict key with '' value.
            survey_dict[r[0].strip(":")] = ''

        # Some information needs special handling. If the "Grid" information is
        # useful, we'll use it to determine the spatial reference information
        # before loading data. All else, load it using YPG sr.
        if r[0] == 'Grid:':
            sr_dict = {'UTM':26711,'WGS84':4326,'WGS84 (G1150)':104013}
            sr = arcpy.SpatialReference(sr_dict[r[1].upper()]) if r[1].upper() in sr_dict.keys() else 0
            # lacking understanding of the Grid value, load YPG spatial reference.
            if sr == 0:
                ypg_sr = r"PROJCS['NAD27_YUMA_PROVING_GROUND',GEOGCS['GCS_North_American_1927',DATUM['D_North_American_1927',SPHEROID['Clarke_1866',6378206.4,294.9786982]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',84738.012],PARAMETER['False_Northing',-175814.044],PARAMETER['Central_Meridian',-113.75],PARAMETER['Scale_Factor',0.999933333],PARAMETER['Latitude_Of_Origin',31.0],UNIT['Meter',1.0]];-6100292.49622249 -14607719.0234388 409368153.975199;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision"
                sr = arcpy.SpatialReference()
                sr.loadFromString(ypg_sr)

            # Set all of our default spatial references to what is determined.
            aStation.sr, aSurveyLine.sr, aSurveyPoint.sr = sr,sr,sr

    # while reading file, if we are at a new section, indicated by the first
    # column label (see FieldMapping()), set the section equal to that label
    # and count the columns, removing the blank columns
    if r[0] in ['Station ID', 'Backsight', 'Pt ID']:
        section = r[0]
        # count the columns and skip over blank columns
        cols = []
        cIndex = 0
        for c in r:
            if c != '':
                cols.append(cIndex)    # creates a list of valid columns (cols)
            cIndex += 1

        # set the column addresses per class
        if r[0] == 'Station ID':
            aStation.set_columns_list(cols)
        if r[0] == 'Backsight':
            aSurveyLine.set_columns_list(cols)
        if r[0] == 'Pt ID':
            aSurveyPoint.set_columns_list(cols)

    # if past the section header, use our object fromRow routines to read data in
    if section != r[0] and r[0] != '' and r[0] != ' ':
        if section == 'Station ID':
            st = aStation.fromRow(r)
        if section == 'Backsight':
            ##sl = aSurveyLine.fromRow(r,st.name)
            sl = aSurveyLine.fromRow(r,st.name)
        if section == 'Pt ID':
            pt = aSurveyPoint.fromRow(r,st.name)

    rIndex += 1

stations_list = [station.name for station in aStation.allObjs]
for p in aSurveyPoint.allObjs:
    if p.name.strip() in stations_list:
        p.type = 'station_line'

survey = aSurvey(survey_dict,ts_file)
survey.classification = classification
aStation.set_survey_uid(survey.id)
aSurveyLine.set_survey_uid(survey.id)
aSurveyPoint.set_survey_uid(survey.id)

# create line objects using station and all points
for p in aSurveyPoint.allObjs:
    aSurveyLine.fromPtRow(p)

# add points to survey.points so we can create a bounding rectangle.
for s in aStation.allObjs:
    survey.points.append(s.shape)
for p in aSurveyPoint.allObjs:
    if p.type not in ['backsight','backsight_as_pt','lof']:
        survey.points.append(p.shape)

# create survey polygon, the pass the feature_set (with 1 survey polygon) back as output parameter
survey.createSurveyRectangle()
survey.writeToDB()

expression = "{} = {}".format('survey_uid',survey.id)
layer = arcpy.MakeFeatureLayer_management(survey.source_fc, "lyr")
rs = arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION", expression)
feature_set = arcpy.FeatureSet()
feature_set.load(rs)
arcpy.SetParameter(3,feature_set)

for station in aStation.allObjs:
    station.writeToDB()
for point in aSurveyPoint.allObjs:
    point.writeToDB()
for line in aSurveyLine.allObjs:
    line.writeToDB()

arcpy.SetParameter(2,'Finished loading file: {}'.format(ts_file))