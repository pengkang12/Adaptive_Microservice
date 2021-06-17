#constrained nonlinear optimization 
from scipy.optimize import minimize, shgo
from scipy.optimize import Bounds
from scipy.optimize import BFGS
from scipy.optimize import LinearConstraint
from scipy.optimize import NonlinearConstraint
import joblib
import numpy as np
import time

slo_target_list = {
    'user' : 150,
    'cart' : 100,
    'catalogue' : 100,
    'payment' : 2000,
    'ratings' : 200,
}

def load_models():
    models = {}
    for name in ['user', 'cart', 'catalogue', 'payment']:
        models[name] = {}
        models[name]['model'] = joblib.load('../ML/models/gp_{}.model'.format(name))
        models[name]['scaler'] = joblib.load('../ML/models/scaler_{}.sav'.format(name))
        models[name]['selected_feature'] = [line.strip() for line in open("../ML/models/selected_feature_{}.txt".format(name), 'r')]
        cpu_loc = []
        for i, feature in enumerate(models[name]['selected_feature']):
            if 'cpu5s' in feature:
                cpu_loc.append(i)
        models[name]['cpu_loc'] = cpu_loc
    return models


def optimize(model, data, workflow):
    
    #print(data)
    model_gp = model['model']
    selected_feature = model['selected_feature']
    scaler = model['scaler']
    
    cpu_loc = model['cpu_loc'] 
    slo_target = slo_target_list[workflow] 
    
    ### initialize data
    X = data[selected_feature]
    
    #normalized values
    norm_temp = scaler.transform(X)[0]
    length = len(norm_temp)
    
    def cpusum(x):
        """sum of normalized cpu utilization of various microservices"""
        return -1*sum(x)

    def cons_f(x):
        temp = update_data(norm_temp, x)
        #temp = np.concatenate(( x, norm_vm, norm_workload), axis=None).reshape(1,length)
        y_pred, sigma = model_gp.predict(temp, return_std=True)
        #print(temp, y_pred, sigma, slo_target)
        return -1.0*(y_pred+2*sigma)+slo_target

    
    def update_data(ret, update_list):
        length = len(ret)
        temp = ret.copy()
        for val in update_list:
            temp[cpu_loc] = val
        return np.array(temp).reshape(1, length)
    
    bounds = [(-1,1)]*len(cpu_loc)
    cons = ({'type': 'ineq', 'fun': cons_f})
    res = shgo(cpusum, bounds, iters=10,constraints=cons)
    print(res.x, cpusum(res.x))

    temp = update_data(norm_temp, res.x)
    y_pred, sigma = model_gp.predict(temp, return_std=True)
    print("response time=", y_pred, "stdev=", sigma, "target=", slo_target)
    final_result = scaler.inverse_transform(temp)[0]
    cputhresholds = [final_result[loc] for loc in cpu_loc]
    print ("denormalized cpu utilization % thresholds=", cputhresholds)
    print ("sum of denormalized cpu utilization % =", sum(cputhresholds))
    print ("\n")
