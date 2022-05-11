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

define(["dojo/_base/declare", "jimu/BaseWidgetSetting"], function (declare, BaseWidgetSetting) {
  return declare([BaseWidgetSetting], {
    baseClass: "jimu-widget-demo-setting",

    postCreate: function () {
      //the config object is passed in
      this.setConfig(this.config);
    },

    setConfig: function (config) {
      this.surveyIDField.value = config.surveyIdField;
      this.surveyMapService.value = config.surveyMapService;
      this.surveyLayerId.value = config.surveyLayerId;
      this.filterSurveysByField.value = config.filterSurveysByField;
      this.writeSurveyDataToExcelUrl.value = config.writeSurveyDataToExcelUrl;
      this.exportWebMapTaskUrl.value = config.exportWebMapTaskUrl;
    },

    getConfig: function () {
      return {
        surveyIdField: this.surveyIDField.value,
        surveyMapService: this.surveyMapService.value,
        surveyLayerId: this.surveyLayerId.value,
        filterSurveysByField: this.filterSurveysByField.value,
        writeSurveyDataToExcelUrl: this.writeSurveyDataToExcelUrl.value,
        exportWebMapTaskUrl: this.exportWebMapTaskUrl.value,
      };
    },
  });
});
