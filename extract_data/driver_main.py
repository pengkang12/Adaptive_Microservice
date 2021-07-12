from collections import defaultdict
import os
import sys
import pandas as pd
import container_mapping
import driver_post_processing 

debug = True 

def write_header(data,output_file):
    header = []
    header.append("test_id")
    data_container = data[1]
    with open(output_file, 'w') as f:
        for key in data_container:
            service = data_container[key]
            for attrib in service:
                header.append(key+"_"+attrib)

        line = ",".join(header)
        line += '\n' # add new line
        f.write(line)


def write_to_csv(data,output_file):


    result = []
    result.append(data[0])
    data_container = data[1]
    with open(output_file,'a') as f:
        for key in data_container:
            service = data_container[key]
            for attrib in service:
                result.append(str(service[attrib]))
       
	# otherwise write the row
        line = ",".join(result)
        line += '\n' # add new line
        f.write(line)


def remove_hidden(folderName):
    drop_list = set()
    drop_list.add(".git")
    for item in drop_list:
        if item in folderName :
            return False
    return True


# Set the directory you want to start from

def main(current_dir=""):
    if not current_dir:
        current_dir = os.getcwd()
    else:
        current_dir = os.path.abspath(current_dir)
    
    duration = 120

    output_file = "bigtable.csv"
    output_file = os.path.join(current_dir,output_file)
    mapFile = "container_node_mapping.csv"

    #mapping = read_container_host_mapping(current_dir, mapFile)

    mapping = None

    data = [os.path.join(current_dir, item) for item in os.listdir(current_dir)
        if os.path.isdir(os.path.join(current_dir, item))]
    
    header_written = True
    name_list = []
    if os.path.exists(output_file):
        name_list = pd.read_csv(output_file)['test_id'].tolist()
        header_written = False
 
    dir_list = filter(remove_hidden, data)
    result_list = []
    for sub_dir in dir_list:
        name = sub_dir.split('/')[-1]
        if debug:
            print("driver_post_process.py {} {} {}".format(sub_dir, duration, output_file))
        if name not in name_list:
            if os.path.exists(os.path.abspath(os.path.join(sub_dir, mapFile))):
                mapping = container_mapping.read_container_host_mapping(sub_dir, mapFile)  #TODO: mapFile shall be local for each directory 
                if "iperf" in mapping:
                    del mapping["iperf"] 
                if "iperf1" in mapping:
                    del mapping["iperf1"]
                if "iperf2" in mapping:
                    del mapping["iperf2"]
                if "iperf3" in mapping:
                    del mapping["iperf3"]
                if "iperf4" in mapping:
                    del mapping["iperf4"]
                if "stream" in mapping:
                    del mapping["stream"]
            result = driver_post_processing.process(sub_dir, duration, mapping)
            result_list.append(result) 
    if header_written==True:
        write_header(result_list[0],output_file)
    for result in result_list:
        write_to_csv(result,output_file)
 

if __name__ == "__main__":
    dir_name = '../training_data/' 
    if len(sys.argv) > 1:
        dir_name = sys.argv[1] 
    main(dir_name)
