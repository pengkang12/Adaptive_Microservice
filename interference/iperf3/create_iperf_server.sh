#kubectl apply -f iperf_server1.yaml -n robot-shop
#kubectl apply -f iperf_service1.yaml -n robot-shop
kubectl apply -f iperf_server2.yaml -n robot-shop
kubectl apply -f iperf_service2.yaml -n robot-shop
kubectl apply -f iperf_server3.yaml -n robot-shop
kubectl apply -f iperf_service3.yaml -n robot-shop
kubectl get service -n robot-shop | grep iperf

echo "please modify file, including iperf_client1, iperf_client2, iperf_client3, that ip address should be service ip"
