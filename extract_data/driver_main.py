from collections import defaultdict
import os
import sys

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
    
    start_pos = 5
    end_pos = 55
    output_file = "bigtable.csv"
    output_file = os.path.join(current_dir,output_file)
    mapFile = "container_node_mapping.csv"

    #mapping = read_container_host_mapping(current_dir, mapFile)



    data = [os.path.join(current_dir, item) for item in os.listdir(current_dir)
        if os.path.isdir(os.path.join(current_dir, item))]
    
    dir_list = filter(remove_hidden, data)
    header_written = False
    for sub_dir in dir_list:
        if debug:
            print("driver_post_process.py {} {} {} {}".format(sub_dir,start_pos,end_pos,output_file))
        if True:
            if os.path.isfile(os.path.abspath(os.path.join(sub_dir, mapFile))):
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
                print(mapping)
            result = driver_post_processing.process(sub_dir, start_pos, end_pos, mapping)
            #print(result)
            if header_written==False:
                write_header(result,output_file)
                header_written=True
            write_to_csv(result,output_file)
        else:
            pass 
        #except Exception as e:
        #    print(e)
            #continue


if __name__ == "__main__":
    dir_name = '../training_data/' 
    if len(sys.argv) > 1:
        dir_name = sys.argv[1] 
    main(dir_name)
