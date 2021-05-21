import os
import sys
import glob 
import pandas as pd
import numpy as np 
from collections import defaultdict
import container_mapping

#global vars
debug = True 
inputFile = dict()
inputFile['locust_stats'] = "locust_stats.csv"
inputFile['containercpu'] = "container-cpu5sRaw.csv"
inputFile['containermemW'] = "container-memW5sRaw.csv"
inputFile['containermemR'] = "container-memR5sRaw.csv"
inputFile['containernetW'] = "container-netW5sRaw.csv"
inputFile['containernetR'] = "container-netR5sRaw.csv"
result = dict()
workflow = ["web", "cart", "catalogue", "ratings", "user", "shipping", "payment"] 
 

def get_latency(dir_name):
    count = dict() 
    for name in workflow:
        result[name] = 0
        count[name] = 0
     
    file_name = os.path.join(dir_name, inputFile['locust_stats'])
    if os.path.isfile(file_name):
        df = pd.read_csv(file_name)
    else:
        return 
    
    #print(df)
    #"Name","# requests","50%","66%","75%","80%","90%","95%","98%","99%","100%"
    for index, row in df.iterrows():
        row95 = int(row['95%'])
        request_count = int(row['Request Count'])
        print(row['Name'], int(row95), request_count) 
        if row95 == "N/A":
            pass
        elif '/' == row['Name']:
            result['web'] = row95*request_count
            count['web'] = request_count
        else:
            for name in workflow: 
                if name in row['Name']:
                    if name == 'shipping' and 'confirm' not in row['Name']:
                        continue
                    result[name] += row95*request_count
                    count[name] += request_count
    for key in result.keys():
        result[key] /= count[key]
    return result

'''
TODO:
disabled for the time being. depending on the requirements, may be used.
needs to changed correspoinding to the columns of the inputFile.
'''
def get_perf_data(dir_name,start_pos,end_pos):
    files = [name for name in glob.glob(dir_name+"/*_perfstat.csv")]

    result = dict()

    for file in files:
        df = pd.read_csv(file)
        df = df.loc[start_pos:end_pos+1]
        df = df[df['cycle']!="<not counted>"]
        df = df[df['instructions']!="<not counted>"]
        df = df[df['LLC-load-misses']!="<not counted>"]
        df.cycle = pd.to_numeric(df.cycle, errors='coerce').fillna(0).astype(np.int64)
        df.instructions = pd.to_numeric(df.instructions, errors='coerce').fillna(0).astype(np.int64)
        df['cpi'] = (df['cycle'])/(df['instructions'])
        cpi = (df['cpi'].mean())
        llc = (df['LLC-load-misses'].mean())
        hostname = df.loc[5]['hostname']
        result[hostname] = {'cpi':cpi,'llc':llc,'hostname':hostname}
    
    return result

def get_cpu_vm(dir_name):
    files = [name for name in glob.glob(dir_name+"/*_vmfile.csv")]
    vm_cpu_avg = dict()

    #go over each files
    for file in files:
        with open(os.path.abspath(file), 'r') as f:
            host_name, val = f.readline().split(':')
            val = float(val)
            vm_cpu_avg[host_name] = val
    
    return vm_cpu_avg




def get_cpu_vm_by_node(dir_name):
    #read from kb-w{}{}_vmfile.csv

    files = [name for name in glob.glob(dir_name+"/*_vmfile.csv")]

    #print("[debug]",files)

    vm_cpu_avg = dict()
    vm_cpu_avg['node1'] = 0
    vm_cpu_avg['node2'] = 0
    vm_cpu_avg['node3'] = 0
    vm_cpu_avg['node4'] = 0

    node1 = set(['kb-w11','kb-w12','kb-w13','kb-w14'])
    node2 = set(['kb-w21', 'kb-w22', 'kb-w23', 'kb-w24'])
    node3 = set(['kb-w31', 'kb-w32', 'kb-w33', 'kb-w34'])
    node4 = set(['kb-w41', 'kb-w42', 'kb-w43', 'kb-w44'])

    cntNode1 = 0
    cntNode2 = 0
    cntNode3 = 0
    cntNode4 = 0

    #go over each files
    for file in files:
        with open (os.path.abspath(file),'r') as f:
            host_name, val = f.readline().split(':')
            val = float(val)
            #print("[debug] from file",host_name,val)
            if host_name in node1:
                vm_cpu_avg['node1'] += val
                cntNode1+=1
            elif host_name in node2:
                vm_cpu_avg['node2'] += val
                cntNode2 += 1
            elif host_name in node3:
                vm_cpu_avg['node3'] += val
                cntNode3 += 1
            elif host_name in node4:
                vm_cpu_avg['node4'] += val
                cntNode4 += 1
    #do the average
    #print("[debug] vm util",vm_cpu_avg)
    #print("[debug] count of nodes",cntNode1,cntNode2,cntNode3,cntNode4)

    #print (vm_cpu_avg)
    try:
        vm_cpu_avg['node1'] /= cntNode1*1.0
        vm_cpu_avg['node2'] /= cntNode2*1.0
        vm_cpu_avg['node3'] /= cntNode3*1.0
        vm_cpu_avg['node4'] /= cntNode4*1.0
    
    except:
        pass


    return vm_cpu_avg


