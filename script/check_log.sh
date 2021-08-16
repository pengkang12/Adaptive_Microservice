name=$1
declare -a arr=(`kubectl -n robot-shop get pod | grep $name | awk '{print $1}'`)
kubectl -n robot-shop logs -f ${arr[$2]}
