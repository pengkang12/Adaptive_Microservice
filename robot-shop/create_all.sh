docker image rm -f `docker image ls | grep kevin2333 | awk '{print $3}'`

for name in "cart" "catalogue" "shipping" "ratings" "user" "payment"
do
echo 123
#echo cloud123 | sudo -S bash ~/robot-shop/create_docker.sh $name  
done
