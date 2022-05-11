define([
  "dijit/_WidgetBase",
  "dijit/_WidgetsInTemplateMixin",
  "dojo/_base/declare",
  "dojo/_base/lang",
  "dojo/_base/array",
  "dojo/_base/html",
  "dojo/dom-construct",
  "dojo/on",
  "dojo/keys",
  "dojo/dom-class",
  "dijit/focus",
  "dojo/query",
  "dojo/Deferred",
  "dojo/store/Memory",
  "dojo/date/locale",
  "jimu/dijit/CheckBox",
  "jimu/dijit/DropMenu",
  "jimu/dijit/LoadingShelter",
  "jimu/utils",
  "esri/tasks/query",
  "esri/symbols/PictureMarkerSymbol",
  "esri/graphic",
  "esri/layers/FeatureLayer",
  "dijit/_TemplatedMixin",
  "dojo/text!./SurveyEditor.html",
  "dojo/dom-class",
  "dojo/dom-style",
  "esri/toolbars/edit",
  "dijit/form/TextBox",
  "dijit/form/DateTextBox",
  "dijit/form/SimpleTextarea",
  "dijit/form/ComboBox",
  "dijit/form/FilteringSelect",
  "dijit/form/TimeTextBox",
], function (
  _WidgetBase,
  _WidgetsInTemplateMixin,
  declare,
  lang,
  arrayUtil,
  html,
  domConstruct,
  on,
  keys,
  domClass,
  focusUtil,
  query,
  Deferred,
  Memory,
  locale,
  CheckBox,
  DropMenu,
  LoadingShelter,
  jimuUtils,
  esriQuery,
  PictureMarkerSymbol,
  Graphic,
  FeatureLayer,
  _TemplatedMixin,
  template,
  domClass,
  domStyle,
  Edit
) {
  return declare([_WidgetBase, _TemplatedMixin, _WidgetsInTemplateMixin], {
    templateString: template,
    currentAssignment: null,
    priorityDomain: null,
    statusDomain: null,
    modifyGeomEnabled: false,
    modifiedGeom: null,

    constructor: function (options) {
      this.assignmentLayer = options.assignmentLayer || null;
      this.refreshLayers = options.refreshLayers || null;
      this.siteLayer = options.siteLayer || null;
      this.surveyors = options.surveyors || null;
      this.surveyorField = options.surveyorField || null;
      this.map = options.map || null;
      this.mapAssignmentLayer = options.mapAssignmentLayer || null;
    },

    postMixInProperties: function () {
      this.inherited(arguments);
    },

    startup: function () {
      console.log("editor started");
      this.inherited(arguments);
      this.mapClickEnabled = false;
      this._populateSurveyorList();
      this._searchDomainLists();
      this._populateDynamicList(this.assignmentLayer, "rtss_program_name <> '' and (status <> 'completed' and status <> 'cancelled')", ["rtss_program_name"], this.cProgNameCtrl);
      this._populateDynamicList(this.assignmentLayer, "rtss_test_officer <> '' and (status <> 'completed' and status <> 'cancelled')", ["rtss_test_officer"], this.cTestOffCtrl);
      // this._populateDynamicList(this.assignmentLayer, "rtss_test_officer <> '' and (status <> 'completed' and status <> 'cancelled')", ['rtss_test_officer','rtss_test_officer_phone'], this.cTestOffCtrl);
      this._populateDynamicList(this.assignmentLayer, "rtss_location IS NOT NULL AND rtss_location <> ''", ["rtss_location"], this.cLocCtrl);
      this.btnSubmit.disabled = true;
      this.editToolbar = new Edit(this.map);
    },

    handleTestOfficerSelectionChange: function (evt) {
      // var testOfficer = this.cTestOffCtrl.get("item");
      // if (testOfficer){
      //   this.cTestOffPNCtrl.set("value", testOfficer['rtss_test_officer_phone']);
      // }
      // else{
      //   this.cTestOffPNCtrl.set("value", "");
      // }
    },

    handleDateTimeChange: function (evt) {
      //check and make sure dates and times are filled in
      var begDtValue = this.cBegDtCtrl.get("value");
      var begDtTmValue = this.cBegDtTmCtrl.get("value");
      var endDtValue = this.cEndDtCtrl.get("value");
      var endDtTmValue = this.cEndDtTmCtrl.get("value");

      //  todo  make sure beginning date is before ending date
      this.btnSubmit.disabled = false;

      // If the date is filled in, but the time is blank, default it to midnight
      if (begDtValue && !begDtTmValue) {
        this.cBegDtTmCtrl.set("value", "T00:00:00");
      }
      if (endDtValue && !endDtTmValue) {
        this.cEndDtTmCtrl.set("value", "T00:00:00");
      }

      if (begDtValue && begDtTmValue && endDtValue && endDtTmValue) {
        begDtTmValue.setTime(begDtTmValue.getTime() - begDtTmValue.getTimezoneOffset() * 60 * 1000);
        var fromTimeEpoch = begDtTmValue.getTime();
        var fromDateEpoch = begDtValue.getTime();
        var fromDate = new Date(fromDateEpoch + fromTimeEpoch);

        endDtTmValue.setTime(endDtTmValue.getTime() - endDtTmValue.getTimezoneOffset() * 60 * 1000);
        var toTimeEpoch = endDtTmValue.getTime();
        var toDateEpoch = endDtValue.getTime();
        var toDate = new Date(toDateEpoch + toTimeEpoch);

        if (toDate < fromDate) {
          domStyle.set(this.datemsg, "display", "block");
          this.btnSubmit.disabled = true;
          return;
        } else {
          domStyle.set(this.datemsg, "display", "none");
        }
        var fdt = locale.format(fromDate, { selector: "date", datePattern: "MM/dd/yyyy H:m" });
        var tdt = locale.format(toDate, { selector: "date", datePattern: "MM/dd/yyyy H:m" });
        this._updateListAvailableSurveyors(fdt, tdt);
      }
    },

    handleSurveyorChange: function (evt) {
      console.log("surveyor", evt);
      if (evt > 0 && this.cStatusCtrl.get("displayedValue") == "Unassigned") {
        //0 is empty value
        this.cStatusCtrl.set("displayedValue", "Assigned");
      }
    },

    checkCommentLength: function () {
      var val = this.cLocNoteCtrl.value;
      if (val) {
        this.cLocNoteCnt.innerHTML = 255 - val.length + " characters remaining";
      }
    },

    _searchDomainLists: function () {
      var field = this.assignmentLayer.getField("priority");
      if (field) {
        if (field.domain && field.domain.type.toLowerCase() == "codedvalue") {
          var priorityList = lang.clone(field.domain.codedValues);
          this._populateDomainLists(priorityList, this.cPriorityCtrl, false);
        }
      }

      field = this.assignmentLayer.getField("status");
      if (field) {
        if (field.domain && field.domain.type.toLowerCase() == "codedvalue") {
          var statusList = lang.clone(field.domain.codedValues);
          this._populateDomainLists(statusList, this.cStatusCtrl, true, "A");
        }
      }
    },

    _populateDomainLists: function (domainList, ctrl, sort, direction) {
      arrayUtil.forEach(domainList, function (value, i) {
        value["id"] = i;
      });

      var store = new Memory({ data: domainList });

      ctrl.set("labelAttr", "name");
      ctrl.set("store", store);
      ctrl.set("searchAttr", "name");
      if (sort) {
        ctrl.set("fetchProperties", { sort: [{ attribute: "name", descending: direction == "D" }] });
      }
    },

    _searchDynamicList: function (layer, defExpress, distinctFields) {
      var query = new esriQuery();
      query.where = defExpress;
      query.outFields = distinctFields;
      query.returnDistinctValues = true;
      query.returnGeometry = false;
      query.orderByFields = distinctFields;

      var def = layer.queryFeatures(query);
      return def;
    },

    _populateDynamicList: function (layer, defExpress, distinctFields, ctrl) {
      this._searchDynamicList(layer, defExpress, distinctFields).then(
        lang.hitch(this, function (featureSet) {
          var features = featureSet.features;
          var store = this._populateStore(features);
          ctrl.set("store", store);
          ctrl.set("searchAttr", distinctFields[0]);
        })
      );
    },

    _updateListAvailableSurveyors: function (fromDate, toDate) {
      this._searchUnavailableSurveyors(fromDate, toDate).then(
        lang.hitch(this, function (featureSet) {
          var busySurveyor = [];
          var store;

          arrayUtil.forEach(
            featureSet.features,
            lang.hitch(this, function (feature) {
              var surveyorName = feature.attributes["surveyor"];
              if (surveyorName != null && surveyorName != "") {
                busySurveyor.push(surveyorName.toUpperCase());
              }
            })
          );

          if (this.currentAssignment) {
            var surveyor = this.currentAssignment.attributes["surveyor"];
            if (surveyor && surveyor.length > 0) {
              if (busySurveyor.indexOf(surveyor) > -1) {
                busySurveyor.splice(busySurveyor.indexOf(surveyor), 1);
              }
            }
          }
          var hasAvailableSurveyors = false;
          var store = this.cSurveyorCtrl.get("store");
          store.query().forEach(function (item) {
            if (item["id"] == 0) {
              item["available"] = true;
            } else {
              if (busySurveyor.indexOf(item.name) > -1) {
                item["available"] = false;
              } else {
                item["available"] = true;
                hasAvailableSurveyors = true;
              }
            }
            store.put(item);
          });

          if (this.currentAssignment) {
            this.cSurveyorCtrl.set("displayedValue", this.currentAssignment.attributes["surveyor"]);
          }
          //todo - if hasAvailableSurveyors == false then need to disable the submit button
        })
      );
    },

    _searchUnavailableSurveyors: function (fromDate, toDate) {
      var query = new esriQuery();

      query.where = "(survey_begin < DATE '" + fromDate + "' and survey_end > DATE '" + fromDate + "') or (survey_begin > DATE '" + fromDate + "' and survey_begin < DATE '" + toDate + "')";
      query.outFields = ["surveyor"];
      query.returnDistinctValues = true;
      query.returnGeometry = false;
      query.orderByFields = ["surveyor"];
      var def = this.assignmentLayer.queryFeatures(query);
      return def;
    },

    _populateSurveyorList: function () {
      if (this.surveyors) {
        this.surveyorList = [];

        var i = 0;
        var noSurveyor = {};
        noSurveyor["name"] = "";
        noSurveyor["id"] = i;
        noSurveyor["available"] = true;
        i++;
        this.surveyorList.push(noSurveyor);

        arrayUtil.forEach(
          this.surveyors,
          lang.hitch(this, function (s) {
            var surveyor = {};
            surveyor["name"] = s.toUpperCase();
            surveyor["id"] = i;
            surveyor["available"] = false;
            i++;
            this.surveyorList.push(surveyor);
          })
        );
        var store = new Memory({ data: this.surveyorList });
        this.cSurveyorCtrl.set("labelAttr", "name");
        this.cSurveyorCtrl.set("store", store);
        this.cSurveyorCtrl.set("searchAttr", "name");
        this.cSurveyorCtrl.set("query", { available: true });
      }
    },

    _populateStore: function (features) {
      var featColl = [];
      var id = 0;
      arrayUtil.forEach(
        features,
        lang.hitch(this, function (feature) {
          var att = feature.attributes;
          att["id"] = id;
          id++;
          featColl.push(att);
        })
      );
      return new Memory({ data: featColl });
    },

    submitAssignment: function () {
      var feature;
      if (this.currentAssignment) {
        //modifying existing assignment
        feature = this.currentAssignment;
        if (this.editToolbar) {
          let editState = this.editToolbar.getCurrentState();
          if (editState.isModified) {
            this.modifiedGeom = editState.graphic.geometry;
          }
        }
        if (this.modifiedGeom) {
          feature.geometry = this.modifiedGeom;
        }
        this._deactivateModifyGeom();
        this._updateFeatureAttributes(feature);
        this.assignmentLayer.applyEdits([], [feature], [], lang.hitch(this, this._handleEditSuccess), lang.hitch(this, this._handleEditError));
      } else {
        if (this.assignGraphic) {
          feature = new Graphic(this.assignGraphic.geometry, null, {});
          this._updateFeatureAttributes(feature);
          this.assignmentLayer.applyEdits([feature], [], [], lang.hitch(this, this._handleEditSuccess), lang.hitch(this, this._handleEditError));
          this._populateDynamicList(this.assignmentLayer, "rtss_location IS NOT NULL AND rtss_location <> ''", ["rtss_location"], this.cLocCtrl);
        }
      }
    },

    _handleEditSuccess: function (adds, updates, deletes) {
      this.map.graphics.clear();
      // this.assignmentLayer.refresh();
      arrayUtil.forEach(
        this.refreshLayers,
        lang.hitch(this, function (layer) {
          layer.refresh();
        })
      );

      console.log(adds, updates, deletes);
      if (adds.length > 0) {
        if (adds[0].success) {
          var oid = adds[0]["objectId"];
          this.msg.innerHTML = "The assignment was successfully created.";
          this.emit("editsuccess", { assignment: oid });
          this.backToMainPanel();
        }
      } else if (updates.length > 0) {
        if (updates[0].success) {
          var oid = updates[0]["objectId"];
          this.msg.innerHTML = "The assignment was successfully updated.";
          this.emit("editsuccess", { assignment: oid });
          this.backToMainPanel();
        }
      }
      // this._clearEditSettings();
    },

    _handleEditError: function (error) {
      console.log(error);
    },

    _updateFeatureAttributes: function (feature) {
      var begDtValue = this.cBegDtCtrl.get("value");
      var begDtTmValue = this.cBegDtTmCtrl.get("value");
      var endDtValue = this.cEndDtCtrl.get("value");
      var endDtTmValue = this.cEndDtTmCtrl.get("value");

      if (begDtValue && begDtTmValue) {
        begDtTmValue.setTime(begDtTmValue.getTime() - begDtTmValue.getTimezoneOffset() * 60 * 1000);
        var fromTimeEpoch = begDtTmValue.getTime();
        var fromDateEpoch = begDtValue.getTime();
        var fromDate = new Date(fromDateEpoch + fromTimeEpoch);
        feature.attributes["survey_begin"] = fromDate.getTime();
      }

      if (endDtValue && endDtTmValue) {
        endDtTmValue.setTime(endDtTmValue.getTime() - endDtTmValue.getTimezoneOffset() * 60 * 1000);
        var toTimeEpoch = endDtTmValue.getTime();
        var toDateEpoch = endDtValue.getTime();
        var toDate = new Date(toDateEpoch + toTimeEpoch);
        feature.attributes["survey_end"] = toDate.getTime();
      }

      var projDtValue = this.cPrjDtCtrl.get("value");
      if (projDtValue) feature.attributes["project_date"] = this.cPrjDtCtrl.get("value").getTime();

      var location = this.cLocCtrl.get("displayedValue");
      feature.attributes["rtss_location"] = location;
      var locNotes = this.cLocNoteCtrl.value;
      feature.attributes["location_notes"] = locNotes;
      var progName = this.cProgNameCtrl.get("displayedValue");
      feature.attributes["rtss_program_name"] = progName;
      var testOfficer = this.cTestOffCtrl.get("displayedValue");
      feature.attributes["rtss_test_officer"] = testOfficer;
      var testOfficerPhNo = this.cTestOffPNCtrl.get("value");
      feature.attributes["rtss_test_officer_phone"] = testOfficerPhNo;
      var adss = this.cADSSCtrl.get("value");
      feature.attributes["rtss_adss"] = adss;
      var wbs = this.cWBSCtrl.get("value");
      feature.attributes["rtss_wbs_no"] = wbs;
      var priorityItem = this.cPriorityCtrl.get("item");
      if (priorityItem) feature.attributes["priority"] = priorityItem.code;
      var statusItem = this.cStatusCtrl.get("item");

      var statNotes = this.cStatNoteCtrl.value;
      feature.attributes["status_notes"] = statNotes;
      var surveyorItem = this.cSurveyorCtrl.get("item");
      if (surveyorItem) feature.attributes["surveyor"] = surveyorItem.name;

      if (statusItem) {
        feature.attributes["status"] = statusItem.code;
      } else {
        if (surveyorItem) {
          feature.attributes["status"] = "assigned";
        } else {
          feature.attributes["status"] = "unassigned";
        }
      }
      var surveyorNotes = this.cSurveyNoteCtrl.value;
      feature.attributes["surveyor_notes"] = surveyorNotes;
    },

    activateMapClick: function () {
      if (!domClass.contains(this.btnActivateMapClick, "active")) {
        this._activateEditorDraw();
      } else {
        this._deactivateEditorDraw();
      }
    },

    activateModifyGeomClick: function () {
      if (!this.modifyGeomEnabled) {
        this._activateModifyGeom();
      } else {
        this._deactivateModifyGeom();
      }
    },

    _activateModifyGeom: function () {
      if (!this.currentAssignment || !this.currentAssignment.geometry) {
        return;
      }
      this.map.setInfoWindowOnClick(false);
      if (this.map.infoWindow.isShowing) {
        this.map.infoWindow.hide();
      }

      this.map.setMapCursor("pointer");
      this.modifyGeomEnabled = true;
      this.modifyMsg.innerHTML = "Drag the assignemnt point to the desired location, then click the button again to finish.";
      domClass.add(this.btnModifyGeometry, "active");

      // store the original geometry for later use
      this.currentAssignment.origGeom = this.currentAssignment.geometry.toJson();
      var query = new esriQuery();
      query.objectIds = [this.currentAssignment.attributes["OBJECTID"]];
      this.mapAssignmentLayer.selectFeatures(
        query,
        FeatureLayer.SELECTION_NEW,
        lang.hitch(this, function (features) {
          if (features && features.length > 0) {
            setTimeout(
              lang.hitch(this, function () {
                this._activateEditToolbar(features[0]);
              }),
              100
            );
          }
        }),
        lang.hitch(this, function () {
          deferred.resolve("failed");
        })
      );
    },

    _activateEditToolbar: function (feature) {
      var layer = feature.getLayer();
      if (this.editToolbar.getCurrentState().tool !== 0) {
        this.editToolbar.deactivate();
      }
      switch (layer.geometryType) {
        case "esriGeometryPoint":
          this.editToolbar.activate(Edit.MOVE, feature);
          break;
        case "esriGeometryPolyline":
        case "esriGeometryPolygon":
          this.editToolbar.activate(Edit.EDIT_VERTICES | Edit.MOVE | Edit.ROTATE | Edit.SCALE, feature);
          break;
      }
    },

    _deactivateModifyGeom: function () {
      this.map.setInfoWindowOnClick(true);
      if (this.mapClickHandler) {
        this.mapClickHandler.pause();
      }
      // Get the modified geometry
      let editState = this.editToolbar.getCurrentState();
      if (editState.isModified) {
        this.modifiedGeom = editState.graphic.geometry;
      }

      domClass.remove(this.btnModifyGeometry, "active");
      this.map.setMapCursor("default");
      this.modifyGeomEnabled = false;
      this.modifyMsg.innerHTML = "Click to modify the assignment location";
      if (this.editToolbar.getCurrentState().tool !== 0) {
        this.editToolbar.deactivate();
      }
    },

    assignLocation: function (e) {
      var pt = e.mapPoint;

      if (this.mapClickEnabled !== undefined && this.mapClickEnabled !== null && this.mapClickEnabled === true) {
        this.addGraphicToMap(pt);
      }
    },

    addGraphicToMap: function (mapPoint) {
      if (this.assignGraphic) this.map.graphics.remove(this.assignGraphic);
      var s = new PictureMarkerSymbol("widgets/Assignments/images/here.png", 30, 40);
      // s.xoffset = -9;
      s.yoffset = 20;
      // var s = new SimpleMarkerSymbol(SimpleMarkerSymbol.STYLE_CIRCLE, 12, new SimpleLineSymbol(SimpleLineSymbol.STYLE_SOLID, new Color("#474747"), 1), new Color("#FF0000"));
      var g = new Graphic(mapPoint, s);
      this.assignGraphic = g;
      this.map.graphics.add(g);
      this.btnSubmit.disabled = false;
    },

    setCurrentAssignment: function (id) {
      //todo update colors in drop down list if status changes from unassigned
      if (id) {
        //modifying existing feature
        //query assignment for feature
        this._searchForAssignmentById(id).then(
          lang.hitch(this, function (featureSet) {
            var features = featureSet.features;
            if (features.length > 0) {
              this.currentAssignment = features[0];
              this._updateEditorControls(features[0]);
              this.btnSubmit.disabled = false;
              domStyle.set(this.cIDRow, "display", "block");
            }
          })
        );
        // Hide the new assignment location button section
        html.setStyle(this.newGeomSection, "display", "none");
        // Show the modify assignment location button section
        html.setStyle(this.modifyGeomSection, "display", "block");
      } else {
        //new assignment
        this.btnSubmit.disabled = true;
        domStyle.set(this.cIDRow, "display", "none");
        //set status to unassigned
        this.cStatusCtrl.set("displayedValue", "Unassigned");
        // Hide the modify assignment location button section
        html.setStyle(this.modifyGeomSection, "display", "none");
        // Show the new assignment location button section
        html.setStyle(this.newGeomSection, "display", "block");
        this.showEditor();
      }
    },

    _updateEditorControls: function (feature) {
      this.cIDCtrl.set("value", feature.attributes["assignment_uid"]);

      var begDate = feature.attributes["survey_begin"];
      if (begDate) {
        this.cBegDtCtrl.set("value", new Date(begDate));
        this.cBegDtTmCtrl.set("value", new Date(begDate));
      }
      var endDate = feature.attributes["survey_end"];
      if (endDate) {
        this.cEndDtCtrl.set("value", new Date(endDate));
        this.cEndDtTmCtrl.set("value", new Date(endDate));
      }

      var projDate = feature.attributes["project_date"];
      if (projDate) {
        this.cPrjDtCtrl.set("value", new Date(projDate));
      }

      this.cLocCtrl.set("displayedValue", feature.attributes["rtss_location"]);
      this.cLocNoteCtrl.value = feature.attributes["location_notes"];
      this.cProgNameCtrl.set("displayedValue", feature.attributes["rtss_program_name"]);
      this.cTestOffCtrl.set("displayedValue", feature.attributes["rtss_test_officer"]);

      this.cTestOffPNCtrl.set("value", feature.attributes["rtss_test_officer_phone"]);
      this.cADSSCtrl.set("value", feature.attributes["rtss_adss"]);
      this.cWBSCtrl.set("value", feature.attributes["rtss_wbs_no"]);
      this.cStatNoteCtrl.value = feature.attributes["status_notes"];
      this.cSurveyNoteCtrl.value = feature.attributes["surveyor_notes"];

      var priorityCode = feature.attributes["priority"];
      if (priorityCode) {
        var store = this.cPriorityCtrl.get("store");
        store.query({ code: priorityCode }).forEach(
          lang.hitch(this, function (item) {
            this.cPriorityCtrl.set("displayedValue", item.name);
          })
        );
      }

      var statusCode = feature.attributes["status"];
      if (statusCode) {
        var store = this.cStatusCtrl.get("store");
        store.query({ code: statusCode }).forEach(
          lang.hitch(this, function (item) {
            this.cStatusCtrl.set("displayedValue", item.name);
          })
        );
      }
    },

    _searchForAssignmentById: function (id) {
      var query = new esriQuery();
      query.objectIds = [id];
      query.outFields = ["*"];
      query.returnGeometry = true;
      query.outSpatialReference = this.map.spatialReference;

      var def = this.assignmentLayer.queryFeatures(query);
      return def;
    },

    showEditor: function () {
      this._activateEditorDraw();
      // this.map.setInfoWindowOnClick(false);
      // if (domClass.contains(this.btnActivateMapClick, "active")) {
      //   //if draw assignment on map is already activated
      //   this.map.setMapCursor("crosshair");
      // }
      // else this.activateMapClick();

      // if (!this.mapClickHandler)
      //     this.mapClickHandler = on.pausable(this.map, "click", lang.hitch(this, this.assignLocation));
      //   else this.mapClickHandler.resume();
    },

    closeEditor: function () {
      this._deactivateEditorDraw();
      // this.map.setInfoWindowOnClick(true);
      // if (this.mapClickHandler){
      //     this.mapClickHandler.pause();
      // }
      // this.map.setMapCursor("default");
    },

    _activateEditorDraw: function () {
      this.map.setInfoWindowOnClick(false);

      domClass.add(this.btnActivateMapClick, "active");
      domClass.add(this.cLocMsg, "active");
      this.mapClickEnabled = true;
      this.map.setMapCursor("crosshair");

      if (!this.mapClickHandler) this.mapClickHandler = on.pausable(this.map, "click", lang.hitch(this, this.assignLocation));
      else this.mapClickHandler.resume();
    },

    _deactivateEditorDraw: function () {
      this.map.setInfoWindowOnClick(true);
      if (this.mapClickHandler) {
        this.mapClickHandler.pause();
      }
      domClass.remove(this.btnActivateMapClick, "active");
      domClass.remove(this.cLocMsg, "active");
      this.map.setMapCursor("default");
      this.mapClickEnabled = false;
    },

    _clearEditSettings: function () {
      this.btnSubmit.disabled = true;
      domStyle.set(this.cIDRow, "display", "none");

      this.cIDCtrl.set("value", "");
      this.cBegDtCtrl.set("value", null);
      this.cBegDtTmCtrl.set("value", null);
      this.cEndDtCtrl.set("value", null);
      this.cEndDtTmCtrl.set("value", null);
      this.cPrjDtCtrl.set("value", null);
      this.cLocCtrl.set("value", null);

      this.cLocNoteCtrl.value = "";
      this.cProgNameCtrl.set("value", null);
      this.cTestOffCtrl.set("value", null);

      this.cTestOffPNCtrl.set("value", null);
      this.cADSSCtrl.set("value", null);
      this.cWBSCtrl.set("value", null);
      this.cStatNoteCtrl.value = "";
      this.cSurveyNoteCtrl.value = "";

      this.cPriorityCtrl.set("item", null);
      this.cStatusCtrl.set("item", null);
      this.cSurveyorCtrl.set("item", null);
      var store = this.cSurveyorCtrl.get("store");
      store.query().forEach(function (item) {
        item["available"] = false;
        store.put(item);
      });
      this.msg.innerHTML = "";
    },

    backToMainPanel: function () {
      this.map.graphics.clear();
      this.currentAssignment = null;
      this.assignGraphic = null;
      this._clearEditSettings();
      this.closeEditor();
      this.emit("canceledit", null);
      if (this.modifyGeomEnabled) {
        this._deactivateModifyGeom();
      }
    },
  });
});
