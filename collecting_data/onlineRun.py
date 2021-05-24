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
import yaml
import datetime
import ast 

from lib.clusterConfig import clusterSetup, deletebatchJobs, ClusterInfo
from lib.kube_config import populateClusterConfig #, workflowScaling
from lib.prom import promQueries
from lib.locust_basic import moveLocustResults
from testRun import collectData

#TODO: Add ability to place interference pods on specific nodes in cluster
#TODO: Add ability to scale different number of pods for each micro-service
#TODO: Figure out strategy for pod isolation on nodes when applying interference to those specific pod(s)
    
def testDirInit(expName):
    currentDir = os.getcwd()
    os.chdir("..")
    # go to previous directory
    workingDir = os.getcwd()
    testDirStr = os.path.join(workingDir, 'data')
    testDirStr = os.path.join(testDirStr, expName)
    if not os.path.exists(testDirStr):
        os.makedirs(testDirStr)
    return testDirStr

def extractData(testDirPath):
    os.chdir("extract_data")
 
    cmdString = "python3.6 driver_main.py"

    cmdArgs = shlex.split(cmdString)
    cmdResultFNm = testDirPath + "/extractLog.txt"
    with open(cmdResultFNm, 'w+') as cmd_f:
        p2 = subprocess.Popen(cmdArgs, stdout=cmd_f, stderr=cmd_f, shell=False)

    print("Started cmd: {0}".format(cmdString))

def onlineScaling(clusterConfs, workflow):
    populateClusterConfig(clusterConfs, workflow)
    #workflowScale(clusterConfs)
 
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
    batch_v1beta1 = client.BatchV1Api()

    clusterConfs = ClusterInfo()

    # fixed parameter
    runtime = "60"
    clientCnt = "10"
    locustDur = runtime + "s"
    exp_Nm = "online_training_real_time_data"
    testDirPath = testDirInit(exp_Nm) #Create current test's directory
    # sampling interval from 5 seconds to 35 seconds
    start_po = "5"
    end_po = "35"
 
    # -------- Main testing loop Start ----------
    for i in range(1, 2):
        print("Current running experiment: %s\n" % exp_Nm)

        #collectData(k8url, locustF, clientCnt, locustDur, exp_Nm, runtime, testDirPath, start_po, end_po)

        # extracted_data
        extractData(testDirPath)
 
        # online inference 
        workflow = None
        # workflow = online_inference()
        
        # add on: if ML's model doesn't work. We request another big machine to re-train model again using our history data. 
        # then we download new model and inference at next time.
        if workflow == None:
            # update
            pass
        else: 
            # online scaling
            onlineScaling(clusterConfs, workflow)
            pass
 
        additional_runtime = 10
        print ("[debug] sleeping for additional {} sec".format(additional_runtime))
        if additional_runtime > 0:
            time.sleep(additional_runtime)
        print("[debug] end time {}".format(datetime.datetime.now()))
        print ("[debug] End of Test")


main()


