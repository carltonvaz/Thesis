#@ File    (label = "Input directory", style = "directory") srcFile
#@ File    (label = "Output directory", style = "directory") dstFile
#@ String(value='(WARNING: Files in output folder will be overwritten)', visibility='MESSAGE') message1
#@ String(label='Save output images as', choices={"Jpeg", "PNG"}) saveExt
#@ String  (label = "Only process:", choices={"prefix", "suffix", "containing"}, style="radioButtonHorizontal") containType
#@ String  (label = " ", value = "") containString
#@ String(value='(Leave blank to process all files in folder)', visibility='MESSAGE') message2
#@ String(value='', visibility='MESSAGE') blank_message1
#@ String(value='Please set ComDet parameters', visibility='MESSAGE') message3
#@ Short(label='Approximate Spot Size (px)', value=40) spot_size
#@ Short(label='Intensity Threshold (in SD)', value=40) intensity_thresh

# Adapted from batch processing boiler plate
# ( Script Editor > Templates > ImageJ 1.x > Batch > Process Folder (Python) )

import os
from ij import IJ, ImagePlus
from ij.measure import ResultsTable
import csv
import math

# Input image extension type
ext = ".tif"

# Desired columns from ComDet results table
desiredCols = ["X_(px)", "Y_(px)", "xMin", "yMin", "xMax", "yMax", "NArea", "IntegratedInt"]
intensityCol = "IntegratedInt"

# Batch summary columns
batchCols = ["Image", "Count", "Min IntegratedInt", "Max IntegratedInt", "Mean IntegratedInt", \
            "Variance IntegratedInt", "SD IntegratedInt", "CoV (%) IntegratedInt"]

#Functions
def run_script():
    batchStatistics = []
    srcDir = srcFile.getAbsolutePath()
    dstDir = dstFile.getAbsolutePath()
    for root, directories, filenames in os.walk(srcDir):
        filenames.sort();
        for filename in filenames:
            # Check for file extension (only process tif files)
            if not filename.endswith(ext):
                continue
            if not containString.strip() == "" :
	            # Check for file name pattern
	            if containType == "prefix" and not filename.lower().startswith(containString.lower()):
	                continue
	            if containType == "suffix" and not filename.lower().endswith(containString.lower() + ext):
	                continue
	            if containType == "containing" and containString.lower() not in filename.lower():
	                continue
            batchStatistics.append(process(srcDir, dstDir, root, filename))

    writeBatchStats(dstDir, containString, containType, batchStatistics)

    # Close windows
    try:
        # Close results window
        IJ.selectWindow("Results")
        IJ.run("Close")

        # Close summary window
        IJ.selectWindow("Summary")
        IJ.run("Close")

        # Close log window
        IJ.selectWindow("Log")
        IJ.run("Close")

    except:
        pass

    print "\nBatch complete!"

def process(srcDir, dstDir, currentDir, fileName):
    print "\nProcessing:"

    # Open the image
    print "Opening image file", fileName
    imp = IJ.openImage(os.path.join(currentDir, fileName))
    imp.show()

    # Run ComDet with specified parameters
    print "Running ComDet with " + "Approximate spot size: " + str(spot_size) + ", Intensity threshold: " + str(intensity_thresh)
    IJ.run("Detect Particles",
 			"include ch1a=" + str(spot_size) + " ch1s=" + str(intensity_thresh) + " add=Nothing")

    print "Analyzing data"
	# Process results table
    rs = ResultsTable.getResultsTable()

    # Find intensity of 4th brightest spot
    intensityColIndex = rs.getColumnIndex(intensityCol)
    intensities = sorted(rs.getColumnAsDoubles(intensityColIndex), reverse=True)
    markerIntensityThresh = intensities[3]


    # Calculate min, max, mean for all spots except those classified as markers
    # (can have more than 4 markers in case of ties)
    N = 0
    mean = 0
    minimum = float('Inf')
    maximum = -minimum
    for intensity in intensities:
        if intensity < markerIntensityThresh:
            mean += intensity
            N += 1
            minimum = min(minimum, intensity)
            maximum = max(maximum, intensity)

    mean = mean/N

    # Calculate variance, SD, CoV for all spots except those classified as markers
    # (can have more than 4 markers in case of ties)
    var = 0
    for intensity in intensities:
        if intensity < markerIntensityThresh:
            var += (intensity - mean)**2

    var = var/(N - 1)
    sd = math.sqrt(var)
    CoV = (sd/mean)*100   # coefficient of variation

    stats = [fileName.replace(ext, ""), str(N), str(minimum), str(maximum), str(mean), str(var), str(sd), str(CoV)]

    print "Count: ", str(N), ", Min: ", str(minimum), ", Max: ", str(maximum), ", Mean: ", str(mean), ", Variance: ", str(var), ", SD: ", str(sd), ", CoV: ", str(CoV)

    # Write results to csv
    csvDir = os.path.join(dstDir, "Intensity Results")
    if not os.path.exists(csvDir):
        os.makedirs(csvDir)

    csvFilename = os.path.join(csvDir, fileName.replace(ext, "") + ".csv")

    with open(csvFilename, 'wb') as csvfile:
        w = csv.writer(csvfile, delimiter=',')

        # Write summary to csv
        w.writerow(["Summary (marker spots excluded from analysis)"])
        w.writerow(["Count", str(N)])
        w.writerow(["Min IntegratedInt", str(minimum)])
        w.writerow(["Max IntegratedInt", str(maximum)])
        w.writerow(["Mean IntegratedInt", str(mean)])
        w.writerow(["Variance IntegratedInt", str(var)])
        w.writerow(["SD IntegratedInt", str(sd)])
        w.writerow(["CoV (%) IntegratedInt", str(CoV)])

        # Blank line
        w.writerow([""])

        # Write data to csv
        desiredCols.append("Marker Spot?")
        w.writerow(desiredCols)

        for row in range(rs.size()):
            line = []
            for col in range(rs.getLastColumn() + 1):
                marker = False
                currColName = rs.getColumnHeading(col)

                if currColName in desiredCols:
            		line.append(rs.getStringValue(col, row))

                if currColName == intensityCol:
                    # Check if spot is a marker spot
                    if rs.getValueAsDouble(col, row) >= markerIntensityThresh:
                        marker = True

            if (marker == True):
                line.append("Yes")
            else:
                line.append("")
            w.writerow(line)


    # Save the image
    saveDir = dstDir
    if not os.path.exists(saveDir):
        os.makedirs(saveDir)
    print "Saving to", saveDir
    IJ.saveAs(imp, saveExt.lower(), os.path.join(saveDir, fileName))

    # Close the image
    imp.close()

    return stats

def writeBatchStats(dstDir, containString, containType, batchStatistics):
    saveDir = dstDir
    if not os.path.exists(saveDir):
        os.makedirs(saveDir)

    # Construct file name
    if not containString.strip() == "" :
        csvFilename = os.path.join(saveDir, "Batch statistics (" + \
                        containType + " " + containString + ").csv")
    else:
        csvFilename = os.path.join(saveDir, "Batch statistics.csv")

    with open(csvFilename, 'wb') as csvfile:
        w = csv.writer(csvfile, delimiter=',')
        w.writerow(batchCols)
        # Write statistics of each file
        for line in batchStatistics:
            w.writerow(line)

# Run script
run_script()
