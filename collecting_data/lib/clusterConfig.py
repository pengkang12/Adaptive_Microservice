from kubernetes import client, config
from kubernetes.client.rest import ApiException
from pprint import pprint
import time
import yaml 

# TODO: move static config of this object to a conf file so it isn't hard coded    
class ClusterInfo(object):
    testNS = "robot-shop"
    workflowDeplList = {"cart": 0, "catalogue": 0,"shipping":0, "payment":0,"ratings":0,"user":0,"web":0}
    interferenceZone = ""
    interferenceLvl = 0
    interferenceCompletionCount = 0
    interferenceType = "stream"


def deletebatchJobs(batch_api,configs):
    name = configs.interferenceType
    namespace = configs.testNS

    try: 
        api_response = batch_api.delete_namespaced_job(name, namespace, pretty='true', grace_period_seconds=2, propagation_policy='Background')
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling BatchV1Api->delete_namespaced_job: %s\n" % e)


def clusterSetup(api_instance, batch_api, configs):
    for deployment, replicaCnt in configs.workflowDeplList.items():
        # setup correct pod replica count for workflow deployments 
        try: 

            print("namespace", configs.testNS, configs.workflowDeplList, deployment)
            workflow_depl = api_instance.read_namespaced_deployment(
                name=deployment,
                namespace=configs.testNS,
                pretty='true',
                exact=True,
                export=True)

            workflow_depl.spec.replicas = int(replicaCnt)
            print("\nUpdating deployment %s with replicaCnt %d\n" % (deployment, workflow_depl.spec.replicas))
            updated_depl = api_instance.patch_namespaced_deployment(
                name=deployment,
                namespace=configs.testNS,
                body=workflow_depl)
            
            #check to confirm that replica cnt is now at correct amount
            ready = False
            for i in range(10):
                time.sleep(3)
                check_depl = api_instance.read_namespaced_deployment(
                    name=deployment,
                    namespace=configs.testNS,
                    pretty='true',
                    exact=True,
                    export=True)
                if check_depl.spec.replicas == int(replicaCnt):
                    print("--Deployment %s updated to replica cnt='%d'" % (updated_depl.metadata.name, updated_depl.spec.replicas))
                    ready = True
                    break

            if ready == False:    
                print("-- Deployment %s not able to be updated within 30sec! ---\n" % deployment)
        
        except ApiException as e:
            print("Exception when calling AppsV1Api->read_namespaced_deployment: %s\n" % e)


    # TODO: place interference deployment in correct zone w/ correct count
    namespace=configs.testNS 
    pretty = 'true' # str | If 'true', then the output is pretty printed. (optional)
    if configs.interferenceLvl > 0:
        body = load_yaml_job_spec(10, configs.interferenceLvl,configs.interferenceZone, configs.interferenceType)
        print(body)
        try: 
            api_response = batch_api.create_namespaced_job(namespace=namespace, body=body, pretty=pretty)
            pprint(api_response)
        except ApiException as e:
            print("Exception when calling BatchV1Api->create_namespaced_job: %s\n" % e)



def load_yaml_job_spec(cntCompletions=10,cntParallelism=2,zone="red",jobType="stream"):
    body = None
    print(jobType)
    if jobType == "stream" or "":
        with open('interference/stream.yaml','r') as f:
            body = yaml.load(f, yaml.FullLoader) 
            pprint(body)
    if body != None:    
        '''
        body.spec.parallelism = cntParallelism
        body.spec.completions = cntCompletions
        zoneSelector  = {}
        zoneSelector['color'] = zone
        body.spec.template.spec.node_selector = zoneSelector
        '''
        body['spec']['parallelism'] = int(cntParallelism)
        body['spec']['completions'] = int(cntCompletions)
        body['spec']['template']['spec']['nodeSelector']['color'] = zone 
        

    return body 
