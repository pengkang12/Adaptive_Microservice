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
result2 = dict()
result3 = dict()

workflow = ["web", "cart", "catalogue", "ratings", "user", "shipping", "payment", "other"] 
 
def get_latency(dir_name):
    count = dict() 
    failure_count = dict() 
    latency = dict() 
    for name in workflow:
        result[name] = 'N/A'
        result2[name] = 'N/A'
        result3[name] = 'N/A'
 
        latency[name] = []
        count[name] = []
        failure_count[name] = 0
     
    file_name = os.path.join(dir_name, inputFile['locust_stats'])
    if os.path.isfile(file_name):
        df = pd.read_csv(file_name)
    else:
        return 
    
    #"Name","# requests","50%","66%","75%","80%","90%","95%","98%","99%","100%"
    for index, row in df.iterrows():
        row95 = int(row['95%'])
        fail_count = int(row['Failure Count'])
        request_count = int(row['Request Count'])  - fail_count
        #    continue
        url = row['Name']
        #print(row['Name'], int(row95), request_count) 
        if row95 == "N/A":
            continue
        elif '/' == url:
            work = 'web' 
            latency[work] += [row95]
            count[work] += request_count,
            failure_count[work] += fail_count
        else:
            work = "other"
            if "/api/ratings/api/rate" in url:
            #if "/api/ratings" in url:
                work = 'ratings'
            elif "payment" in url:
                work = 'payment'
            elif "catalogue/products" in url or "catalogue/categories" in url :
            #elif "catalogue" in url:
                work = 'catalogue'
            elif "shipping/confirm" in url:
            #elif "shipping" in url:
                work  = 'shipping'
            elif "cart/add" in url:
                work = 'cart'
            #elif "/api/user/login" in url:
            elif "/api/user/login" in url:
                work = 'user'

            latency[work] += [row95]
            count[work] += request_count,
            failure_count[work] += fail_count
 
    for key in result.keys():
        if key == 'other':
            continue
        if len(count[key]) > 0:
            tmp = [0]
            for c in count[key]:
                tmp += latency[key] * c
           
            result[key] = np.percentile(tmp, 95) 
            if key in ["ratings", "catalogue"]:
                result[key] = np.percentile(tmp, 90) 
 
            result2[key] = sum(count[key])
            result3[key] = failure_count[key]
        else:
            result[key] = 'N/A'
    return result, result2, result3

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
        length = df.shape[0]
        df = df.loc[length-end_pos:length-start_pos+1]
        df = df[df['cycle']!="<not counted>"]
        df = df[df['instructions']!="<not counted>"]
        df = df[df['LLC-load-misses']!="<not counted>"]
        df.cycle = pd.to_numeric(df.cycle, errors='coerce').fillna(0).astype(np.int64)
        df.instructions = pd.to_numeric(df.instructions, errors='coerce').fillna(0).astype(np.int64)
        df['cpi'] = (df['cycle'])/(df['instructions'])
        cpi = (df['cpi'].mean())
        llc = (df['LLC-load-misses'].mean())
        hostname = df.loc[length-end_pos]['hostname']
        result[hostname] = {'cpi':cpi,'llc':llc,'hostname':hostname}
    
    return result

def get_cpu_vm(dir_name, start_pos, end_pos):
    files = [name for name in glob.glob(dir_name+"/*_vmfile.tmp")]
    vm_cpu_avg = dict()

    #go over each files
    for vm_file in files:
        host_name = vm_file.split('/')[-1].split('_')[0]
        with open(vm_file,'r') as f1:
            #field12 for user cpu
            vm_cpu_sum = 0
            count = 0
            vm_cpu = []
            for line in f1:
                #print("debug:{}".format(line))
                if ("procs" in line) or ("swpd" in line):
                    pass
                else:
                    if count>=start_pos and count <= end_pos:
                        vm_cpu_sum += int(line.split()[13])
                        if int(line.split()[13]) > 0:
                            vm_cpu.append(int(line.split()[13]))
                    count += 1
            vm_cpu_avg[host_name] = sum(vm_cpu)*1.0/len(vm_cpu)
    print(vm_cpu_avg, count)
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
                pass
                #print("get_dep_name-| Podname: '{}' matches Service: '{}'".format(podName, k)) #debug
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
                    #print("pod is not in mapping {0}".format(data[0]))	
                    pass
               
                pod = get_dep_name(iresult, data[0])
                if pod:
                    if additional == "cpuavg":
                        iresult[pod].append(get_container_cpu_avg(data[1:], start_pos, end_pos))
                    else:
                         iresult[pod].append(get_line_avg(data[1:], start_pos, end_pos, additional))
 
        #print("iresutl ", iresult) 
	# all avg's collected, create return list    
        ret = {}
        for k, v in iresult.items():
            total = []
            for i, val in enumerate(v):
                if val == "N/A" or val == "nan":
                    continue
                total.append(float(val))

            if len(total) == 0:
                ret[k] = "0"
            else:
                # return avg of all pod avgs for specific deployment
                #if additional == "cpuavg":
                #    ret[k] =  max(total)
                #else:
                ret[k] =  float(sum(total)/len(total))
        if debug:
            #print("Service avg vals ret: {}".format(ret))
            pass
        return ret

