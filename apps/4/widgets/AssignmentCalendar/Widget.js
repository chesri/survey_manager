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
define(["dojo/_base/declare", "dojo/on", "dojo/_base/lang", "dojo/date/locale", "jimu/BaseWidget", "esri/tasks/QueryTask", "esri/tasks/query", "./node_modules/fullcalendar/main"], function (declare, on, lang, locale, BaseWidget, QueryTask, Query, _) {
  //To create a widget, you need to derive from BaseWidget.
  return declare([BaseWidget], {
    baseClass: "assignment-calendar",

    postCreate: function () {
      this.inherited(arguments);
    },

    getColorCode: function () {
      const randomColor = "#" + Math.floor(Math.random() * 16777215).toString(16);
      return randomColor;
    },

    startup: function () {
      this.inherited(arguments);
      var panel = this.getPanel();
      var pos = panel.position;
      pos.width = 600;
      pos.height = 600;
      panel.setPosition(pos);
      panel.panelManager.normalizePanel(panel);

      var calendarEl = document.getElementById("calendar");

      // var queryTask = new QueryTask(`${this.config.surveyMapService}/${this.config.surveyLayerId}`);
      var queryTask = new QueryTask(this.config.assignmentsUrl);
      var query = new Query();
      query.outFields = ["*"];
      query.returnGeometry = false;
      query.where = `1=1`;
      queryTask.execute(
        query,
        lang.hitch(this, function (results) {
          if (results && results.features.length > 0) {
            const assignments = results.features.filter((feature) => {
              return feature.attributes[this.config.fields.surveyor] !== "" && feature.attributes[this.config.fields.surveyor] !== null;
            });

            const surveyorColors = Object.fromEntries(
              assignments.map((feature) => {
                return [feature.attributes[this.config.fields.surveyor].toLowerCase(), this.getColorCode()];
              })
            );

            const calendarObj = {
              initialView: "dayGridMonth",
              initialDate: new Date(),
              headerToolbar: {
                left: "prev,next today",
                center: "title",
                right: "dayGridMonth,timeGridWeek,timeGridDay",
              },
              events: [],
              selectable: true,
              editable: false,
              eventClick: lang.hitch(this, function (info) {
                var eventObj = info.event;
                const selectedRecord = eventObj.extendedProps.record;

                var assignedDate = locale.format(new Date(selectedRecord[this.config.fields.assignedDate]), { selector: "date", datePattern: "MM/dd/yyyy" });
                var projectDate = locale.format(new Date(selectedRecord[this.config.fields.projectDate]), { selector: "date", datePattern: "MM/dd/yyyy" });
                this.surveyorValue.innerHTML = selectedRecord[this.config.fields.surveyor];
                this.assignedDateValue.innerHTML = assignedDate;
                this.projectDateValue.innerHTML = projectDate;
                this.statusValue.innerHTML = selectedRecord[this.config.fields.status];
                this.locationValue.innerHTML = selectedRecord[this.config.fields.location];
                this.locationNotesValue.innerHTML = selectedRecord[this.config.fields.locationNotes];
                this.programNameValue.innerHTML = selectedRecord[this.config.fields.programName];
                this.testOfficerValue.innerHTML = selectedRecord[this.config.fields.testOfficer];
                this.testOfficerPhoneValue.innerHTML = selectedRecord[this.config.fields.testOfficerPhone];
                this.adssValue.innerHTML = selectedRecord[this.config.fields.adss];
                this.wbsValue.innerHTML = selectedRecord[this.config.fields.wbs];
              }),
            };

            for (var i = 0; i < assignments.length; i++) {
              calendarObj.events.push({
                title: assignments[i].attributes[this.config.fields.surveyor],
                start: assignments[i].attributes[this.config.fields.surveyBegin],
                end: assignments[i].attributes[this.config.fields.surveyEnd],
                color: surveyorColors[assignments[i].attributes[this.config.fields.surveyor].toLowerCase()],
                record: assignments[i].attributes,
              });
            }

            var calendar = new window.FullCalendar.Calendar(calendarEl, calendarObj);

            calendar.render();
          }
        })
      );
    },
  });
});
