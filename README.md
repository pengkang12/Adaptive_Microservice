# this project for microservices

# runtine environment
python3.6

# build robot-shop application.

Go into k8s-robot-shop-application. and install it. 

install helm https://helm.sh/docs/intro/install/

helm version is 3.5.4

k8s version is 1.18.2

# workload

Go into load-gen. and check README.

this ip address is the api to access  the Robot-shop application. 
```
kubectl get service -n robot-shop
NAME        TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)              AGE
web         ClusterIP   10.105.207.202   <none>        8080/TCP             10d
```
```
locust --host http://`kubectl get service -n robot-shop |grep web| awk '{print $3}'`:8080 -f load-gen/robot-shop.py -u 10 -t 60s --print-stats --csv=locust  --headless --stop-time=2
```


# how to run program
```
# online version
cd run
bash run_online.sh
```

```
# collectin training data 
cd run
bash run_offline.sh
```


# how to analyze data

```
cd analyze_data
python driver_main.py ../example_data/
```


# how to solve some error.

# check log
```
kubectl -n robot-shop logs -f container-name
```

erro1: mysql and mongodb
if you are running multiple mysql and mongodb, make sure each pod successfully run.

error2: web only can have 1. if you have mutiple web pod, maybe you will face some 504 errro.


error3: payment error. 
check dispatch can access rabbitmq. If can't, delete pod and create again. 

payment gatway can't access.  check k8s/helm/values.yaml ping payment\_gatway.

error4: cart error. check web's number. and check instana is running successful. 