def get_line_avg(inputs, start_i, end_i, additional=None):
    last_entry_cnt = 1
    prev_val = 0
    diffs = []
    for i, entry in enumerate(inputs, start_i-1):
        # passed data section, break
        if i >= end_i:
            break
        # if entry is blank, just iterate num entries since last entry
        if entry == '':
            last_entry_cnt += 1
            continue
        # if first entry, populate init prev_val & continue
        entry = float(entry)
        if prev_val == 0:
            prev_val = entry
            last_entry_cnt = 1
            continue
        else:
            # Incase of error where newer entry is less than prev, data is not valid, return N/A
            if prev_val > entry: 
                break
                continue 
            elapsed = abs(entry - prev_val) / last_entry_cnt
            last_entry_cnt = 1
            prev_val = entry
            diffs.append(elapsed)

    if len(diffs) == 0:
        return "N/A"
    total = 0.0        
    for ind ,i in enumerate(diffs):
        total += i
    return total# / len(diffs)
    #return total

def get_container_cpu_avg(inputs, start_i, end_i):
    lst = [float(i) for i in inputs[start_i:end_i] if i not in ['']]
    if len(lst) == 0 or lst[-1] - lst[0] < 0 or lst[-1] - lst[0] > 1000:
        return "N/A"
    new_lst = []
    prev = lst[0]
    for i in range(1, len(lst)):
        if prev < lst[i]:
            new_lst.append(lst[i]-prev)
            prev = lst[i]
            
    if len(new_lst) == 0:
        return "N/A"
    ret = sum(new_lst)#/len(new_lst)
    #print(ret, new_lst, len(inputs))
    return ret

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



def process(dir_name,duration,mapping):
    # actual aggregation
    result = {}
    #result['test_id'] = dir_name

    latency, workload, workload_fail = get_latency(dir_name)

    duration = int(duration) 
    # 30s for grace and try to get stable results

    start_pos, end_pos = 30, 90
    vm_cpu = get_cpu_vm(dir_name, start_pos, end_pos)
    start_pos, end_pos = 10, 23
    perf_data =  get_perf_data(dir_name,start_pos,end_pos)
    print("Current dirName is: {}".format(dir_name)) #debug

    #start_pos, end_pos = 10, 10 + 12 + 1
    start_pos, end_pos = 6, 6+1+18


    print(start_pos, end_pos)
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
        result[service_name]['workload'] = workload.get(service_name,0)
        result[service_name]['workload_fail'] = workload_fail.get(service_name,0)
    
    for svc_name, node in mapping.items():
        if svc_name in container_cpu:
            result[svc_name]['cont_cpu5s_avg'] = container_cpu[svc_name]
            #print(svc_name, container_cpu[svc_name])
        if svc_name in container_memW:
            result[svc_name]['cont_memW5s_avg'] = container_memW[svc_name]
        if svc_name in container_memR:
            result[svc_name]['cont_memR5s_avg'] = container_memR[svc_name]
        if svc_name in container_netW:
            result[svc_name]['cont_netW5s_avg'] = container_netW[svc_name]
        if svc_name in container_netR:
            result[svc_name]['cont_netR5s_avg'] = container_netR[svc_name]

    #print("latency_for_each, ", latency)

    print("\nresult struct:") #debug   
    #print(result) #debug
    test_id = dir_name.split('/')[-1] #last item

    return (test_id, result)

if __name__ == "__main__":

    process(dir_name=sys.argv[1],duration=int(sys.argv[2]),mapping=sys.argv[3])
