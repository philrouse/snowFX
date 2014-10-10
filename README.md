Written by Philip Rouse 2014

snowFX

======

To use the script, follow the installation instructions below and launch the GUI. From here the user 
can create spirals or generate particle effects from the relevant tabs. When generating particle 
effects, the user should adjust the variables to their preference, more details for the variables can be 
found in the included documentation. If using a source curve or plane, the user can select the object 
in the viewport and click the ‘set selected’ button to automatically fill in the object name. Clicking 
the ‘Generate’ button will call the relevant procedure with the user defined variables to create the 
particle animation. The script will also ask to save the scene before starting.

NOTE: If generating over 100 snowflakes or 500 shards or in a very large scene, this can take a very long time. However, 
making a new scene or closing and reopening Maya can yield faster results.

Example videos of the different snowflake effects can be found at https://vimeo.com/album/3078690

Installation Instructions:

Copy the contents of the /icons and /scripts folders to your maya prefs folders (/prefs/icons and 
/prefs/scripts)

run:

>>>import snowflakeGUI

>>>reload(snowflakeGUI)

in the maya script editor or save it to your shelf
