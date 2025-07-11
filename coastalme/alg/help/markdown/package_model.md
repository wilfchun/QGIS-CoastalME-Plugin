### Description

Interface to COASTALME's package model functionality.

### Parameters

For more information please see the package model documentation in the COASTALME Manual or the COASTALME Wiki:

[Package Model QGIS Tool Wiki](https://wiki.coastalme.com/Package_Model_in_QGIS)
[COASTALME Manual](https://downloads.coastalme.com/_archive/COASTALME/Releases/2018-03/COASTALME%20Manual.2018-03.pdf#page=478)
[Package Model COASTALME Wiki](https://wiki.coastalme.com/Run_COASTALME_From_a_Batch-file#Package_a_COASTALME_model)

* **COASTALME exe**: Path to COASTALME executable used to package model.
* **TCF**: Path to the COASTALME control file.
* **XF Files**: How to treat input files that generate xf files. Options are:
  * **Do not copy xf files**: Do not copy xf files
  * **Copy all**: Copy both raw inputs and xf files
  * **Copy only xf files**: Only copy xf files (if they exist) and do not copy raw inputs
* **Copy All File Extensions**: Copies all files with the same name ignoring file extensions
* **List Files Only**: If checked, will only list the files that would be copied (but does not copy them)
* **Output Directory**: Output directory for the copied files
* **Zip Output**: If checked, will zip the output directory
* **Base Directory**: Base directory of the COASTALME model
* **Scenarios**: List of scenarios in the form of `s[n] == [scenario-name] | ...`. Required to copy input files that contain scenario wildcards in their names.
* **Events**: List of events in the form of `e[n] == [event-name] | ...`. Required to copy input files that contain event wildcards in their names.
