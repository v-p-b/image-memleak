import csv
import sys
import statistics

series={}
stats={}

class STDevDetect:
    def __init__(self,multi=1.0):
        self.multi=multi

    def detect(self,value,mean,stdev):
        if value>mean+(stdev*self.multi) or value<mean-(stdev*self.multi):
            return True
        return False

    def __str__(self):
        return "STDevDetect with x%f multiplier" % (self.multi)

class AboveDetect:
    def __init__(self,limit):
        self.limit=limit

    def detect(self,value,mean,stdev):
        if value>self.limit:
            return True
        return False

    def __str__(self):
        return "AboveDetect with limit=%f" % (self.limit)


DTRS={"RareDotDetector":STDevDetect(0.5),"CompressorDetector":STDevDetect()}
ORACLE_DB=["bad_zlib_checkbits","bad_zlib_method","empty_zlib_object","zlib_invalid_window", "nonconsecutive_idat","bad_zlib_checksum"]

for d,detector in DTRS.items():
    series[d]=[]
    stats[d]={"mean":0.0, "stdev":0.0}
    print("%s - %s" % (d, detector))

with open(sys.argv[1],"r") as csvfile:
    csvreader=csv.DictReader(csvfile,delimiter="\t",quotechar="\"")
    for row in csvreader:
        for d in DTRS:
            series[d].append(float(row[d]))
    for d in DTRS:
        stats[d]["mean"]=statistics.mean(series[d])
        stats[d]["stdev"]=statistics.stdev(series[d])
    print("STATISTICS: %s" % repr(stats))
    csvfile.seek(0)
    csvreader=csv.DictReader(csvfile,delimiter="\t",quotechar="\"")
    for row in csvreader:
        oracle_outlier=False
        for substr in ORACLE_DB:
            if substr in row['Name']:
                oracle_outlier=True
                break

        outlier=False
        row_results=[]
        row_values=[]
        for d, detector in DTRS.items():
            row_results.append(detector.detect(float(row[d]),stats[d]["mean"],stats[d]["stdev"]))
            row_values.append(float(row[d]))
            if row_results[-1]:
                outlier=True
        if outlier and not oracle_outlier:
            print("FP %s %s %s" % (row['Name'],repr(row_results),repr(row_values)))
        if not outlier and oracle_outlier:
            print("FN %s %s %s" % (row['Name'],repr(row_results),repr(row_values)))



    
