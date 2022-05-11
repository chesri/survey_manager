define([
  "dijit/_WidgetBase",
  "dijit/_WidgetsInTemplateMixin",
  "dojo/_base/declare",
  "dojo/sniff",
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
  "esri/tasks/Geoprocessor",
  "esri/tasks/DataFile",
  "esri/request",
  "esri/tasks/ProjectParameters",
  "dijit/_TemplatedMixin",
  "dojo/text!./UploadDocGP.html",
  "dojo/dom-class",
  "dojo/dom-style",
], function (
  _WidgetBase,
  _WidgetsInTemplateMixin,
  declare,
  has,
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
  Geoprocessor,
  DataFile,
  esriRequest,
  ProjectParameters,
  _TemplatedMixin,
  template,
  domClass,
  domStyle
) {
  return declare([_WidgetBase, _TemplatedMixin, _WidgetsInTemplateMixin], {
    templateString: template,
    assignmentId: 0,
    uploadUrl: "",
    gpsToolUrl: "",
    tsToolUrl: "",

    constructor: function (options) {
      this.uploadUrl = options.uploadUrl || null;
      this.gpsToolUrl = options.gpsToolUrl || null;
      this.tsToolUrl = options.tsToolUrl || null;
    },

    postMixInProperties: function () {
      this.inherited(arguments);
    },

    startup: function () {
      this.inherited(arguments);
      this.uploadFileInput.addEventListener("change", lang.hitch(this, this.uploadPackageFile), false);
      console.log("added listener");
      this.gpUploadDocumentGPS = new Geoprocessor(this.gpsToolUrl);
      this.gpUploadDocumentTS = new Geoprocessor(this.tsToolUrl);
    },

    backToMainPanel: function () {
      // this.msg.innerHTML = "";
      this._clearMessages();
      this.emit("cancelupload", null);
    },

    _clearMessages: function () {
      var i;
      for (i = this.toolMsgList.options.length - 1; i >= 0; i--) {
        this.toolMsgList.remove(i);
      }
    },

    setCurrentAssignment: function (id) {
      console.log(id);
      this._clearMessages();
      // this.btnSubmit.disabled = true;
      //todo update colors in drop down list if status changes from unassigned
      if (id) {
        this.assignmentId = id;
      } else {
      }
    },

    browseUploadPackage: function (event) {
      console.log("clicked upload button");
      var fileInputCtrl = this.uploadFileInput;
      fileInputCtrl.click();
    },

    _addMsgToToolResultList: function (msg) {
      var opt;
      opt = domConstruct.create("option", { innerHTML: msg, value: this.toolMsgList.options.length });
      this.toolMsgList.append(opt);
    },

    uploadPackageFile: function (event) {
      if (!this.uploadFileInput.value) return;
      console.log("picked file", event);
      domStyle.set(this.toolMsgPanel, "display", "block");

      this._addMsgToToolResultList("Preparing to upload document.");
      // this.toolMsgList
      // domStyle.set(this.loadingPanel, "display", "block");
      var uploadUrl = this.uploadUrl;
      var r;
      var args;

      args = {
        url: uploadUrl,
        content: {
          f: "json",
        },
        form: this.uploadFileContainer,
        handleAs: "json",
        load: lang.hitch(this, this.uploadDidFinish),
        error: lang.hitch(this, this.uploadDidFail),
      };

      r = esriRequest(args);
      return false;
    },

    uploadDidFinish: function (response) {
      // this.msgBox.innerHTML = "Preparing to upload file";
      this.uploadFileInput.value = null;
      var uploadedFile = new DataFile();

      if (response.success) {
        // this.btnSubmit.disabled = false;
        // this.msg.innerHTML = "The document was uploaded successfully. Click Submit to process the file.";
        this._addMsgToToolResultList("The document was uploaded successfully.");

        var gpTask = this._getTaskByFileType(response.item.itemName);

        uploadedFile.itemID = response.item.itemID;

        this.messageCount = 0;

        if (gpTask) {
          this._addMsgToToolResultList("Preparing to run tool to process the document.");
          if (gpTask == "gps") {
            var gpParam = {
              GPS_File: uploadedFile,
              Assignment_ID: this.assignmentId,
            };
            this.gpUploadDocumentGPS.submitJob(gpParam, lang.hitch(this, this._handleGeoprocessingSuccessGPS), lang.hitch(this, this._handleGeoprocessingStatus), lang.hitch(this, this._handleGeoprocessingError));
          } else {
            var gpParam = {
              Total_Station_File: uploadedFile,
              Assignment_ID: this.assignmentId,
            };
            this.gpUploadDocumentTS.submitJob(gpParam, lang.hitch(this, this._handleGeoprocessingSuccessTS), lang.hitch(this, this._handleGeoprocessingStatus), lang.hitch(this, this._handleGeoprocessingError));
          }

          console.log("Upload Successful");
        }

        //add processing button
        // this.gpUploadDocument.submitJob(param, lang.hitch(this, this._handleGeoprocessingSuccess), this._handleGeoprocessingStatus, this._handleGeoprocessingError);
        // console.log("Upload Successful");
      }
    },

    _getTaskByFileType: function (fileName) {
      var ext = fileName.split(".").pop();
      ext = ext.toUpperCase();
      if (ext == "XLS" || ext == "XLSX") {
        return "gps";
      } else if (ext == "TXT" || ext == "ASC") {
        return "total_station";
      }

      return null;
    },

    _handleGeoprocessingStatus: function (jobInfo) {
      if (jobInfo.messages.length > this.messageCount) {
        this._parseNewStatusMessages(jobInfo.messages, this.messageCount);
        // this._addMsgToToolResultList(jobInfo.jobStatus);
        this.messageCount = jobInfo.messages.length;
      }

      console.log(jobInfo);
      console.log("status", jobInfo.jobStatus);
    },

    _parseNewStatusMessages: function (messages, cnt) {
      for (var i = cnt; i < messages.length; i++) {
        this._addMsgToToolResultList(messages[i].description);
      }
    },

    _handleGeoprocessingSuccessGPS: function (response) {
      // this.checkImage(this.config.photoUrl + "/" + this.facilityNo + ".jpg");
      // domStyle.set(this.loadingPanel, "display", "none");
      console.log(response);
      if (response.jobStatus == "esriJobFailed") {
        this._addMsgToToolResultList("There was an error processing the document.");
      } else {
        this._addMsgToToolResultList("The tool completed successfully.");
        var jobId = response["jobId"];

        this.gpUploadDocumentGPS.getResultData(
          jobId,
          "result_polygon",
          lang.hitch(this, function (result) {
            console.log(result);
            if (result.dataType == "GPFeatureRecordSetLayer") {
              if (result.value.features.length > 0) {
                //get first result and zoom to it
                var feat = result.value.features[0];
                this._projectFeature(feat.geometry.getExtent(), this.map.spatialReference).then(
                  lang.hitch(this, function (projExt) {
                    this.map.setExtent(projExt.expand(4));
                  })
                );
                // var ext = feat.geometry.getExtent();
                // this.map.setExtent(ext);
              }
            }
          }),
          function (err) {}
        );

        console.log("success");
      }

      console.log(response);
    },

    _handleGeoprocessingSuccessTS: function (response) {
      // this.checkImage(this.config.photoUrl + "/" + this.facilityNo + ".jpg");
      // domStyle.set(this.loadingPanel, "display", "none");

      if (response.jobStatus == "esriJobFailed") {
        this._addMsgToToolResultList("There was an error processing the document.");
      } else {
        this._addMsgToToolResultList("The tool completed successfully.");

        var jobId = response["jobId"];

        this.gpUploadDocumentTS.getResultData(
          jobId,
          "output_feature_set",
          lang.hitch(this, function (result) {
            console.log(result);
            if (result.dataType == "GPFeatureRecordSetLayer") {
              if (result.value.features.length > 0) {
                //get first result and zoom to it
                var feat = result.value.features[0];
                this._projectFeature(feat.geometry.getExtent(), this.map.spatialReference).then(
                  lang.hitch(this, function (projExt) {
                    this.map.setExtent(projExt.expand(4));
                  })
                );
              }
            }
          }),
          function (err) {}
        );
        console.log("success");
      }

      console.log(response);
    },

    _handleGeoprocessingError: function (err) {
      // domStyle.set(this.loadingPanel, "display", "none");
      this._addMsgToToolResultList("There was an error calling the tool.");
      console.log("failure");
      console.log(err);
    },

    uploadDidFail: function (b) {
      // domStyle.set(this.loadingPanel, "display", "none");
      this._addMsgToToolResultList("The document did not upload successfully.");
      console.log("Upload Fail");
      console.log(b);
    },

    _projectFeature: function (geometry, spatialRef) {
      var def = new Deferred();
      var parameter = new ProjectParameters();
      parameter.geometries = [geometry];
      parameter.outSR = spatialRef;

      esriConfig.defaults.geometryService.project(
        parameter,
        lang.hitch(this, function (geometries) {
          if (!this.domNode) {
            return;
          }
          if (geometries && geometries.length) {
            def.resolve(geometries[0]);
          } else {
            def.reject(new Error("EditXY:: points were not projected."));
          }
        }),
        lang.hitch(this, function (err) {
          // projection error
          if (!err) {
            err = new Error("EditXY:: point was not projected.");
          }
          def.reject(err);
        })
      );
      return def;
    },
  });
});
