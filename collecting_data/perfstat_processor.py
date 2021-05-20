from itertools import islice
import sys
import pandas as pd
import warnings
import os

warnings.filterwarnings("ignore", message="numpy.dtype size changed")


def write_to_csv(dataframe,header,output_file):
    df = pd.DataFrame(dataframe, columns=header)
    df.to_csv(output_file+".csv",index=False)

def clean_up_file(infile):
    outfile = infile.split('.')[0]+".swp"

    with open(infile,'r') as f_in, open(outfile,'w') as f_out:
        for line in f_in:
            if "started" in line:
                pass
            elif not line.strip():
                pass
            else:    
                f_out.write(line)
    os.rename(outfile,infile)

 


def post_process_perfstat(filename):
    clean_up_file(filename)
    df = []
    N = 3

    output_file = filename.split('.temp')[0] #ommitting the temp part of the input file
    hostname = filename.split('/')[-1].split('_')[0]  #hostname
    #print("filename",filename) 
    with open(filename, 'r') as infile:
        while(True):
            lines_gen = list(islice(infile, N))
            #break if end
            if len(lines_gen)==0:
                break
            # debug
            print("_________")
            print(lines_gen)
            # keep reading 3 lines at a time
            record = []
            
            for line in lines_gen:
                try:
                    record.append(line.split(',')[1])
                except:
                    pass
            
            record.append(hostname) 
            print(record)
            df.append(record)
    header=["cycle","instructions","LLC-load-misses","hostname"]
    write_to_csv(df,header,output_file)



if __name__ == "__main__":
    filename = sys.argv[1]
    post_process_perfstat(filename) 
