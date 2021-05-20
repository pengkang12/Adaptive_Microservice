# this project for microservices

# runtine environment
python3.6

# check environment
locust version is 1.5.1

this ip address is the api to access  the Robot-shop application. http://10.105.207.202:8080 
```
kubectl get service -n robot-shop
NAME        TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)              AGE
web         ClusterIP   10.105.207.202   <none>        8080/TCP             10d
```

```
locust --host http://10.105.207.202:8080 -f robot-shop.py -u 10 -t 110s --print-stats --csv=locust  --headless 
```

# how to run program

bash run.sh


