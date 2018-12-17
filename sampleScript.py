# I am assuming that a sample that "maximizes precision of subsequent testing" per instructions will be one that represents
# the larger population. Therefore I am using stratified sampling to make sure that the distribution of sensors by type in the 
# larger and smaller sample files will be the same. I calculate the appropriate strata sizes so I can partition the data, then I take
# random samples so the proportions of the sensor types will be consistent. 

# I also run a chi square test in case the distributions are not the same (it would be impressive if not but maybe some error could happen)
# Finally I present a bar chart comparing the two samples and showing the distribution of sensors by type for both samples. 

# load relevant libraries
# note that for a regular analysis I would probably use pandas but since this is 
# an exercise and an application I am not using pandas. 
import sys
import os
import helperFunctions as hf

# take the input path from stdin
infile = os.path.abspath(sys.argv[1])

argss=len(sys.argv)

if argss>2:
	outputfile = os.path.abspath(sys.argv[2])
else:
	outputfile="outsample.csv"	

nsensors,sensorTypes=hf.getSensorTypesAndTotal(infile)

strataSizes,nsensorsu=hf.splitCsvAndGetCounts(infile,outputfile,sensorTypes)

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

ctable,pval=hf.checkOutputSample(outputfile,sensorTypes,strataSizes)		

hf.makeSampleChart(ctable,pval)

