redis-cli -h 10.108.141.22 keys "*"

# for shippings
mysql -u shipping -psecret -h `kubecmd get svc | grep mysql | awk '{print $3}'`   citie

# connect mongodb
mongo --host mongodb://`kubecmd get svc | grep mongodb | awk '{print $3}'`:27017

# for ratings
mysql -u root -h `kubecmd get svc | grep mysql | awk '{print $3}'`

