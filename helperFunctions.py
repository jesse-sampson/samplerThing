# load relevant libraries
# note that for a regular analysis I would probably use pandas but since this is
# an exercise and an application I am not using pandas.
# also trying to be not too memory-intensive since IRL this would probably be a bigger dataset that needed sampling
import math
import csv
import sys
import os
import random
import tempfile
from collections import defaultdict
from statistics import mean,stdev
from scipy.stats import chi2,chi2_contingency
import numpy as np
import matplotlib.pyplot as plt

# function to loop over input file to get the unique types of sensors and the total count
def getSensorTypesAndTotal(csvIn):
    # handy with syntax handles file cleanup tasks automagically
    with open(csvIn,newline='') as csvfile:
        # take a quick look at first kb of file to see what the format looks like
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        # reset csv iterator to beginning
        csvfile.seek(0)
        # create a new reader to iterator over csv file input
        reader = csv.reader(csvfile,dialect)
        # capture the unique sensor types in a set.
        typeSet = set()
        for idx,row in enumerate(reader):
            if idx > 0:
                typeSet.add(row[1])
    # want to change my set into a list now so it will preserve order
    # returning the index number gives me a rough total count
    typeSet=sorted(typeSet, key=str.lower)
    return idx,typeSet


# now that we know what our partitioning variables are (aka stratifying variables) we can look at our input file again
def splitCsvAndGetCounts(csvIn,filepath,sTypes):
    with open(csvIn,newline='') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        reader = csv.reader(csvfile    ,dialect)
        # open output file for writing and add header
        with open(filepath,'w',newline='') as outfile:
            #define the writer for our output sample
            outwriter=csv.writer(outfile,delimiter=',',quoting=csv.QUOTE_NONE)
            #give our output a header so it's the same format
            outwriter.writerow(['sensorid','sensortype'])

            # create an empty set for deduplicating. there were no dupes in the dataset but just in case.
            # we want to only keep records not seen by the iterator yet.
            seen=set()

            # this will hold our output data
            ss={}

            # will hold the total unique count
            countUnq=0

            csvfile.seek(0)
            # count if not a header and not yet seen
            for idx,row in enumerate(reader):
                if str(row) not in seen and idx>0:
                    countUnq+=1
                    seen.add(str(row))

            csvfile.seek(0)

            # loop over sensor types list and count sensors per partition
            sensorTypes=sTypes
            for i in sensorTypes:
                with tempfile.TemporaryFile('r+',newline='') as tf:
                    tmpwriter=csv.writer(tf,delimiter=',',quoting=csv.QUOTE_NONE)
                    csvfile.seek(0)
                    seen=set()
                    typeCount=0
                    # increment count of type/strata if a match, not header and not duplicated.
                    # write to temporary file so we can sample it.
                    for idx,row in enumerate(reader):
                        if row[1]==i and str(row) not in seen and idx>0:
                            typeCount+=1
                            seen.add(str(row))
                            tmpwriter.writerow(row)
                    # update output variable with count
                    ss[i]=typeCount
                    # randomly sample (without replacement) the same proportion of types out of 200 as the original sample
                    sampleRows=set(random.sample(range(typeCount),round(typeCount*(200/countUnq))))
                    tf.seek(0)
                    # iterate over our temp file for the stratum and pull out only the row indices from our sample
                    tfreader = csv.reader(tf,dialect)
                    for idx,row in enumerate(tfreader):
                        if idx in sampleRows:
                            outwriter.writerow(row)
                    # update data container with results of count by stratum
                    ss[i] = [ss[i],round(typeCount*(200/countUnq))]

            # return total unique count to alert on if need be
            nsensorsu=countUnq
    return ss,nsensorsu


# function to create contingency tables for both samples then run a two-sample chi-squared test on them
# the two sample chi-squared test compares the expected values based on a chi-squared distribution with n
# categories (degrees of freedom). the null hypothesis is that the distributions are the same, the alternative is that they are different.
# a high p-value is what we want to see in this case, since it is evidence the variations between the sample are the result of random chance
# (e.g. rounding errors) and the underlying distribution is still preserved in the small sample. I am using a conservative threshold of 0.1 since any deviation is a surprise.
# I pass the output sample I created to this function for testing.
# this is another fidelity check that will ensure the precision of testing per instructions
def checkOutputSample(csvIn,sTypes,stratSizes):
    with open(csvIn,newline='') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        reader = csv.reader(csvfile    ,dialect)
        sampleTableCounts=[]
        ctable=[[] for i in range(2)]
        sensorTypes=sTypes
        strataSizes=stratSizes

        # iterate over the sample file and get the counts per stratum
        for i in sensorTypes:
            typeCount=0
            csvfile.seek(0)
            for idx,row in enumerate(reader):
                if row[1]==i:
                    typeCount+=1
            ctable[0].append(strataSizes[i][0])
            ctable[1].append(typeCount)

        # run the test and get the appropriate values
        stat, p, dof, expected = chi2_contingency(ctable)
        alpha=0.1

        # if the p-value is below our alpha level there might be something wrong, should alert and get another look
        if p<alpha:
            print('ERROR there was a problem with this sample and it no longer fits the expected distribution. please run tool again.')
            sys.exit(1)
        return ctable,p

# per instructions I am making a bar chart to show the team the characteristics of the sample.
# the most salient features are the proportions of the types by sample. They should be nearly identical.
# I also include the raw count of sensors for reference. Finally I report the p-value from the chi-squared test in the corner.
def makeSampleChart(ctable,p,chartoutput):

    # function to get the heights of a bar and put a number on top
    def autolabel(rects,ct):
        for rect in range(len(rects)):
            height = rects[rect].get_height()
            ax.text(rects[rect].get_x() + rects[rect].get_width()/2., 1.05*height,'%d' % ct[rect],ha='center', va='bottom')

    # data to plot
    n_groups = 5

    # get the percentages of the total
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

    # decorate plot and save
    plt.xlabel('Sensor Type')
    plt.ylabel('Percent of Total')
    plt.ylim(top=100)
    plt.title('Comparison of Sensor Type Distributions: Population vs. 200-unit Sample')
    plt.suptitle('Our test shows that we do not reject the null \nhypothesis of identical distributions. \nThe sample is about the same \ndistribution as the population\nbut there are some minute differences\ndue to rounding ' + '(p=' + str(p)[:5] + ').',y=0.90,x=0.15,size='x-small',ha='left')
    plt.xticks(index + bar_width, ('Type1', 'Type2', 'Type3', 'Type4','Type5'))
    plt.legend()

    plt.tight_layout()
    plt.savefig(chartoutput)
