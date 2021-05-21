#https://itnext.io/k8s-monitor-pod-cpu-and-memory-usage-with-prometheus-28eec6d84729

import time
import json
import csv
import os

from  prometheus_http_client import Prometheus

class podDataCollection(object):
    podName = ""
    cpu5s = []
    memW5s = []
    memR5s = []
    netW5s = []
    netR5s = []

    def __init__(self, name):
        self.podName = name

# generate and save container metrics csv files in testing dir
def createRawCSVs(tStampList, podNmList, testDirPath, podMetDict):
    # create CPU csv
    with open(os.path.join(testDirPath, 'container-cpu5sRaw.csv'), mode='w') as cpu_file:
        fieldnms = ['Pod_Name']
        fieldnms.extend(tStampList)
        writer = csv.DictWriter(cpu_file, fieldnames=fieldnms)
        writer.writeheader()

        for pod in podNmList:
            cpuVals = podMetDict[pod].cpu5s
            rowDict = {'Pod_Name' : pod }
            for pair in cpuVals:
                if pair[0] in tStampList:
                    rowDict[pair[0]] = pair[1]
            try:
                writer.writerow(rowDict)
            except:
                print("Cpu write error: {0}".format(rowDict))

    # create MemW/R csv
    with open(os.path.join(testDirPath, 'container-memR5sRaw.csv'), mode='w') as memR_file:
        fieldnms = ['Pod_Name']
        fieldnms.extend(tStampList)
        writer = csv.DictWriter(memR_file, fieldnames=fieldnms)
        writer.writeheader()

        for pod in podNmList:
            memRVals = podMetDict[pod].memR5s
            rowDict = {'Pod_Name' : pod }
            for pair in memRVals:
                if pair[0] in tStampList:
                    rowDict[pair[0]] = pair[1]
            writer.writerow(rowDict)

    with open(os.path.join(testDirPath, 'container-memW5sRaw.csv'), mode='w') as memW_file:
        fieldnms = ['Pod_Name']
        fieldnms.extend(tStampList)
        writer = csv.DictWriter(memW_file, fieldnames=fieldnms)
        writer.writeheader()

        for pod in podNmList:
            memWVals = podMetDict[pod].memW5s
            rowDict = {'Pod_Name' : pod }
            for pair in memWVals:
                if pair[0] in tStampList:
                    rowDict[pair[0]] = pair[1]
            writer.writerow(rowDict)

    # create NetW/R csv
    with open(os.path.join(testDirPath, 'container-netR5sRaw.csv'), mode='w') as netR_file:
        fieldnms = ['Pod_Name']
        fieldnms.extend(tStampList)
        writer = csv.DictWriter(netR_file, fieldnames=fieldnms)
        writer.writeheader()

        for pod in podNmList:
            netRVals = podMetDict[pod].netR5s
            rowDict = {'Pod_Name' : pod }
            for pair in netRVals:
                 if pair[0] in tStampList:
                    rowDict[pair[0]] = pair[1]
            writer.writerow(rowDict)

    with open(os.path.join(testDirPath, 'container-netW5sRaw.csv'), mode='w') as netW_file:
        fieldnms = ['Pod_Name']
        fieldnms.extend(tStampList)
        writer = csv.DictWriter(netW_file, fieldnames=fieldnms)
        writer.writeheader()

        for pod in podNmList:
            netWVals = podMetDict[pod].netW5s
            rowDict = {'Pod_Name' : pod }
            for pair in netWVals:
                if pair[0] in tStampList:
                    rowDict[pair[0]] = pair[1]
            writer.writerow(rowDict)

# promQueries function 
def promQueries(startTime, stopTime, testDirPath):
    prom = Prometheus()
    namespace = "robot-shop" 
    step='5s'
    # If you’re using Kubernetes 1.16 and above you’ll have to use pod instead of pod_name and container instead of container_name.
    # Can use queries below to find rate of change also
    cpu5s = json.loads(prom.query_rang(metric='sum(rate(container_cpu_usage_seconds_total{namespace="'+namespace+'"}[1m])) by (pod)', start=startTime, end=stopTime, step=step))
    memWriteB5s = json.loads(prom.query_rang(metric='sum(rate(container_fs_writes_bytes_total{namespace="'+namespace+'"}[1m])) by (pod)', start=startTime, end=stopTime, step=step))
    memReadB5s = json.loads(prom.query_rang(metric='sum(rate(container_fs_reads_bytes_total{namespace="'+namespace+'"}[1m])) by (pod)', start=startTime, end=stopTime, step=step))
    netReadB5s = json.loads(prom.query_rang(metric='sum(irate(container_network_receive_bytes_total{namespace="'+namespace+'"}[1m])) by (pod)', start=startTime, end=stopTime, step=step))
    netWriteB5s = json.loads(prom.query_rang(metric='sum(irate(container_network_transmit_bytes_total{namespace="'+namespace+'"}[1m])) by (pod)', start=startTime, end=stopTime, step=step))

    podMetricsDict = {} # List of podDataCollection objects
    timestampList = [] # List of scraped timestamps
    podNameList = [] # List of scraped pods
    tmp_pod = []
    print("cpu5s, ", cpu5s)
    # Create list of podDataCollection objects, with CPU vals:
    for pod in cpu5s['data']['result']:
        p = podDataCollection(pod['metric']['pod'])
        podNameList.append(pod['metric']['pod'])
        p.cpu5s = pod['values']
        podMetricsDict[p.podName] = p
        if not tmp_pod:
            tmp_pod = pod['values'] 
    print("tmp_pdo", tmp_pod) 
    for tStamp, val in tmp_pod:
        timestampList.append(tStamp)

    for pod in memWriteB5s['data']['result']:
        podMetricsDict[pod['metric']['pod']].memW5s = pod['values']
        
    for pod in memReadB5s['data']['result']:
        podMetricsDict[pod['metric']['pod']].memR5s = pod['values']  

    for pod in netWriteB5s['data']['result']:
        podMetricsDict[pod['metric']['pod']].netW5s = pod['values']   

    for pod in netReadB5s['data']['result']:
        podMetricsDict[pod['metric']['pod']].netR5s = pod['values']
    print(podMetricsDict)

    createRawCSVs(timestampList, podNameList, testDirPath, podMetricsDict)

def main():
    prom = Prometheus()
    namespace = "robot-shop" 
    startTime = time.time()
    time.sleep(30)
    stopTime = time.time()
    time.sleep(5)
    promQueries(startTime, stopTime, "/tmp/")

    


if __name__ == '__main__':
    main()

