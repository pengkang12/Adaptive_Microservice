#constrained nonlinear optimization 
from scipy.optimize import minimize
from scipy.optimize import Bounds
from scipy.optimize import BFGS
from scipy.optimize import LinearConstraint
from scipy.optimize import NonlinearConstraint
import joblib
import numpy as np
import timeit


slo_target = {
    'user' : 200,
    'cart' : 200,
    'catalogue' : 200,
    'payment' : 200,
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

CPU_length = 2

half_cpu_length = 3
slo_target = 160


def optimize(model, data, name):

    selected_feature = model[name]
    scaler = model['scaler']
    cpu_loc = model['cpu_loc'] 
    slo_target = model['slo_target'] 
    start = timer()
    
    ### initialize data
    rdf = data[selected_feature]
    #normalized values
    norm_temp = scaler.transform(temp)
    
    def cpusum(x):
        """sum of normalized cpu utilization of various microservices"""
        return -1*sum(x)

    def cons_f(x):
        temp = norm_temp.copy()
        for val in x:
            temp[cpu_loc] = val
        #temp = np.concatenate(( x, norm_vm, norm_workload), axis=None).reshape(1,length)
        y_pred, sigma = model_gp.predict(temp, return_std=True)
        return -1.0*(y_pred+2*sigma)+slo_target

    bounds = [(-1,1)]*len(cpu_loc)
    cons = ({'type': 'ineq', 'fun': cons_f})
    res = shgo(cpusum, bounds, iters=10,constraints=cons)
    print(res.x, cpusum(res.x))

    temp = norm_temp.copy()
    for val in res.x:
        temp[cpu_loc] = val
 
    y_pred, sigma = model_gp.predict(temp, return_std=True)
    print("response time=", y_pred, "stdev=", sigma, "target=", slo_target)
    final_result = scaler.inverse_transform(temp)[0]
    cputhresholds = [final_result[loc] for loc in cpu_loc]
    end = timer()
    print ("optimize time is ", end - start)
    print ("denormalized cpu utilization % thresholds=", cputhresholds)
    print ("sum of denormalized cpu utilization % =", sum(cputhresholds))
    print ("\n")
