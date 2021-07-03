name=$1

docker image rm -f `docker image ls | grep $name | awk '{print $3}'`
docker image rm -f `docker image ls | grep none | awk '{print $3}'`

docker build -t kevin2333/rs-${name} ${name}

base_tag=`docker image ls | grep kevin2333/rs-${name} | grep latest | awk '{print $3}'`

echo $base_tag

docker tag $base_tag kevin2333/rs-${name}:latest

docker image push kevin2333/rs-${name}:latest
