helm uninstall robot-shop --namespace robot-shop 
sleep 15

helm install robot-shop --namespace robot-shop .
