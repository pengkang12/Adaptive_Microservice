''' Current assumptions:
    --

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
import ast 

from lib.clusterConfig import clusterSetup, deletebatchJobs, ClusterInfo, populateClusterConfig 
from lib.prom import promQueries
from lib.locust_basic import moveLocustResults
from lib.basic import testDirInit


data_dir = "training_data"
#TODO: Add ability to place interference pods on specific nodes in cluster
#TODO: Add ability to scale different number of pods for each micro-service
#TODO: Figure out strategy for pod isolation on nodes when applying interference to those specific pod(s)

def collectData(k8url, locustF, clientCnt, locustDur, exp_Nm, runtime, testDirPath, start_po, end_po):

    print("\nTest %s start" % exp_Nm)
    # build locust command to run locust
    locustCmd = "locust --host http://" + k8url + " -f " + locustF + " -u " + clientCnt + " -t " + locustDur + " --headless --print-stats --csv=locust "

    locustArgs = shlex.split(locustCmd)
    print("locust Command: %s" % locustCmd)
    print("locust CMD args: %s" % locustArgs)
    # TODO: Later: confirm cluster is setup properly

    # Get time-stamp before running test

    # TODO: add perfstat shell cmd in 
    # Exec perfstat using params passed in through testParam file
    # #format: python <script_name> exp_name total_duration output_dir

    perfstatCmdString = "python3.6 collecting_data/perfstat_driver.py {} {} {}".format(exp_Nm,runtime,testDirPath)

    perfstatArgs = shlex.split(perfstatCmdString)
    perfstatResultFNm = testDirPath + "/perfstatLog.txt"
    with open(perfstatResultFNm, 'w+') as perfstat_f:
        p1 = subprocess.Popen(perfstatArgs, stdout=perfstat_f, stderr=perfstat_f, shell=False)
    
    print("Started Perfstat {0}".format(perfstatCmdString))        
    # Exec vmstat using params passed
    vmstatCmdString = "python3.6 collecting_data/vmstat_driver.py {} {} {} {} {}".format(exp_Nm,runtime,testDirPath,start_po,end_po)

    vmstatArgs = shlex.split(vmstatCmdString)
    vmstatResultFNm = testDirPath + "/vmstatLog.txt"
    with open(vmstatResultFNm, 'w+') as vmstat_f:
        p2 = subprocess.Popen(vmstatArgs, stdout=vmstat_f, stderr=vmstat_f, shell=False)

    print("Started VMStat: {0}".format(vmstatCmdString))
    print("[debug] start time {}".format(datetime.datetime.now()))

    startT = time.time() 
    
    startT2 = datetime.datetime.now()        
    # Exec locust command, exporting to CSV file & using params passed in through testParam file
    locustResultFNm = testDirPath + "/LocustLog.txt"
    with open(locustResultFNm, 'w+') as locust_f:
        p = subprocess.call(locustArgs, stdout=locust_f, stderr=locust_f, shell=False)
    
    # Once locust command finishes, get end timestamp
    stopT = time.time()
    stopT2 = datetime.datetime.now()
    print ("[debug] test is completed. post processing")

    moveLocustResults(testDirPath)
    
    time.sleep(15)
    cmd = "kubectl get pod -o wide -n robot-shop | awk '{print $1, $7}' > "+testDirPath+"/container_node_mapping.csv &"
    os.system(cmd)     
    # Exec Prometheus API query(s) to gather metrics & build resulting csv files
    time.sleep(15)        
    promQueries(int(startT), int(stopT), testDirPath)
     
    return (int(runtime) - int(stopT-startT) ) + 10

def main():
    #construct & parse args
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--file", required=True,
        help="Name of input file containing test params")
    ap.add_argument("-pName", "--prometheus-operator-685cb6b46b-l6hrd", required=True,
        help="Name of prometheus operator pod inside k8 cluster")
    ap.add_argument("-k8url", required=True,
        help="URL & port number of k8 cluster we are accessing")
    ap.add_argument("-locustF", required=True,
        help="Name of locust file to be used for this round of testing")
    # add more args here
    args = vars(ap.parse_args())
    #kubernetes setup
    config.load_kube_config()
    apps_v1 = client.AppsV1Api()
    batch_v1beta1 = client.BatchV1Api()

    clusterConfs = ClusterInfo()
    interference_level = {} 
    interference_level['low'] = 1
    interference_level['medium'] = 2
    interference_level['high'] = 3 
    
    k8url = args['k8url']
    locustF = args['locustF']    

    os.chdir("..")
    # -------- Main testing loop Start ----------
    for line in open(args["file"]):
        if line.startswith("#"):
            continue
        lnArgs = [x.strip() for x in line.split('/')]
        # if len(lnArgs) != 9: # change val to appropriate cnt later
        #     print("Skipping experiment %s, wrong number of args" % lnArgs[0])
        #     continue
        exp_Nm = lnArgs[0]
        runtime = lnArgs[1]
        clientCnt = lnArgs[3]

        testDirPath = testDirInit(exp_Nm, data_dir) #Create current test's directory
        clusterConfs.interferenceType = lnArgs[2]   
        clusterConfs.interferenceZone = lnArgs[4]
        clusterConfs.interferenceLvl = interference_level[lnArgs[5]]

        populateClusterConfig(clusterConfs, ast.literal_eval(lnArgs[6]))
        start_po = lnArgs[7]
        end_po = lnArgs[8]
        # add more var defs here ^ if more args get added to lines (like node color interference is on)
        print("Current running experiment: %s\n" % exp_Nm)
        locustDur = runtime + "s"
        
        # setup cluster using input params
        print("Configuring cluster to match experiment input, %s\n" %clusterConfs)
        clusterSetup(apps_v1, batch_v1beta1, clusterConfs)
        print("10 seconds grace period\n")
        time.sleep(15)

        additional_runtime = collectData(k8url, locustF, clientCnt, locustDur, exp_Nm, runtime, testDirPath, start_po, end_po)
        # delete the batch jobs 
        if clusterConfs.interferenceLvl > 0:
            deletebatchJobs(batch_v1beta1,clusterConfs)

        print("[debug] sleeping for additional {} sec".format(additional_runtime))
        if additional_runtime > 0:
            time.sleep(additional_runtime)
        print("[debug] end time {}".format(datetime.datetime.now()))
        print("[debug] End of Test")

if __name__ == '__main__':
    main()


