# COASTALME Runner

PyQT5 based extendable Runner for COASTALME and COASTALME FV models

The runner replaces the need for batch files and has the following features:
- Manage a queue of simulations to run (combination of COASTALME/COASTALME FV)
- Uses an extensible "plugin" approach so other processes (executables) can be managed in the same queue
- Manages available computer CPU and GPU resources
- Plugins can define restrictions for licenses, GPUs and CPUs
- Handle COASTALME scenarios and events
  - Add multiple simulations based upon a combination of scenarios and events
  - Secnarios and events are remembered between simulations
- Run multiple simulations at a time dependent upon computer and plugin resources
- Tracks progress of running simulation
- Simulation screen output for running or finished simulations (searchable)
- COASTALME provides graphical output (matplotlib) of simulation volume in and volume out through time
- Change priority of items in the run queue
- Remove items from the run queue
- Kill currently running items in the run queue
- Rerun a previously run simulation from the run queue (right-click)
- Option to save and load a run queue to easily rerun a group of simulations

Setup:
- Launch the application (run main.py)
- Choose settings from the menu.
  - Specify the resources (CPU and GPU)
  - Specify plugin information such as location of executables
  - COASTALME and COASTALME FV configurations should reflect the licenses available to the machine

To run a model:
- Select run type (plugin)
- Identify the folder that contains the simulation files (Base folder)
- Select the simulation file (must be .tcf for COASTALME or .fvc for COASTALME FV)
- Click on the add button
  - For COASTALME simulations a dialog will come up to add scenarios and events (must use ~s?~ and ~e?~) in the simulation filename
- Toggle on the "Run" button

Once the run has been toggled, the simulations in the queue should run in order. Select simulations and use the toolbar buttons to change the priority of the simulations in the run queue. 

To add additional plugins, derive objects from the base classes in "plugin_base" and create a plugin object at the beginning of MainWindow (main.py).

Installation instructions
The COASTALME runner was developed in Python 3.9 but should work in other versions as well. These steps you have python installed.

To install
1. Clone or download the repository using your favorite program or method.
2. Install the dependencies using pip: pip install -r requirements.txt
3. Launch the main.py script

The requirements are here (newer versions of the libraries should also be acceptable):
pyqt5~=5.15.4
numpy~=1.23.3
pandas~=1.5.0
python-dateutil~=2.8.2
seaborn~=0.12.1
qtwidgets~=0.18