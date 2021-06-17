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
from lib.online_optimize import optimize, load_models
from lib.container_mapping import read_container_host_mapping_3

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
    time.sleep(3)
    # store old data

def onlineScaling(apps_instance, clusterConfs, workflow):
    populateClusterConfig(clusterConfs, workflow)
    workflowScale(apps_instance, clusterConfs)

def onlineInference(model_list, workflows):
    # read data from bigtable.csv
    current_data = []
    with open(os.getcwd()+'/{}/bigtable.csv'.format(data_dir)) as bigtable_file:
        csv_reader = csv.reader(bigtable_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            current_data.append(row)
    # remember update thread number for current_data
    print("inference data is ", current_data[1])
    os.system("mv {0}/online_* /tmp/data/".format(data_dir))
    print("inference model information is ", model_list)
     
    new_workflows = {} 
    updated_workflow = False
    for name in model_list.keys():
        #new_workflows = optimize(model_list[name], current_data[1], name)
        for key in new_workflows.keys():
            if new_workflows[key] != workflows[key]:
                updated_workflow = True 
                workflows[key] = new_workflows[key] 
 
    return workflows, updated_workflow

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



    model_list = load_models()

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
        exp_Nm = "online_color_1_none_none_{}".format(current_time)
        testDirPath = testDirInit(exp_Nm, data_dir) #Create current test's directory
 
        collectData(k8url, locustF, clientCnt, locustDur, exp_Nm, runtime, testDirPath, start_po, end_po) 
        additional_runtime = 10
        print ("[debug] sleeping for additional {} sec".format(additional_runtime))
        if additional_runtime > 0:
            time.sleep(additional_runtime)
        
        # extracted_data
        extractData(testDirPath)
        
        # get workflow information
        workflow = {'cart': 1, 'catalogue': 1, 'mongodb': 1, 'mysql': 1, 
                    'payment': 1, 'ratings': 1, 'shipping': 1, 'user': 1, 'web': 1} 
        real_workflow = read_container_host_mapping_3(testDirPath)
        for key in workflow.keys():
            workflow[key] = real_workflow[key]
        print(workflow)

        # online inference 
        workflow, updated_workflow = onlineInference(model_list, workflow) 
        # add on: if ML's model doesn't work. We request another big machine to re-train model again using our history data. 
        # then we download new model and inference at next time.
        if updated_workflow == True:
            # online scaling
            #onlineScaling(apps_v1, clusterConfs, workflow)
            pass
        print("---------------------------------end experiment---------------------------------\n")
main()


