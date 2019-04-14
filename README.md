# ComDet batch processing

This script was developed to enable batch processing using the ComDet ImageJ plugin (https://imagej.net/Spots_colocalization_(ComDet)) for a specific microarray image dataset as part of an undergraduate thesis.

The script allows the user to process multiple 16 bit TIFF files through a simple user interface:
![User interface](https://github.com/carltonvaz/Thesis/blob/master/github%20images/AnalyzeSpots%20interface.PNG)

# Getting started

## Prerequisites

The script was developed using the Fiji distribution (recommended) of ImageJ (https://fiji.sc/). It should work with other distributions that support ImageJ2, but has not been tested in these environments.

The ComDet plugin needs to be installed and integrated with ImageJ as described here: (https://github.com/ekatrukha/ComDet/wiki/How-to-install-plugin)

## Integrating script with ImageJ

1. Download the AnalyzeSpots_.py file.
2. If you wish to change the name, it's fine as long as you ensure that the file name ends with an underscore ‘_’.
3. Locate the directory where Fiji (or ImageJ) is installed on your machine.
4. Place the ‘AnalyzeSpots_.py’ file in Fiji.app/plugins/Scripts and restart Fiji.
5. To run the script, *Fiji Menu > Plugins > Scripts > AnalyzeSpots*.

See: (https://imagej.net/Scripting#Adding_scripts_to_the_Plugins_menu) for reference
