export web_url=`kubectl get service web -n robot-shop | grep web | awk '{print $3}'`
export web_port=`kubectl get services -n robot-shop | grep web | awk '{print $5}' | cut -d ":" -f1`
echo "web is "$web_url:$web_port

# how do you install prometheus, https://github.com/giantswarm/prometheus
# kubectl get service -n monitoring
# prometheus                 NodePort    10.97.48.8       <none>        9090:31674/TCP   12m
# big picture for prometheus.https://prometheus.io/docs/introduction/overview/
export PROMETHEUS_URL="http://"`kubectl get service -n monitoring | grep prometheus-k8s | awk '{print $3}'`":9090"
echo "promethues "$PROMETHEUS_URL

prometheusName=`kubectl get pod -n monitoring | grep operator | awk '{print $1}'`

sleep 460

python3.6 ../collecting_data/testRun.py -f run/produce_input_data/inputTest.txt -pName $prometheusName -k8url $web_url:$web_port -locustF load-gen/robot-shop.py >> /tmp/result.log &

