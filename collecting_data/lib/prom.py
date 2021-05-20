#https://itnext.io/k8s-monitor-pod-cpu-and-memory-usage-with-prometheus-28eec6d84729

import time
from  prometheus_http_client import Prometheus
import json
import csv

class podDataCollection(object):
    podName = ""
    cpu5s = []
    memW5s = []
    memR5s = []
    netW5s = []
    netR5s = []

    def __init__(self, name):
        self.podName = name

# promQueries function 
def promQueries(startTime, stopTime, testDirPath):
    prom = Prometheus()
    namespace = "robot-shop" 
    step='5s'
    # If you’re using Kubernetes 1.16 and above you’ll have to use pod instead of pod_name and container instead of container_name.
    # Can use queries below to find rate of change also
    cpu5s = json.loads(prom.query_rang(metric='sum(rate(container_cpu_usage_seconds_total{namespace="default"}[1m])) by (pod)', start=startTime, end=stopTime, step=step))
    memWriteB5s = json.loads(prom.query_rang(metric='sum(rate(container_fs_writes_bytes_total{namespace="robot-shop"}[1m])) by (pod)', start=startTime, end=stopTime, step=step))
    memReadB5s = json.loads(prom.query_rang(metric='sum(rate(container_fs_reads_bytes_total{namespace="robot-shop"}[1m])) by (pod)', start=startTime, end=stopTime, step=step))
    netReadB5s = json.loads(prom.query_rang(metric='sum(irate(container_network_receive_bytes_total{namespace="default"}[1m])) by (pod)', start=startTime, end=stopTime, step=step))
    netWriteB5s = json.loads(prom.query_rang(metric='sum(irate(container_network_transmit_bytes_total{namespace="default"}[1m])) by (pod)', start=startTime, end=stopTime, step=step))

    podMetricsDict = {} # List of podDataCollection objects
    timestampList = [] # List of scraped timestamps
    podNameList = [] # List of scraped pods

    print("cpu5s, ", cpu5s)
    # Create list of podDataCollection objects, with CPU vals:
    for pod in cpu5s['data']['result']:
        p = podDataCollection(pod['metric']['pod'])
        podNameList.append(pod['metric']['pod'])
        p.cpu5s = pod['values']
        podMetricsDict[p.podName] = p

    for tStamp, val in pod['values']:
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


    step='5s'
    cpu5s = json.loads(prom.query_rang(metric='sum(rate(container_cpu_usage_seconds_total{namespace="robot-shop"}[1m])) by (pod)', start=startTime, end=stopTime, step='5s'))
    print(cpu5s)     

    cpu5s = json.loads(prom.query_rang(metric='sum(rate(container_cpu_usage_seconds_total{namespace="robot-shop"}[5m])) by (pod)', start=startTime, end=stopTime, step='5s'))
     
    print(cpu5s)     



if __name__ == '__main__':
    main()