# returns the key name (deployment name) of the pod based on pod name
def get_dep_name(depdict, podName):
    for k in depdict.keys():
        if k in podName:
            if debug:
                print("get_dep_name-| Podname: '{}' matches Service: '{}'".format(podName, k)) #debug
            return k
    return None

# returns avg amount of  cpu util (per 5 seconds) (measured in seconds) per pod type
def get_container_metrics(dir_name,start_pos,end_pos, inputFileName, additional=None):
    iresult = {}
    pod_name_list = ['cart', 'catalogue', 'dispatch', 'mongodb', 'mysql', 'payment', 
			'rabbitmq', 'ratings', 'redis', 'shipping', 'user', 'web']
    infer_name_list = ['iperf', 'streaming']
    for pod_name in pod_name_list:
        iresult[pod_name] = []
    for pod_name in infer_name_list:
        iresult[pod_name] = []

    file_name = os.path.join(dir_name,inputFileName)

    if debug:
        print("Collecting avgs for container data file: {}".format(inputFileName))

    if os.path.isfile(file_name):
        with open(file_name) as f:
            for i, line in enumerate(f):
                if i == 0:
                    continue
                data = line.strip("\r\n").split(",")
	
		#filter bad pod data	
                mapping = container_mapping.read_container_host_mapping_2(dir_name)
                service_name = mapping.keys()
                #print(data)
                if data[0] not in service_name:
                    print("pod is not in mapping {0}".format(data[0]))	
               
                pod = get_dep_name(iresult, data[0])
                if pod:
                    iresult[pod].append(get_line_avg(data[1:], start_pos, end_pos, additional))

        #print("iresutl ", iresult) 
	# all avg's collected, create return list    
        ret = {}
        for k, v in iresult.items():
            total = 0
            cnt = 0
            for i, val in enumerate(v):
                if val == "N/A" or val == "nan":
                    continue
                total += float(val)
                cnt += 1

            if total == 0:
                ret[k] = "N/A"
            else:
                # return avg of all pod avgs for specific deployment
                ret[k] =  float(total/cnt)
        
        if debug:
            #print("Service avg vals ret: {}".format(ret))
            pass
        return ret

def get_container_cpu_avg(inputs, start_i, end_i):
    lst = [float(i) for i in inputs[start_i:end_i] if i]
    if len(lst) == 0 or lst[-1] - lst[0] < 0 or lst[-1] - lst[0] > 1000:
        return "N/A"
    return lst[-1] - lst[0]

    prev_val = 0
    diffs = []
    first_entry_cnt = 0
    for i, entry in enumerate(inputs, start_i-1):
        # passed data section, break
        if i >= end_i:
            break
        # if entry is blank, just iterate num entries since last entry
        if entry == '':
            continue
        # if first entry, populate init prev_val & continue
        entry = float(entry)
        if prev_val == 0:
            prev_val = entry
            first_entry_cnt = i
            continue
        else:
            # Incase of error where newer entry is less than prev, data is not valid, return N/A
            if prev_val > entry:
                if debug:
                    print("Error in data for processing a pod.")
                diffs = []
                break

            elapsed = (entry - prev_val)
            prev_val = entry
            last_entry_cnt = i
            diffs.append(elapsed)

    if len(diffs) == 0:
        return "N/A"
    total = 0.0        
    for ind ,i in enumerate(diffs):
        total += i
    if total > 1000:
        return "N/A"
    return total

# inputs is a list of string typed floats
def get_line_avg(inputs, start_i, end_i, additional=None):
    cnt = 0
    count = 0.0
    for i, value in enumerate(inputs):
        if i >= len(inputs) - start_i and value not in ['0', '']:
            count += float(value)
            cnt += 1
    if cnt == 0:
        return 'N/A'
    return count/cnt


def getHorizontalLine():
    l = 80
    result = "-"*l
    return result 


def get_average_vm_utilization(vm_cpu, node_list):

    sumCpu = 0
    count  = 0
    for node in node_list:
        sumCpu += vm_cpu.get(node,0)
        count += 1 if vm_cpu.get(node,0) >0 else 0
    
    if count ==0:
        return 0
    return sumCpu/count

def get_average_vm_net(vm_net, node_list):

    sumCpu = 0
    count  = 0
    for node in node_list:
        sumCpu += float(vm_net.get(node))
        count += 1 if float(vm_net.get(node)) >0 else 0
    if count ==0:
        return 0
    return sumCpu/count



