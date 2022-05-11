define([
  'dojo/_base/declare',
  'dojo/_base/lang',
  'dojo/_base/html',
  'dojo/query',
  'dojo/dom-style',
  'esri/request',
  'dojo/on',
  "dojo/topic",
  'dojo/dom-construct',
  'dijit/_WidgetsInTemplateMixin',
  'dojo/mouse',
  "dojo/date/locale",
  "dojo/date",
  'esri/tasks/query',
  'esri/layers/GraphicsLayer',
  'esri/layers/FeatureLayer',
  'esri/renderers/SimpleRenderer',
  'esri/graphic',
  "dojo/aspect",
  'jimu/WidgetManager',
  'jimu/SelectionManager',
  'esri/symbols/jsonUtils'
], function(declare, lang, html, query, domStyle, esriRequest, on, topic, dojoDomConstruct, _WidgetsInTemplateMixin,
  mouse, locale, date, Query, GraphicsLayer, FeatureLayer, SimpleRenderer, Graphic, aspect,
  WidgetManager, SelectionManager, symbolJsonUtils
) {

  return declare('SurveyManager', null, {
    map: null,
    config: null,
    appConfig: null,
    beginingDate: null,
    endingDate: null,
    surveyCalendar: null,
    layerInfosObj: null,
    featuresHighlighted: null,
    layerId: null,
    cellsWithEvents: [],
    cellEvents: [],
    highlightLayer: null,
    highlightSymbol: null,
    selectedDayLayer: null,
    assignmentLayerObj: null,
    assignmentsEachDayOnCalendar: [],
    attributeTableWidget: null,
    smartEditWidget: null,
    surveyonDayLyrTitle: "Assignments On Selected Day",
    surveyonDayLyrId: "AssignmentsOnSelectedDay",
    dateField_begin: "",
    dateField_end: "",
    attributeTableWidgetId: null,
    smartEditWidgetId: null,

    constructor: function(inMap, inConfig, inAppConfig, parent) {
      this.map = inMap;
      this.config = inConfig;
      this.appConfig = inAppConfig;
      this.parent = parent;
      this.surveyCalendar = parent.surveyCalendar;
      this.layerInfosObj = parent.layerInfosObj;
      this.layerId = this.config.filters[0].layerId;
      this.highlightSymbol = symbolJsonUtils.fromJson(this.config.filters[0].symbol);
      this.dateField_begin = this.config.filters[0].dateField_begin;
      this.dateField_end = this.config.filters[0].dateField_end;


      this.surveyCalendar.watch("currentFocus", lang.hitch(this, this.onCalendarFocusChange));

      this.assignmentLayerObj = this.layerInfosObj.getLayerInfoById(this.layerId).layerObject;
      this.assignmentInfoTemplate = this.assignmentLayerObj.infoTemplate;

      this.parent.own(this.assignmentLayerObj.on(
        'load',
        lang.hitch(this, this.highlightDaysOnCalendar))
      );

      var renderer = new SimpleRenderer(this.highlightSymbol);
      this.highlightLayer = new GraphicsLayer();
      this.highlightLayer.setRenderer(renderer);
      this.map.addLayer(this.highlightLayer);

      this.selectedDayLayer = new FeatureLayer(this.assignmentLayerObj.url, {
        "outFields": ["*"],
        "id": this.surveyonDayLyrId,
        "title": this.surveyonDayLyrTitle,
        "name": this.surveyonDayLyrTitle,
        "infoTemplate": this.assignmentInfoTemplate
      });
      this.selectedDayLayer.setDefinitionExpression("1 = 0");
      this.selectedDayLayer.visible = false;
      this.map.addLayer(this.selectedDayLayer);

      //domStyle.set(this.selectedDayLayer.getNode(), "pointer-events","none");

      topic.subscribe("survey/tableRowClicked", lang.hitch(this, "tableRowClicked"));
      on(this.assignmentLayerObj, 'edits-complete', lang.hitch(this, "reApplyFilter"));

      this.attributeTableWidgetId = this.findWidgetId(this.appConfig.widgetOnScreen, "widgets/AttributeTable/Widget");
      this.attributeTableWidget = WidgetManager.getInstance().getWidgetById(this.attributeTableWidgetId);
      //aspect.after(this.attributeTableWidget, "setActiveTable", lang.hitch(this, "afterActiveTableSet"));

      this.smartEditWidgetId = this.findWidgetId(this.appConfig.widgetPool, "widgets/SmartEditor/Widget");
      if (this.smartEditWidgetId == null && this.appConfig.widgetOnScreen) {
        this.smartEditWidgetId = this.findWidgetId(this.appConfig.widgetOnScreen, "widgets/SmartEditor/Widget");
      }
	  
      if (this.smartEditWidgetId == null && this.appConfig.widgetOnScreen && this.appConfig.widgetOnScreen.groups) {
		  var i = -1;
		  do {
			this.smartEditWidgetId = this.findWidgetId(this.appConfig.widgetOnScreen.groups[++i], "widgets/SmartEditor/Widget");
		  } while (this.smartEditWidgetId == null)
	  }
      return this;
    },

    afterActiveTableSet: function(mthd, args) {
      if (args && args[0] && args[0].configedInfo && args[0].configedInfo.id == "AssignmentsOnSelectedDay") {
        args[0].grid.on('.dgrid-row:click', lang.hitch("onAssignmentTableRowClicked"));
      }
    },

    onAssignmentTableRowClicked: function(event) {
      var row = grid.row(event);
      console.log('Row clicked:', row.id);
    },

    findWidgetId: function(ws, w_uri) {
      var widgets = ws.widgets;
      for (var i = 0; i < widgets.length; i++) {
        if (widgets[i].uri == w_uri) {
          return widgets[i].id;
        }
      }
      return null;
    },

    onCalendarFocusChange: function(propName, oldFocus, newFocus) {
         if (this.parent.surveyManagerNeededParameters.node.toggleButton.checked
            && propName == "currentFocus" &&
              (oldFocus.getFullYear() != newFocus.getFullYear() ||
                oldFocus.getMonth() != newFocus.getMonth())) {

            WidgetManager.getInstance().triggerWidgetOpen(this.attributeTableWidgetId).then(lang.hitch(this, function(wdgt) {
              wdgt.layerTabPageClose(this.surveyonDayLyrId, true);
            }));
            this.assignmentLayerObj.clearSelection();
            this.selectedDayLayer.clearSelection();
            this.reApplyFilter();
          }
    },

    reApplyFilter: function() {
      if(this.parent.surveyManagerNeededParameters.node.toggleButton.checked){
        this.parent.applyFilterValues(this.parent.surveyManagerNeededParameters.node, this.parent.surveyManagerNeededParameters.filterObj);
      }
    },

    tableRowClicked: function(row) {
      WidgetManager.getInstance().triggerWidgetOpen(this.attributeTableWidgetId).then(lang.hitch(this, function(wdgt) {
        if (wdgt._activeLayerInfoId == this.surveyonDayLyrId) {
          var q = new Query();
          q.where = "OBJECTID = " + row.OBJECTID;
          q.outFields = ["*"];
          q.returnGeometry = true;
          this.assignmentLayerObj.selectFeatures(q, FeatureLayer.SELECTION_NEW).then(
            lang.hitch(this, 'openSmartEditWidget'),
            lang.hitch(this, 'queryFailed'));
        }
      }));
    },

    openSmartEditWidget: function(feature) {
      var smtWidget = WidgetManager.getInstance().getWidgetById(this.smartEditWidgetId);
      if (smtWidget && smtWidget.state == "open") {
        smtWidget.beginEditingByFeatures([feature], this.assignmentLayerObj, [this.layerId], [feature]);
      } else {
        WidgetManager.getInstance().triggerWidgetOpen(this.smartEditWidgetId).then(lang.hitch(this, function(smtWidget) {
          smtWidget.beginEditingByFeatures([feature], this.assignmentLayerObj, [this.layerId], [feature]);
        }));
      }
    },

    // build the where for the current month
    buildWhereforCurrentMonth: function() {
      this.assignmentLayerObj.clearSelection();
      this.selectedDayLayer.clearSelection();
      WidgetManager.getInstance().triggerWidgetOpen(this.attributeTableWidgetId).then(lang.hitch(this, function(wdgt) {
        wdgt.layerTabPageClose(this.surveyonDayLyrId, true);
      }));

      // get the current month and full year
      var currentYear = this.surveyCalendar.currentFocus.getFullYear();
      var currentMonth = this.surveyCalendar.currentFocus.getMonth();

      // get the first day in the month and its day in week
      // get Sunday before or on it
      this.beginingDate = new Date(currentYear, currentMonth, 1);
      this.beginingDate.setDate(this.beginingDate.getDate() - this.beginingDate.getDay());

      var beginingDateStr = this.formatDate2ISOString(this.beginingDate);

      // get the last day in the month and its day in week
      // get Sunday after or on it
      this.endingDate = new Date(currentYear, currentMonth + 1, 0);
      this.endingDate.setDate(this.endingDate.getDate() + 6 - this.endingDate.getDay() + 1);
      var endingDateStr = this.formatDate2ISOString(this.endingDate);

      this.initAssignmentsEachDayOnCalendar();

      var dateFilter = this.dateField_end + " >= TIMESTAMP '" + beginingDateStr +
        "' and " + this.dateField_begin + " < TIMESTAMP '" + endingDateStr + "'";

      return dateFilter;
    },

    initAssignmentsEachDayOnCalendar: function() {
      var nDays = this.surveyCalendar.dateModule.difference(this.beginingDate, this.endingDate, "day");
      this.assignmentsEachDayOnCalendar = new Array(nDays);
      this.assignmentsEachDayOnCalendar.fill(0);
    },

    queryDatesHavingSurveys: function(layerId) {
      this.map.infoWindow.hide();
      this.removeCellEventListeners();
      this.highlightLayer.clear();

      if(!this.parent.surveyManagerNeededParameters.node.toggleButton.checked) {
        this.assignmentLayerObj.clearSelection();
        this.selectedDayLayer.clearSelection();
        WidgetManager.getInstance().triggerWidgetOpen(this.attributeTableWidgetId).then(lang.hitch(this, function(wdgt) {
          wdgt.layerTabPageClose(this.surveyonDayLyrId, true);
        }));
        return;
      }

      var calendarQuery = new Query();
      //calendarQuery.where = "1 = 1";
      calendarQuery.outFields = ["*"];
      calendarQuery.returnGeometry = true;

      this.assignmentLayerObj.queryFeatures(calendarQuery,
        lang.hitch(this, 'highlightDaysOnCalendar'),
        lang.hitch(this, 'queryFailed'));
    },

    highlightDaysOnCalendar: function(response) {
      // get the unique local dates (not including time)
      //var features = this.assignmentLayerObj.
      var uniqueDates = [];
      if (response.features) {
        var nFeatures = response.features.length;
        for (var i = 0; i < nFeatures; i++) {
          var begin_date = response.features[i].attributes[this.dateField_begin];
          var end_date = response.features[i].attributes[this.dateField_end];
          this.countAssignmentsPerDay(begin_date, end_date);

        }
      }

      // highlight the dates
      for (var i = 0; i < this.assignmentsEachDayOnCalendar.length; i++) {
        // find the sequence number of the dateCell
        //var iDateCell = this.surveyCalendar.dateModule.difference(this.beginingDate, new Date(uniqueDates[i]), "day");
        if (this.assignmentsEachDayOnCalendar[i] > 0) {
          this.setCellWithSurvey(i, i);
        }
      }
    },

    countAssignmentsPerDay: function(begin_date_ms, end_date_ms) {
      begin_date = new Date(begin_date_ms);
      if (begin_date < this.beginingDate) {
        begin_date = this.beginingDate;
      }
      end_date = new Date(end_date_ms);
      if (end_date > this.endingDate) {
        end_date = this.endingDate;
      }

      var d = begin_date;
      var d_str = this.formatDate2LocalString(d, false, true);
      d = new Date(d_str);
      while (d <= end_date) {
        var nDays = this.surveyCalendar.dateModule.difference(this.beginingDate, d, "day");
        if (nDays >= 0) {
          this.assignmentsEachDayOnCalendar[nDays]++;
          d = date.add(d, "day", 1);
        }
      }
    },

    setCellWithSurvey: function(iDateCell, d) {
      var theCell = this.surveyCalendar.dateCells[iDateCell];
      if (iDateCell != null && iDateCell != undefined && iDateCell >= 0) {
        html.addClass(theCell, "dateWithAssignments");
        // define the handler when users click the dateCell
        this.cellsWithEvents.push(theCell);
        d = date.add(this.beginingDate, "day", iDateCell);
        this.cellEvents.push(on(theCell, "mouseenter", lang.hitch(this, 'query4Features4Date', d, "highlightFeatures")));
        this.cellEvents.push(on(theCell, "mouseleave", lang.hitch(this, 'removeHighlightSurveysOnMap', d)));
        this.cellEvents.push(on(theCell, "click", lang.hitch(this, 'query4Features4Date', d, "openInTable")));
      }
    },

    query4Features4Date: function(d, callbackFunctionName, event) {
      // query the layer and highlight those features
      //console.log("query4Features4Date on " + d);
      var existingLyrFilter = this.parent.filterManager.getWidgetFilter(this.layerId, this.parent.id);

      s_startDate = this.formatDate2ISOString(d);
      var d1 = date.add(d, "day", 1);
      s_endDate = this.formatDate2ISOString(d1);

      var dateFilter = this.dateField_end + " >= TIMESTAMP '" + s_startDate +
        "' and " + this.dateField_begin + " < TIMESTAMP '" + s_endDate + "'";

      var calendarQuery = new Query();
      calendarQuery.where = existingLyrFilter + " and (" + dateFilter + ")";
      calendarQuery.outFields = ["*"];
      calendarQuery.returnGeometry = true;

      this.assignmentLayerObj.queryFeatures(calendarQuery,
        lang.hitch(this, callbackFunctionName, d, calendarQuery.where),
        lang.hitch(this, 'queryFailed'));

    },

    highlightFeatures: function(d, sWhere, response) {
      this.highlightLayer.clear();
      //console.log("num of features to highlight: " + response.features.length);
      for (var i = 0; i < response.features.length; i++) {
        var newFeature = response.features[i].clone();
        newFeature.symbol = this.highlightSymbol;
        this.highlightLayer.add(newFeature);
      }

      /*
      if (response.features.length > 0) {
        var g = response.features[0];
        g.infoTemplate = this.assignmentInfoTemplate;
        this.map.infoWindow.setFeatures([g]);
        this.map.infoWindow.show(g.geometry, {
          closetFirst: true
        });
      } */

    },

    removeHighlightSurveysOnMap: function(d, event) {
      this.highlightLayer.clear();
    },

    openInTable: function(d, sWhere, response) {
      this.selectedDayLayer.setDefinitionExpression(sWhere);
      var lyrInfo = this.layerInfosObj.getLayerInfoById(this.surveyonDayLyrId);
      lyrInfo.title = this.surveyonDayLyrTitle;
      lyrInfo.name = this.surveyonDayLyrTitle;
      this.parent.publishData({
        'target': 'AttributeTable',
        'layer': lyrInfo
      });
    },

    onLayerInfosChanged: function(layerInfo, changeType, layerInfoSelf) {
      if (!layerInfoSelf || !layerInfo) {
        return;
      }
      if ('added' === changeType) {
        layerInfoSelf.getSupportTableInfo().then(lang.hitch(this, function(supportTableInfo) {
          if (supportTableInfo.isSupportedLayer) {
            this.publishData({
              'target': 'AttributeTable',
              'layer': layerInfoSelf
            });
          }
        }));
      } else if ('removed' === changeType) {
        // do something
      }
    },

    removeCellEventListeners: function() {

      for (var i = 0; i < this.cellsWithEvents.length; i++) {
        html.removeClass(this.cellsWithEvents[i], "dateWithAssignments");
      }
      this.cellsWithEvents = [];
      for (var i = 0; i < this.cellEvents.length; i++) {
        this.cellEvents[i].remove();
      }
      this.cellEvents = [];
    },

    formatDate2LocalString: function(date, bWithTime, b4LocalTime) {
      var dateFormat = "yyyy-MM-dd";
      if (b4LocalTime) {
          dateFormat = "yyyy/M/d"
      }
      if (bWithTime) {
        return locale.format(date, {
          selector: "date",
          datePattern: dateFormat + ' HH:mm:ss'
        });
      } else {
        return locale.format(date, {
          selector: "date",
          datePattern: dateFormat
        });
      }
    },

    formatDate2ISOString: function(d) {
      // ISO String format is 2018-11-26T08:00:00.000Z
      // get the format to TIMESTAMP 'YYYY-MM-DD HH:MI:SS'
      var s = d.toISOString().split("T");
      var sTime = s[1].split(".")[0];
      return s[0] + " " + sTime;
    },

    queryFailed: function(err) {
      console.error(err.message);
    }

  });

});
