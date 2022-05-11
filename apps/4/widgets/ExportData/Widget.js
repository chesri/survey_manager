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
  "jimu/BaseWidget",
  "dijit/_WidgetsInTemplateMixin",
  "dojo/on",
  "dojo/_base/lang",
  "dojo/dom-style",
  "esri/tasks/IdentifyTask",
  "esri/tasks/IdentifyParameters",
  "esri/tasks/Geoprocessor",
  "esri/tasks/QueryTask",
  "esri/tasks/query",
  "esri/geometry/Point",
  "dijit/Dialog",
  "dijit/form/Select",
  "dijit/form/TextBox",
  "dijit/form/Button",
  "dojo/domReady!",
], function (declare, BaseWidget, _WidgetsInTemplateMixin, on, lang, domStyle, IdentifyTask, IdentifyParameters, Geoprocessor, QueryTask, Query, Point) {
  return declare([BaseWidget, _WidgetsInTemplateMixin], {
    baseClass: "export-data-widget",
    mapClickHandler: null,
    identifyTask: null,
    identifyParameters: null,
    selectedProject: null,
    possibleProjects: [],

    postCreate: function () {
      this.inherited(arguments);
    },

    startup: function () {
      this.inherited(arguments);
      // This will be used when selecting features on the map for the project ID
      this.identifyTask = new IdentifyTask(this.config.surveyMapService);
      this.identifyParameters = new IdentifyParameters();
      this.identifyParameters.tolerance = 10;
      this.identifyParameters.returnGeometry = true;
      this.identifyParameters.layerIds = [this.config.surveyLayerId];
      this.identifyParameters.layerOption = IdentifyParameters.LAYER_OPTION_ALL;
      this.identifyParameters.width = this.map.width;
      this.identifyParameters.height = this.map.height;
    },

    onOpen: function () {
      this.activateMapClick();
    },

    onClose: function () {
      this.deactivateMapClick();
    },

    // When the map is clicked, find the project(s) at that click
    findProjects: function (event) {
      this.map.graphics.clear();
      this.identifyParameters.geometry = event.mapPoint;
      this.identifyParameters.mapExtent = this.map.extent;
      this.identifyTask.execute(
        this.identifyParameters,
        lang.hitch(this, function (idResults) {
          if (idResults && idResults.length === 1) {
            // If only one feature is found, populate the project ID field with the selected feature
            this.projectIdInput.set("value", idResults[0].feature.attributes[this.config.surveyIdField]);
            this.selectedProject = idResults[0].feature;
          } else if (idResults && idResults.length > 1) {
            // If more than one feature is found, display a pop-up prompting for which project they want to use
            // First clear out the select, and the options
            while (this.surveySelect.options.length > 0) {
              this.surveySelect.removeOption(0);
            }
            this.possibleProjects = [];

            // Next loop thru the results and add them to the select
            for (let i = 0; i < idResults.length; i++) {
              let siteOption = {
                label: idResults[i].feature.attributes[this.config.filterSurveysByField],
                value: idResults[i].feature.attributes[this.config.surveyIdField],
              };
              this.surveySelect.addOption(siteOption);
              this.possibleProjects.push(idResults[i].feature);
            }
            this.selectProjectDialog.show();
          } else {
            this.noProjectDialog.show();
          }
        })
      );
    },

    // Set the project ID field to the one selected in the multiple features found dropdown.
    projectSelected: function () {
      this.projectIdInput.set("value", this.surveySelect.get("value"));
      for (let i = 0; i < this.possibleProjects.length; i++) {
        if (this.possibleProjects[i].attributes[this.config.surveyIdField] === this.surveySelect.get("value")) {
          this.selectedProject = this.possibleProjects[i];
        }
      }
    },

    // Enable the map to be selectable in order to select a project
    activateMapClick: function () {
      this.map.setInfoWindowOnClick(false);
      this.map.setMapCursor("crosshair");

      if (!this.mapClickHandler) this.mapClickHandler = on.pausable(this.map, "click", lang.hitch(this, this.findProjects));
      else this.mapClickHandler.resume();
    },

    // Disable map selection
    deactivateMapClick: function () {
      this.map.setInfoWindowOnClick(true);
      if (this.mapClickHandler) {
        this.mapClickHandler.pause();
        this.mapClickHandler = null;
      }
      this.map.setMapCursor("default");
    },

    callWriteSurveyGP: function (extent, projectId) {
      let params = { survey_id: projectId };
      let gp = new Geoprocessor(this.config.writeSurveyDataToExcelUrl);
      gp.submitJob(
        params,
        lang.hitch(this, function (result) {
          if (result) {
            gp.getResultData(
              result.jobId,
              "output_excel",
              lang.hitch(this, function (outputResult) {
                if (outputResult) {
                  const link = document.createElement("a");
                  const url = outputResult.value.url;
                  const filename = url.substring(url.lastIndexOf("/") + 1);
                  link.href = url;
                  link.setAttribute("download", filename);
                  document.body.appendChild(link);
                  domStyle.set(this.processingPanel, "display", "none");
                  this.activateMapClick();
                  link.click();
                }
              })
            );
          }
        })
      );
    },

    submitExport: function () {
      domStyle.set(this.processingPanel, "display", "flex");
      let projectIdValue = this.projectIdInput.get("value");

      // If the selected project is set, then the project was entered by clicking on the map.
      if (this.selectedProject) {
        this.deactivateMapClick();
        this.callWriteSurveyGP(this.selectedProject.geometry.getExtent(), projectIdValue);

        // If the project ID was entered manually, and not selected on the map, query for the extent of the project
      } else if (!this.selectedProject && projectIdValue) {
        var queryTask = new QueryTask(`${this.config.surveyMapService}/${this.config.surveyLayerId}`);
        var query = new Query();
        query.outFields = ["*"];
        query.returnGeometry = true;
        query.outSpatialReference = this.map.spatialReference;
        query.where = `${this.config.surveyIdField} = ${projectIdValue}`;
        queryTask.execute(
          query,
          lang.hitch(this, function (results) {
            if (results && results.features.length > 0) {
              this.callWriteSurveyGP(results.features[0].geometry.getExtent(), projectIdValue);
            }
          })
        );
        // If no project was entered, show a dialog that this is a required field.
      } else {
        this.requiredFieldsDialog.show();
      }
    },
  });
});