def get_average_perf(perf_data, node_list):

    sumCpi = 0 
    sumLLC = 0
    count = 0

    for node in node_list:
        if node in perf_data.keys():
            sumCpi += perf_data[node]['cpi']
            sumLLC += perf_data[node]['llc']
            count +=1
    
    if count==0:
        return 0
    sumCpi = sumCpi/count
    sumLLC = sumLLC/count
    return [sumCpi,sumLLC]


def get_container_net_metrics(dir_name,start_pos,end_pos, inputFileName, additional=None):
    iresult = {}
    file_name = os.path.join(dir_name,inputFileName)

    if os.path.isfile(file_name):
        with open(file_name) as f:
            for i, line in enumerate(f):
                if i == 0:
                    continue
                data = line.strip("\r\n").split(",")
                iresult[data[0]] = get_line_avg(data[1:], start_pos, end_pos)
        # all avg's collected, create return list    
        return iresult

def get_vm_net(dir_name, container_net):
    mapping = container_mapping.read_container_host_mapping(dir_name) 
    ret = dict() 

    for service_name, node_name in mapping.items():
        if service_name == "NAME":
           continue  
        for node in node_name:
            if node not in ret:
                ret[node] = container_net.get(service_name,0)
            else: 
                ret[node] += container_net.get(service_name,0)
    return ret	



def process(dir_name,start_pos,end_pos,mapping):
    # actual aggregation
    result = {}
    #result['test_id'] = dir_name

    latency = get_latency(dir_name)
    
    vm_cpu = get_cpu_vm(dir_name)
    perf_data =  get_perf_data(dir_name,start_pos,end_pos)
    print("Current dirName is: {}".format(dir_name)) #debug
    container_cpu = get_container_metrics(dir_name, start_pos, end_pos, inputFile["containercpu"], 'cpuavg')
    #container_cpu_inc = get_container_metrics(dir_name, start_pos, end_pos, inputFile["containercpu"])
    container_memW = get_container_metrics(dir_name, start_pos, end_pos, inputFile["containermemW"])
    container_memR = get_container_metrics(dir_name, start_pos, end_pos, inputFile["containermemR"])
    container_netW = get_container_metrics(dir_name, start_pos, end_pos, inputFile["containernetW"], 'netW')
    container_netR = get_container_metrics(dir_name, start_pos, end_pos, inputFile["containernetR"], 'netR')
    
    #collect net's data for virtual machine
    container_net_vm_W = get_container_net_metrics(dir_name,start_pos,end_pos, inputFile["containernetW"])
    vm_netW = get_vm_net(dir_name, container_net_vm_W)
    container_net_vm_R = get_container_net_metrics(dir_name,start_pos,end_pos, inputFile["containernetR"])
    vm_netR = get_vm_net(dir_name, container_net_vm_R)
      
    print("mapping.items debug out:") #debug
    #print(mapping.items()) #debug
    for service_name, node_name in mapping.items():
        if service_name == "NAME":
            continue
        print("service & nodename debug:")
        #print(service_name) #debug
        #print(node_name) #debug
        if service_name not in result.keys():
            result[service_name] = {}
        #print("inside loop debug") #debug
        result[service_name]['vm_util'] = get_average_vm_utilization(vm_cpu,node_name)
        result[service_name]['perf_cpi'] = get_average_perf(perf_data,node_name)[0] #first column cpi
        result[service_name]['perf_llc'] = get_average_perf(perf_data, node_name)[1] #second column llc
     	
        #this is new metric for vm_net 
        result[service_name]['vm_netW'] = get_average_vm_net(vm_netW, node_name)
        result[service_name]['vm_netR'] = get_average_vm_net(vm_netR, node_name)
        
        
        result[service_name]['95th_latency'] = latency.get(service_name,0)
    
    for svc_name, node in mapping.items():
        if svc_name in container_cpu:
            result[svc_name]['cont_cpu5s_avg'] = container_cpu[svc_name]
            print(svc_name, container_cpu[svc_name])
        if svc_name in container_memW:
            result[svc_name]['cont_memW5s_avg'] = container_memW[svc_name]
        if svc_name in container_memR:
            result[svc_name]['cont_memR5s_avg'] = container_memR[svc_name]
        if svc_name in container_netW:
            result[svc_name]['cont_netW5s_avg'] = container_netW[svc_name]
        if svc_name in container_netR:
            result[svc_name]['cont_netR5s_avg'] = container_netR[svc_name]

    print("latency_for_each, ", latency)

    print("\nresult struct:") #debug   
    #print(result) #debug
    test_id = dir_name.split('/')[-1] #last item

    return (test_id, result)

if __name__ == "__main__":

    process(dir_name=sys.argv[1],start_pos=int(sys.argv[2]),end_pos=int(sys.argv[3]),mapping=sys.argv[4])
