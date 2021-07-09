redis-cli -h `kubecmd get svc | grep redis | awk '{print $3}'`  keys "*"

# for shippings
mysql -u shipping -psecret -h `kubecmd get svc | grep mysql | awk '{print $3}'`   citie

# connect mongodb
mongo `kubecmd get svc | grep mongodb | awk '{print $3}'`:27017

# for ratings
mysql -u root -h `kubecmd get svc | grep mysql | awk '{print $3}'`
mysql -u ratings -piloveit -h `kubecmd get svc | grep mysql | awk '{print $3}'`

