### Description

This tool creates a COASTALME project with the following features:

* Creates the COASTALME folder structure
* Generates the empty input files
* Creates a template COASTALME control files (.tcf, .tgc, etc.)
* Saves the settings to the QGIS project and JSON file which can be used by the other COASTALME tools. JSON file allows settings to be copied and shared between users and projects more easily.

Note this tool currently only supports COASTALME Classic / HPC.

### Parameters

1. **Project Name**: The name of the project. This will be used to help name the input files. The name should  avoid spaces and other characters not supported in file paths (e.g. `/\:*?"<>|`).
2. **Project Folder**: The location of the project folder.
3. **COASTALME Executable**: The location of the COASTALME executable.
4. **COASTALME Settings**: Common COASTALME settings that can be configured by the user that will be written to the template control files.
5. **Domain Setup**: Setup the model domain that will be written to the template control files.
6. **Output Formats**: Setup the output formats that will be written to the template control files.
7. **Create Empty Files**: If checked, will (re)generate empty files.
8. **Create Folder Structure**: If checked, will create the COASTALME folder structure. Only creates the folder structure if it does not already exist.
9. **Setup Control File Templates**: If checked, will create a series of template control files that can be used as inputs to COASTALME. Note, the templates are not complete and require further editing by the user before use. The settings and inputs used in the templates are not considered to be final and appropriate for all models, in fact most of them are simply examples and should be treated as such.