## SampleThing

This has been for an exercise submission. The project goal is to take a representative sample of a larger csv file of a given format and produce a sample and chart. 

My approach is to use stratified sampling https://en.wikipedia.org/wiki/Stratified_sampling and layer in a two-sample chi-squared test https://ned.ipac.caltech.edu/level5/Wall2/Wal4_3.html to provide an extra layer of evidence that the sample represents underlying values. 

## Usage: 

sampleScript.py CSVINPUT [SAMPLE_OUTPUT_PATH] [CHART_OUTPUT_PATH]

* must have functions.py in the same directory.
* can specify optional paths
* limited to 200 sensor types
* must provide .csv in this format 
```
sensorId,sensorType
integer,integer
integer,integer 
...
```

## Requirements:

* Python 3.5+

* math
* csv
* sys
* os
* random
* tempfile
* collections
* statistics
* scipy
* numpy
* matplotlib

```

import pip

def import_or_install(package):
	try:
     __import__(package)
   	except ImportError:
   	pip.main(['install', package]) 

for i in ["math","csv","sys","os","random","tempfile","collections","statistics","scipy","numpy","matplotlib"]:
	import_or_install(i)
```


Any feedback please send to jesse {DOT} sampson {AT} gmail {DOT} com
