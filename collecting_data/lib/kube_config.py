''' Current assumptions:
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

#TODO: Add ability to place interference pods on specific nodes in cluster
#TODO: Add ability to scale different number of pods for each micro-service
#TODO: Figure out strategy for pod isolation on nodes when applying interference to those specific pod(s)
class podDataCollection(object):
    podName = ""
    cpu5s = []
    memW5s = []
    memR5s = []
    netW5s = []
    netR5s = []

    def __init__(self, name):
        self.podName = name

    
def testDirInit(expName):
    workingDir = os.getcwd()
    testDirStr = os.path.join(workingDir, expName)
    if not os.path.exists(testDirStr):
        os.makedirs(testDirStr)
    return testDirStr

def populateClusterConfig(clusterObject, configDict):
    #workflowDeplList = {"cart": 0, "catalogue": 0,"shipping":0, "payment":0,"ratings":0,"user":0,"web":0}

    for key in configDict:
        clusterObject.workflowDeplList[key] = configDict[key]
