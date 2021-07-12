dir_name=/home/cc/microservices/Adaptive_Microservice
cd ${dir_name}/extract_data
python3.6 driver_main.py ${dir_name}/training_data/bak/
cp ${dir_name}/bak/bigtable.csv ${dir_name}/training_data/bigtable.csv 
git add ${dir_name}/training_data/bigtable.csv 
git commit -m "update data"
git push

