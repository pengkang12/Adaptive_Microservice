# usage:

#python generate_test_case.py <output_file>
#output_format 

#test_id, #duration, #rate, #connection, #zone, #interference_level, #cart,#catalogue,#shipping,#start_pos, #end_pos

import random
import sys
from datetime import date 
import hashlib
duration = 120 #sec


def getClusterConfiguration(cntCart=1,cntCatalogue=1,cntShipping=1,cntPayment=1,cntRatings=2,cntUser=2, cntWeb=2):
    pods = {}
    pods['cart'] = cntCart
    pods['catalogue'] = cntCatalogue
    pods['shipping'] = cntShipping
    pods['payment'] = cntPayment
    pods['ratings'] = cntRatings
    pods['user'] = cntUser
    # web should be 1, if increase web's number, the error will have.
    pods['web'] = cntWeb
    return pods

def getConfigHash(pods):
    result = 0
    for k in sorted(pods.keys()):
        result *= 10
        result += pods[k]
    
    return result 

start_position = 15
end_position = 120

output_file = "default_test_case.csv"

zones = ['red', 'green','blue', 'yellow']

interference_level = ['low','medium']
interference_type = ['stream', 'iperf']
#interference_type = ['iperf']
interference_level = ['none']
connections = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
connections = [10, 20, 30, 40, 50]


workflow = ["cart", "catalogue", "ratings", "user", "shipping", "payment"]

# variables - zone, interference_level, connection


def produce(shipping=4, ratings=3):


    paramCnt = {}
    for pod in workflow:
        paramCnt[pod] = 5
    paramCnt['cart'] = 6
    paramCnt['shipping'] = shipping
    paramCnt['ratings'] = ratings
    #paramCnt['payment'] = 1 


    for work in ["cart", "catalogue", "payment", "user"]:#"ratings", "shipping"]:
        for cnt in [5,4,3,2]:
        #if True: 
            paramCnt[work] -= 1
            if paramCnt[work] == 1:
                paramCnt[work] = 2
                continue 
            for zone in zones:
                for j, i_type in enumerate(interference_type):
                    if j == random.randint(0, 2):
                        continue
                    for k, i_level in enumerate(interference_level):
                        if k == random.randint(0, 2):
                            #i_level = 'none'
                            continue
                        for con in connections:
                            today = date.today()
                            date_prefix = today.strftime("%b%d")
                            configuration = getClusterConfiguration(cntCart = paramCnt["cart"], cntCatalogue = paramCnt["catalogue"],
                            cntShipping = paramCnt["shipping"], cntRatings = paramCnt["ratings"],
                            cntPayment = paramCnt["payment"], cntUser=paramCnt["user"])

                            test_id = "{}_{}_{}_{}_{}_{}".format(date_prefix,zone,con, i_type, i_level, getConfigHash(configuration) )
                            data = "{}/{}/{}/{}/{}/{}/{}/{}/{}\n".format(test_id,duration,i_type,con,zone,i_level,configuration,start_position,end_position)                             
                            f.write(data)
    print("test")
with open(output_file,'a' )as f:
    f.write("#test_id/duration/rate/con/zone/i_level/{configuration}/start_position/end_position\n")
    produce(shipping=5, ratings=5)
    #produce(shipping=3, ratings=3)
    #produce(shipping=3, ratings=2)




