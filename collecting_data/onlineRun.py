''' online collecting data
'''
import os
import sys
import argparse
import shlex, subprocess
import datetime
import time
from  prometheus_http_client import Prometheus
from kubernetes import client, config
import json
import csv
import ast 

from lib.clusterConfig import clusterSetup, deletebatchJobs, ClusterInfo, workflowScale, populateClusterConfig
from lib.prom import promQueries
from lib.locust_basic import moveLocustResults
from testRun import collectData
from lib.basic import testDirInit

#TODO: Add ability to place interference pods on specific nodes in cluster
#TODO: Add ability to scale different number of pods for each micro-service
#TODO: Figure out strategy for pod isolation on nodes when applying interference to those specific pod(s)
   

data_dir = "online_data"


def extractData(testDirPath):
    os.chdir("extract_data")
 
    cmdString = "python3.6 driver_main.py ../{0}/".format(data_dir)

    cmdArgs = shlex.split(cmdString)
    cmdResultFNm = testDirPath + "/extractLog.txt"
    with open(cmdResultFNm, 'w+') as cmd_f:
        p2 = subprocess.Popen(cmdArgs, stdout=cmd_f, stderr=cmd_f, shell=False)

    print("Started cmd: {0}".format(cmdString))
    os.chdir("..")
    # store old data

def onlineScaling(apps_instance, clusterConfs, workflow):
    populateClusterConfig(clusterConfs, workflow)
    workflowScale(apps_instance, clusterConfs)

def onlineInference():
    # read data from bigtable.csv
    current_data = []
    with open('{}/bigtable.csv'.format(data_dir)) as bigtable_file:
        csv_reader = csv.reader(bigtable_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            current_data.append(row)
    print(current_data)
    os.system("tail -n 1 {0}/bigtable.csv >> {0}/bigtable_history.csv".format(data_dir))
    return current_data

def main():
    #construct & parse args
    ap = argparse.ArgumentParser()
    ap.add_argument("-pName", "--prometheus-operator-685cb6b46b-l6hrd", required=True,
        help="Name of prometheus operator pod inside k8 cluster")
    ap.add_argument("-k8url", required=True,
        help="URL & port number of k8 cluster we are accessing")
    ap.add_argument("-locustF", required=True,
        help="Name of locust file to be used for this round of testing")
    # add more args here
    args = vars(ap.parse_args())

    k8url = args['k8url']
    locustF = args['locustF']

    #kubernetes setup
    config.load_kube_config()
    apps_v1 = client.AppsV1Api()

    clusterConfs = ClusterInfo()

    # fixed parameter
    runtime = "60"
    clientCnt = "10"
    locustDur = runtime + "s"
    
    # sampling interval from 5 seconds to 35 seconds
    start_po = "5"
    end_po = "35"
    
    # return to previous directory 
    os.chdir("..")
    # -------- Main testing loop Start ----------
    for i in range(1, 5):
        now = datetime.datetime.now()
        current_time = now.strftime("%m-%d-%H-%M")
        exp_Nm = "{0}".format(current_time)
        testDirPath = testDirInit(exp_Nm, data_dir) #Create current test's directory
 
        print("Current running experiment: %s\n" % exp_Nm)

        collectData(k8url, locustF, clientCnt, locustDur, exp_Nm, runtime, testDirPath, start_po, end_po) 
        additional_runtime = 10
        print ("[debug] sleeping for additional {} sec".format(additional_runtime))
        if additional_runtime > 0:
            time.sleep(additional_runtime)
        # extracted_data
        extractData(testDirPath)
 
        # online inference 
        workflow = {'cart': 1, 'ratings': 1, 'shipping': 1, 'catalogue': 1, 'user': 1, 'payment': 1}
        # workflow = online_inference()
        onlineInference() 
        # add on: if ML's model doesn't work. We request another big machine to re-train model again using our history data. 
        # then we download new model and inference at next time.
        if workflow == None:
            # update
            pass
        else: 
            # online scaling
            onlineScaling(apps_v1, clusterConfs, workflow)
            pass
 
       # update exp_Nm, because pod has a new name.

main()


