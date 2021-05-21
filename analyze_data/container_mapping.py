import os
from collections import defaultdict

def read_container_host_mapping(current_dir, mapFile="container_node_mapping.csv"):
    mapping = defaultdict(list)
    mapFile = os.path.abspath(os.path.join(current_dir, mapFile))

    with open (mapFile,'r') as f:
        for line in f:
            container, node = line.strip('\n').split(' ')
            container = container.split('-')[0] #very first section of the pod name 
            if container not in ["name", "NAME"]:
                mapping[container].append(node)
    return mapping

def read_container_host_mapping_2(current_dir, mapFile="container_node_mapping.csv"):
    mapping = defaultdict(list)
    mapFile = os.path.abspath(os.path.join(current_dir, mapFile))
    with open (mapFile,'r') as f:
        for line in f:
            container, node = line.strip('\n').split(' ')
            if container not in ["name", "NAME"]:
                mapping[container].append(node)
    return mapping

