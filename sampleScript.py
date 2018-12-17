# I am assuming that a sample that "maximizes precision of subsequent testing" per instructions will be one that represents
# the larger population. Therefore I am using stratified sampling to make sure that the distribution of sensors by type in the 
# larger and smaller sample files will be the same. I calculate the appropriate strata sizes so I can partition the data, then I take
# random samples so the proportions of the sensor types will be consistent. 

# I also run a chi square test in case the distributions are not the same (it would catch subtle input errors or other issues)
# Finally I present a bar chart comparing the two samples and showing the distribution of sensors by type for both samples. 

# import some helper libraries
import sys
import os
import re

# helperFunctions.py has the workhorse functions, importing here
import helperFunctions as hf

# take the input path from stdin
try:
	infile = os.path.abspath(sys.argv[1])
except: 
	print("ERROR: Usage: sampleScript.py CSVINPUT [SAMPLE_OUTPUT_PATH] [CHART_OUTPUT_PATH]")

# also checking for help flags and putting a usage helper in there if a help flag is applied.
helps=set(["-help", "--help" ,"-h", "--h"])
for i in sys.argv:
	if i in helps:
		print("Usage: sampleScript.py CSVINPUT [SAMPLE_OUTPUT_PATH] [CHART_OUTPUT_PATH]")
		exit(1)

# getting other possible inputs, output paths
argss=len(sys.argv)
if argss>2:
	outputfile = os.path.abspath(sys.argv[2])
else:
	outputfile="outsample.csv"	
if argss>3:
	chartoutput = os.path.abspath(sys.argv[3])
else:
	chartoutput="sample_output.png"

# finally to sanitize inputs failing if too many args are passed and they are not help
if argss>4:
	print("ERROR: Usage: sampleScript.py CSVINPUT [SAMPLE_OUTPUT_PATH] [CHART_OUTPUT_PATH]")
	sys.exit(1)

# get the total number sensors and the unique types. This is necessary to construct the strata and also calculate how many 
# sensors are needed in each stratum. We take the proportion of the stratum and scale to the sample size. 
nsensors,sensorTypes=hf.getSensorTypesAndTotal(infile)

# here we get unique sensors by stratum. we use the list of sensorTypes derived in the last function to calculate the strata. we can 
# also use this to alert if there are any duplicate sensor ids within a type.
strataSizes,nsensorsu=hf.splitCsvAndGetCounts(infile,outputfile,sensorTypes)

# comparing the row count to the sum of the unique count of sensor types per stratum 
# the script ignores duplicates.
if nsensors>nsensorsu:
	nsensors=nsensorsu
	print("looks like there are some duplicate sensors in the file, these will be ignored.")

# per instructions, if there are only 200 or fewer sensors in the file they will all be sampled.
if nsensors <= 200:
	print("Alert! Only 200 sensors were in the input file so only 200 sensors are in the sample. Hope this is ok.")

# Per instructions, if there are over 200 types of sensors in the file, alert and quit.
if len(strataSizes.keys()) > 200: 
	print("ERROR: You have more than the maximum supported 200 sensor types in this input file, please reduce to 200 or fewer.")
	sys.exit(1)

# check the output sample for fidelity to the original using a chi-squared test
ctable,pval=hf.checkOutputSample(outputfile,sensorTypes,strataSizes)		

# produce a bar chart with a note about the test results, showing the proportion of sensor types in both the original and new samples. 
# also shows count of sensors in addition to proportion. The proportions are very close. 
hf.makeSampleChart(ctable,pval,chartoutput)

print("your sample file is at " + str(outputfile) + " and your Chart is at " + str(chartoutput))