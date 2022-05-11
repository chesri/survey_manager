///////////////////////////////////////////////////////////////////////////
// Copyright © Esri. All Rights Reserved.
//
// Licensed under the Apache License Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
///////////////////////////////////////////////////////////////////////////
define([
  "dojo/_base/declare",
  "dijit/_WidgetsInTemplateMixin",
  "dojo/on",
  "dojo/_base/lang",
  "dojo/_base/array",
  "dojo/date/locale",
  "dojo/Deferred",
  "dojo/store/Memory",
  "dojo/dom-style",
  "dijit/focus",
  "jimu/BaseWidget",
  "jimu/LayerInfos/LayerInfos",
  "jimu/utils",
  "jimu/portalUtils",
  "jimu/portalUrlUtils",
  "esri/tasks/query",
  "esri/layers/FeatureLayer",
  "esri/symbols/SimpleMarkerSymbol",
  "esri/Color",
  "esri/arcgis/Portal",
  "./Selector",
  "./SurveyEditor",
  "./UploadDocGP",
  "dijit/form/FilteringSelect",
  "dijit/form/Select",
  "dojo/domReady!",
], function (
  declare,
  _WidgetsInTemplateMixin,
  on,
  lang,
  arrayUtil,
  locale,
  Deferred,
  Memory,
  domStyle,
  focusUtils,
  BaseWidget,
  LayerInfos,
  utils,
  portalUtils,
  portalUrlUtils,
  Query,
  FeatureLayer,
  SimpleMarkerSymbol,
  Color,
  arcgisPortal,
  Selector,
  SurveyEditor,
  UploadDocGP,
  FilteringSelect,
  Select
) {
  //To create a widget, you need to derive from BaseWidget.
  return declare([BaseWidget, _WidgetsInTemplateMixin], {
    // Custom widget code goes here

    baseClass: "jimu-widget-assignments",

    //this property is set by the framework when widget is loaded.
    name: "Assignments",

    assignmentLayer: null,
    mapAssignmentLayer: null,
    surveyors: [],
    surveyorField: "name",
    siteLayer: null,
    siteField: "site_name",
    refreshLayers: [],
    //methods to communication with app container:

    postCreate: function () {
      this.inherited(arguments);
      console.log("postCreate");
    },

    startup: function () {
      this.inherited(arguments);
      this._initSelector();
      // this.mapIdNode.innerHTML = 'map id:' + this.map.id;
      this._initLookupLayers();
      this._findAssignmentLayer();
      this._populateAssignmentList("project_date", "D", null);
      this.assignmentLayer.on(
        "load",
        lang.hitch(this, function (layer) {
          console.log("init");
          // Get the list of surveyors by querying the surveyors group on the portal
          var portal = new arcgisPortal.Portal(this.appConfig.portalUrl);
          var params = {
            f: "json",
            q: "Yuma Surveyor",
          };
          portal.queryGroups(params).then(
            lang.hitch(this, function (groupsResults) {
              if (groupsResults.results && groupsResults.results.length > 0) {
                arrayUtil.forEach(
                  groupsResults.results,
                  lang.hitch(this, function (group) {
                    if (group.title === "Yuma Surveyor") {
                      group.getMembers().then(
                        lang.hitch(this, function (members) {
                          this.surveyors = members.users.concat(members.admins);
                          this._initEditor();
                          utils.initFirstFocusNode(this.domNode, this.surveyEditWidget.cBegDtCtrl);
                          focusUtils.focus(this.surveyEditWidget.cBegDtCtrl);
                          utils.initLastFocusNode(this.domNode, this.surveyEditWidget.cSurveyNoteCtrl);
                        })
                      );
                    }
                  })
                );
              }
            })
          );
        })
      );

      // this.surveyEditWidget.showEditor();

      this.btnModify.disabled = true;
      this.btnUpload.disabled = true;
    },

    _initLookupLayers: function () {
      this.assignmentLayer = new FeatureLayer(this.config.assignmentLayer, { outFields: ["*"] });
      this.siteLayer = new FeatureLayer(this.config.siteLayer, { outFields: [this.siteField] });
    },

    _initSelector: function () {
      this.sel = new Selector({
        items: this.config.categories,
      });
      this.sel.placeAt(this.cSortPanel);
      this.sel.on("change", this._setCategory.bind(this));
      this.sel.startup();
    },

    _initEditor: function () {
      this.surveyEditWidget = new SurveyEditor({
        assignmentLayer: this.assignmentLayer,
        refreshLayers: this.refreshLayers,
        siteLayer: this.siteLayer,
        surveyors: this.surveyors,
        surveyorField: this.surveyorField,
        map: this.map,
        mapAssignmentLayer: this.mapAssignmentLayer,
      });
      this.surveyEditWidget.on("canceledit", lang.hitch(this, this._cancelEdit));
      this.surveyEditWidget.on("editsuccess", lang.hitch(this, this._refreshAssignments));
      this.surveyEditWidget.placeAt(this.panelCreate);
      // this.surveyEditWidget.startup();

      this.uploadDocGPWidget = new UploadDocGP({
        assignmentId: 0,
        map: this.map,
        uploadUrl: this.config.geoprocessing.uploadUrl,
        gpsToolUrl: this.config.geoprocessing.gpsToolUrl,
        tsToolUrl: this.config.geoprocessing.tsToolUrl,
      });
      this.uploadDocGPWidget.on("cancelupload", lang.hitch(this, this._cancelEdit));
      this.uploadDocGPWidget.placeAt(this.panelUpload);
      // this.uploadDocGPWidget.startup();
    },

    _findAssignmentLayer: function () {
      var opLayers = this.map.itemInfo.itemData.operationalLayers;
      arrayUtil.forEach(
        opLayers,
        lang.hitch(this, function (opLayer) {
          // if (opLayer.layerType == "ArcGISFeatureLayer" && opLayer.title.toLowerCase() == this.config.assignmentLayer.toLowerCase()){
          if (opLayer.layerType == "ArcGISFeatureLayer" && this.config.refreshLayers.indexOf(opLayer.title) > -1) {
            this.refreshLayers.push(opLayer.layerObject);
            if (this.config.assignmentBySurveyorName.indexOf(opLayer.title) > -1) {
              this.mapAssignmentLayer = opLayer.layerObject;
            }
            // this.assignmentLayer = opLayer.layerObject;
            //set selection symbol
            // var selectionSymbol = new SimpleMarkerSymbol(SimpleMarkerSymbol.STYLE_CIRCLE, 16, null, new Color([0, 255, 255, 0.8]));
            // this.assignmentLayer.setSelectionSymbol(selectionSymbol);
          }
          // else if (opLayer.layerType == "ArcGISFeatureLayer" && opLayer.title.toLowerCase() == this.config.siteLayer.toLowerCase()){
          //   this.siteLayer = opLayer.layerObject;
          // }
        })
      );
    },

    _refreshAssignments: function (evt) {
      console.log("refresh", evt);
      this.cAssignments.set("value", null);
      this.btnModify.disabled = true;
      this.btnUpload.disabled = true;
      var sortCatIndex = this.sel.selectedIndex;
      var curSortSettings = this.config.categories[sortCatIndex];
      if (curSortSettings.label == "Project Date") {
        this.assignFieldLBL.innerHTML = "Project Date - Program Name - Test Officer - Surveyor:";
      } else if (curSortSettings.label == "Program Name") {
        this.assignFieldLBL.innerHTML = "Program Name - Project Date - Test Officer - Surveyor:";
      } else if (curSortSettings.label === "Surveyor Name") {
        this.assignFieldLBL.innerHTML = "Surveyor - Project Date - Program Name - Test Officer:";
      } else {
        this.assignFieldLBL.innerHTML = "Test Officer - Project Date - Program Name - Surveyor:";
      }
      this._populateAssignmentList(curSortSettings["field"], curSortSettings["direction"], evt["assignment"]);

      // if (evt["assignment"]){
      //   this.zoomToAssignment(evt["assignment"]);
      // }
    },

    _searchAssignments: function (queryExpression) {
      var query = new Query();
      query.where = queryExpression;
      query.outFields = ["*"];
      query.returnGeometry = true;
      query.outSpatialReference = this.map.spatialReference;

      var def = this.assignmentLayer.queryFeatures(query);
      return def;
    },

    _searchSurveyors: function () {},

    _searchSites: function () {},

    _setCategory: function (evt) {
      this.cAssignments.set("item", null);
      this.btnModify.disabled = true;
      this.btnUpload.disabled = true;
      this._clearAssignmentSelection();
      var fieldName = evt.item.field;
      var direction = evt.item.direction;

      if (evt.item.label == "Project Date") {
        this.assignFieldLBL.innerHTML = "Project Date - Program Name - Test Officer - Surveyor:";
      } else if (evt.item.label == "Program Name") {
        this.assignFieldLBL.innerHTML = "Program Name - Project Date - Test Officer  - Surveyor:";
      } else if (evt.item.label === "Surveyor Name") {
        this.assignFieldLBL.innerHTML = "Surveyor - Project Date - Program Name - Test Officer:";
      } else {
        this.assignFieldLBL.innerHTML = "Test Officer - Project Date - Program Name - Surveyor:";
      }
      var labelField = this._getLabelField(fieldName);
      this.cAssignments.set("labelAttr", labelField);
      this.cAssignments.set("searchAttr", labelField.replace("label", "display"));
      this.cAssignments.set("fetchProperties", { sort: [{ attribute: fieldName, descending: direction == "D" }] });
    },

    _populateAssignmentList: function (sortBy, direction, assignmentId) {
      this._searchAssignments("status <> 'completed' and status <> 'cancelled'").then(
        lang.hitch(this, function (featureSet) {
          var features = featureSet.features;
          var store = this._populateStore(features);
          var labelField = this._getLabelField(sortBy);
          this.cAssignments.set("labelAttr", labelField);
          this.cAssignments.set("labelType", "html");
          this.cAssignments.set("store", store);
          this.cAssignments.set("searchAttr", labelField.replace("label", "display"));
          this.cAssignments.set("fetchProperties", { sort: [{ attribute: sortBy, descending: direction == "D" }] });

          if (assignmentId) {
            console.log("assignment", assignmentId);
            var store = this.cAssignments.get("store");
            store.query({ id: assignmentId }).forEach(
              lang.hitch(this, function (item) {
                this.cAssignments.set("item", item);
              })
            );
          }
        })
      );
    },

    _getLabelField: function (fieldName) {
      switch (fieldName.toLowerCase()) {
        case "project_date":
          return "label_project_date";
        case "rtss_program_name":
          return "label_rtss_program_name";
        case "rtss_test_officer":
          return "label_rtss_test_officer";
        case "surveyor":
          return "label_surveyor";
        default:
          return "label_project_date";
      }
    },

    _sortFeatures: function (features, sortField, direction) {
      features.sort(function (a, b) {
        if (direction == "A") return a.attributes[sortField] - b.attributes[sortField];
        //ascending order
        else {
          return b.attributes[sortField] - a.attributes[sortField];
        }
      });
    },

    _populateStore: function (features) {
      var featColl = [];
      arrayUtil.forEach(
        features,
        lang.hitch(this, function (feature) {
          var att = feature.attributes;
          att["id"] = att["OBJECTID"];
          att["shape"] = feature.geometry;
          var tdt = new Date(att["project_date"]);
          var dt = locale.format(tdt, { selector: "date", datePattern: "MM/dd/yyyy" });

          if (att["status"] == "unassigned") {
            att["label_rtss_program_name"] = "<p style='background-color: #ffb6c1; padding: 2px;'><b>" + att["rtss_program_name"] + "</b> • " + dt + " • " + att["rtss_test_officer"] + " • " + att["surveyor"] + "</p>";
            att["label_project_date"] = "<p style='background-color: #ffb6c1; padding: 2px;'><b>" + dt + "</b> • " + att["rtss_program_name"] + " • " + att["rtss_test_officer"] + " • " + att["surveyor"] + "</p>";
            att["label_rtss_test_officer"] = "<p style='background-color: #ffb6c1; padding: 2px;'><b>" + att["rtss_test_officer"] + "</b> •" + dt + " • " + att["rtss_program_name"] + " • " + att["surveyor"] + "</p>";
            att["label_surveyor"] = "<p style='background-color: #ffb6c1; padding: 2px;'><b>" + att["surveyor"] + "</b> • " + dt + " • " + att["rtss_program_name"] + " • " + att["rtss_test_officer"] + "</p>";
          } else {
            att["label_rtss_program_name"] = "<p style='padding: 2px;'><b>" + att["rtss_program_name"] + "</b> • " + dt + " • " + att["rtss_test_officer"] + " • " + att["surveyor"] + "</p>";
            att["label_project_date"] = "<p style='padding: 2px;'><b>" + dt + "</b> • " + att["rtss_program_name"] + " • " + att["rtss_test_officer"] + " • " + att["surveyor"] + "</p>";
            att["label_rtss_test_officer"] = "<p style='padding: 2px;'><b>" + att["rtss_test_officer"] + "</b> • " + dt + " • " + att["rtss_program_name"] + " • " + att["surveyor"] + "</p>";
            att["label_surveyor"] = "<p style='padding: 2px;'><b>" + att["surveyor"] + "</b> • " + dt + " • " + att["rtss_program_name"] + " •" + att["rtss_test_officer"] + "</p>";
          }

          att["display_rtss_program_name"] = att["rtss_program_name"] + " • " + dt + " • " + att["rtss_test_officer"] + " • " + att["surveyor"];
          att["display_project_date"] = dt + " • " + att["rtss_program_name"] + " • " + att["rtss_test_officer"] + " • " + att["surveyor"];
          att["display_rtss_test_officer"] = att["rtss_test_officer"] + " • " + dt + " • " + att["rtss_program_name"] + " • " + att["surveyor"];
          att["display_surveyor"] = att["surveyor"] + " • " + att["rtss_test_officer"] + " • " + dt + " • " + att["rtss_program_name"];

          featColl.push(att);
        })
      );
      return new Memory({ data: featColl });
    },

    zoomToAssignment: function (id) {
      //show popup
      console.log(id);
      var store = this.cAssignments.get("store");
      var item = store.get(id);
      if (item) {
        this.btnModify.disabled = false;
        this.btnUpload.disabled = false;

        var geom = item.geometry;

        this._selectAssignmentById(id).then(
          lang.hitch(this, function (features, method) {
            if (features.length > 0) {
              this.own(
                on.once(
                  this.map,
                  "extent-change",
                  lang.hitch(this, function (evt) {
                    var popup = this.map.infoWindow;
                    popup.setFeatures(features);
                    popup.show(features[0].geometry);
                  })
                )
              );
              this.map.centerAt(features[0].geometry);
            }
          })
        );
      }
      console.log(id);
    },

    _selectAssignmentById: function (id) {
      var activeAssignmentLayer = null;
      arrayUtil.forEach(
        this.refreshLayers,
        lang.hitch(this, function (layer) {
          if (layer.visible) {
            activeAssignmentLayer = layer;
          }
        })
      );

      if (!activeAssignmentLayer) {
        activeAssignmentLayer = this.refreshLayers[0];
        activeAssignmentLayer.visible = true;
      }
      var query = new Query();
      query.objectIds = [id];
      query.outFields = ["*"];
      query.returnGeometry = true;
      query.outSpatialReference = this.map.spatialReference;

      var def = activeAssignmentLayer.selectFeatures(query, FeatureLayer.SELECTION_NEW);
      return def;
    },

    createNewAssignment: function (evt) {
      this._clearAssignmentSelection();
      this.surveyEditWidget.setCurrentAssignment(null);
      domStyle.set(this.panelMain, "display", "none");
      domStyle.set(this.panelCreate, "display", "block");
    },

    modifyAssignment: function (evt) {
      this._clearAssignmentSelection();
      var assignment = this.cAssignments.get("item");
      if (assignment) {
        this.surveyEditWidget.setCurrentAssignment(assignment["id"]);
        domStyle.set(this.panelMain, "display", "none");
        domStyle.set(this.panelCreate, "display", "block");
      }
    },

    _clearAssignmentSelection: function (evt) {
      arrayUtil.forEach(
        this.refreshLayers,
        lang.hitch(this, function (layer) {
          layer.clearSelection();
        })
      );

      // this.assignmentLayer.clearSelection();
      this.map.infoWindow.hide();
    },

    uploadDocument: function (evt) {
      var assignment = this.cAssignments.get("item");
      if (assignment) {
        this.uploadDocGPWidget.setCurrentAssignment(assignment["assignment_uid"]);
        domStyle.set(this.panelMain, "display", "none");
        domStyle.set(this.panelUpload, "display", "block");
      }
    },

    _cancelEdit: function () {
      domStyle.set(this.panelCreate, "display", "none");
      domStyle.set(this.panelUpload, "display", "none");
      domStyle.set(this.panelMain, "display", "block");
    },
  });
});
