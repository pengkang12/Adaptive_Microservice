cd /home/cc/microservices/2019_experiments/extract_data
python3.6 driver_main.py /home/cc/microservices/2019_experiments/training_data/bak/
cp /home/cc/microservices/2019_experiments/training_data/bak/bigtable.csv /home/cc/microservices/2019_experiments/training_data/bigtable.csv 
git add /home/cc/microservices/2019_experiments/training_data/bigtable.csv 
git commit -m "update data"
git push

