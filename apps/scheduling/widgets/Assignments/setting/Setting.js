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

define(["dojo/_base/declare", "dojo/_base/lang", "dojo/_base/html", "dojo/sniff", "dojo/query", "dojo/_base/array", "dijit/_WidgetsInTemplateMixin", "jimu/utils", "jimu/BaseWidgetSetting", "dojox/form/CheckedMultiSelect", "dijit/form/TextBox"], function (
  declare,
  lang,
  html,
  has,
  query,
  arrayUtil,
  _WidgetsInTemplateMixin,
  utils,
  BaseWidgetSetting,
  CheckedMultiSelect,
  TextBox
) {
  /*jscs: disable maximumLineLength*/
  return declare([BaseWidgetSetting, _WidgetsInTemplateMixin], {
    //these two properties is defined in the BaseWidget
    baseClass: "jimu-widget-assignments-setting",

    postCreate: function () {
      this.inherited(arguments);
    },

    startup: function () {
      this.inherited(arguments);

      this.assignmentLayerSelect = new CheckedMultiSelect({
        name: "selectLayers",
        multiple: true,
        style: "width:100%;",
      }).placeAt(this.layersContainer);

      this.setConfig(this.config);
    },

    _populateLayerCheckList: function (layers) {
      var opLayers = this.map.itemInfo.itemData.operationalLayers;
      var options = [];

      for (var i = opLayers.length - 1; i >= 0; i--) {
        var filteredArr = arrayUtil.filter(options, function (item) {
          return item.label === opLayers[i].title;
        });
        if (filteredArr === null || filteredArr.length === 0) {
          if (layers.indexOf(opLayers[i].title) > -1) {
            this.assignmentLayerSelect.addOption({
              label: opLayers[i].title,
              value: opLayers[i].title,
              selected: "selected",
            });
          } else {
            this.assignmentLayerSelect.addOption({
              label: opLayers[i].title,
              value: opLayers[i].title,
            });
          }
        }
      }
    },

    setConfig: function (config) {
      this.config = config;

      if (this.config.hasOwnProperty("refreshLayers") && this.config["refreshLayers"].length > 0) {
        this._populateLayerCheckList(this.config["refreshLayers"]);
      } else {
        this._populateLayerCheckList([]);
      }

      if (this.config.hasOwnProperty("assignmentLayer")) {
        this.assignmentLayerUrl.set("value", this.config["assignmentLayer"]);
      }

      if (this.config.hasOwnProperty("siteLayer")) {
        this.siteLayerUrl.set("value", this.config["siteLayer"]);
      }

      if (this.config.hasOwnProperty("geoprocessing")) {
        var geoprocessingObj = this.config["geoprocessing"];
        if (geoprocessingObj.hasOwnProperty("uploadUrl")) {
          this.gpUploadUrl.set("value", geoprocessingObj["uploadUrl"]);
        }
        if (geoprocessingObj.hasOwnProperty("gpsToolUrl")) {
          this.gpToolGPSUrl.set("value", geoprocessingObj["gpsToolUrl"]);
        }
        if (geoprocessingObj.hasOwnProperty("tsToolUrl")) {
          this.gpToolTSUrl.set("value", geoprocessingObj["tsToolUrl"]);
        }
      }
    },

    validateConfig: function () {},

    getConfig: function () {
      var layersArray = [];

      for (i = 0; i < this.assignmentLayerSelect.options.length; i++) {
        var opt = this.assignmentLayerSelect.options[i];
        if (opt.selected) {
          layersArray.push(opt.value);
        }
      }

      this.config["refreshLayers"] = layersArray;
      this.config["assignmentLayer"] = this.assignmentLayerUrl.get("value");
      this.config["siteLayer"] = this.siteLayerUrl.get("value");

      var geoprocessingObj = {};

      geoprocessingObj["uploadUrl"] = this.gpUploadUrl.get("value");
      geoprocessingObj["gpsToolUrl"] = this.gpToolGPSUrl.get("value");
      geoprocessingObj["tsToolUrl"] = this.gpToolTSUrl.get("value");

      this.config["geoprocessing"] = geoprocessingObj;
      return this.config;
    },

    destroy: function () {
      this.inherited(arguments);
    },
  });
});
