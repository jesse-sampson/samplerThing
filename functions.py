# function to loop over input file to get the unique types of sensors and the total count
def getSensorTypesAndTotal(csvIn):
	with open(csvIn,newline='') as csvfile:				
		# take a quick look at first kb of file to see what the format looks like
		dialect = csv.Sniffer().sniff(csvfile.read(1024))	
		# reset csv iterator to beginning 
		csvfile.seek(0)
		# create a new reader to iterator over csv file input
		reader = csv.reader(csvfile,dialect)
		typeSet = set()
		for idx,row in enumerate(reader):
			if idx > 0:			
				typeSet.add(row[1])
	typeSet=sorted(typeSet, key=str.lower)
	return idx,typeSet

def splitCsvAndGetCounts(csvIn,filepath):
	with open(csvIn,newline='') as csvfile:				
		dialect = csv.Sniffer().sniff(csvfile.read(1024))			
		reader = csv.reader(csvfile	,dialect)	
		# open output file for writing and add header 
		with open(filepath,"w") as outfile:
			outwriter=csv.writer(outfile,delimiter=",",quoting=csv.QUOTE_NONE)
			outwriter.writerow(['sensorid','sensortype'])
			seen=set()
			ss={}
			countUnq=0						
			csvfile.seek(0)	
			for idx,row in enumerate(reader):
				if str(row) not in seen and idx>0:
					countUnq+=1					
					seen.add(str(row))
			
			csvfile.seek(0)		
			
			for i in sensorTypes:
				with tempfile.TemporaryFile("r+") as tf:
					tmpwriter=csv.writer(tf,delimiter=",",quoting=csv.QUOTE_NONE)																
					csvfile.seek(0)
					seen=set()
					typeCount=0
					for idx,row in enumerate(reader):
						if row[1]==i and str(row) not in seen and idx>0:
							typeCount+=1		
							seen.add(str(row))														
							tmpwriter.writerow(row)					
					ss[i]=typeCount
					sampleRows=set(random.sample(range(typeCount),round(typeCount*(200/countUnq))))
					tf.seek(0)					
					tfreader = csv.reader(tf,dialect)
					for idx,row in enumerate(tfreader):				
						if idx in sampleRows:													
							outwriter.writerow(row)						
					ss[i] = [ss[i],round(typeCount*(200/countUnq))]	

			nsensorsu=countUnq
	return ss,nsensorsu

def checkOutputSample(csvIn):
	with open(csvIn,newline='') as csvfile:				
		dialect = csv.Sniffer().sniff(csvfile.read(1024))			
		csvfile.seek(0)		
		reader = csv.reader(csvfile	,dialect)
		sampleTableCounts=[]
		ctable=[[] for i in range(2)]
		for i in sensorTypes:
			typeCount=0
			csvfile.seek(0)		
			for idx,row in enumerate(reader):	
				if row[1]==i:					
					typeCount+=1
			ctable[0].append(strataSizes[i][0])
			ctable[1].append(typeCount)
		
		chi2stat=0
		alpha=0.1	
		stat, p, dof, expected = chi2_contingency(ctable)				
		if p<alpha:
			print("ERROR there was a problem with this sample and it doesn't fit the expected distribution. please run tool again.")
			sys.exit(1)	
		return ctable,p

def makeSampleChart(ctable,p):
	def autolabel(rects,ct):
		for rect in range(len(rects)):
			height = rects[rect].get_height()
			ax.text(rects[rect].get_x() + rects[rect].get_width()/2., 1.05*height,'%d' % ct[rect],ha='center', va='bottom')

	# data to plot
	n_groups = 5
	totals_pop = [100*(ctable[0][i]/float(sum(ctable[0]))) for i in range(len(ctable[0]))]
	totals_samp = [100*(ctable[1][i]/float(sum(ctable[1]))) for i in range(len(ctable[1]))]

	# create plot
	fig, ax = plt.subplots()
	index = np.arange(n_groups)
	bar_width = 0.35
	opacity = 0.8
	 
	rects1 = plt.bar(index, totals_pop, bar_width,
	                 alpha=opacity,
	                 color='b',
	                 label='All Sensors')
	 
	rects2 = plt.bar(index + bar_width, totals_samp, bar_width,
	                 alpha=opacity,
	                 color='g',
	                 label='Sample Sensors')
	
	autolabel(rects1,ctable[0])
	autolabel(rects2,ctable[1])
	


	plt.xlabel('Sensor Type')
	plt.ylabel('Percent of Total')
	plt.ylim(top=100)
	plt.title('Comparison of Sensor Type Distributions: Population vs. Sample')
	plt.suptitle('Our test shows that we do not reject the null \nhypothesis of identical distributions. \nThe sample is about the same \ndistribution as the population\nbut there are some minute differences\ndue to rounding.' + '(p=' + str(p)[:5] + ').',y=0.90,x=0.15,size='x-small',ha="left")
	plt.xticks(index + bar_width, ('Type1', 'Type2', 'Type3', 'Type4','Type5'))
	plt.legend()
	 
	plt.tight_layout()
	plt.savefig("sample_output.png")		
	