The scripts in the "survey_tools_scripts_5-17-2022" folder are revised versions of the Survey Management Tools. 

Changes in this version include:
1) Removing the f-string functions that is supported in Python 3.7 and above. 
2) Corrected references to survey, survey_point, survey_lines, and station layers.
3) Added code to check the Geodatabase (arcpy.env.workspace) more thoroughly and report when it isn't working as expected. 

To use the tools:
1) Open up each tool and examine for any pathname dependencies and modify those to work for your network.
   gdb_delete_surveys.py - update the Geodatabase connection file path 
   gdb_export_to_excel.py - update the Geodatabase connection file path 
                            update the "printed_map.aprx" file path
                            update the signature_files folder path and add names to dictionaty reference.
   gdb_import_GPS.py - update the Geodatabase connection file path 
   gdb_import_TS.py - update the Geodatabase connection file path 

2) Associate the tools with the appropriate Toolbox.tbx tool references. 
3) Run the tools in ArcGIS Pro, then right-click on the tool history and publish. 
