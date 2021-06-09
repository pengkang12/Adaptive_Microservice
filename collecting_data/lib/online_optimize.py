#constrained nonlinear optimization 
from scipy.optimize import minimize
from scipy.optimize import Bounds
from scipy.optimize import BFGS
from scipy.optimize import LinearConstraint
from scipy.optimize import NonlinearConstraint
import joblib
import numpy as np
import timeit

def load_models():
    models = {}
    models['models'] = []
    models['scalers'] = []
    for name in ['user', 'cart', 'catalogue', 'payment']:
        models['models'].append(joblib.load('../ML/models/gp_{}.model'.format(name)))
        models['scalers'].append(joblib.load('../ML/models/scaler_{}.sav'.format(name)))
    return models

CPU_length = 2

half_cpu_length = 3
slo_target = 160


def optimize(model, scaler, selected_feature, data):

    start = timer()
    
    length = len(selected_feature)
    CPU_length = 6
    half_cpu_length = 3
    slo_target = 2506

    ### initialize data
    rdf = data[selected_feature]
    workload = data[-1:]
    cpu0 = data[0:CPU_length]
    vm = data[CPU_length:-1]

    temp = np.concatenate((cpu0, vm, workload), axis=None).reshape(1,length)
    #normalized values
    norm_temp = scaler.transform(temp)
    norm_cpu0 = norm_temp[0][0:CPU_length]
    norm_vm = norm_temp[0][CPU_length:-1]
    norm_workload = norm_temp[0][-1:]
    
    def cpusum(x):
        """sum of normalized cpu utilization of various microservices"""
        return -1*sum(x)

    def cons_f(x):
        temp = np.concatenate(( x, norm_vm, norm_workload), axis=None).reshape(1,length)
        y_pred, sigma = model_gp.predict(temp, return_std=True)
        return -1.0*(y_pred+2*sigma)+slo_target


    bounds = [(-1,1)]*CPU_length
    cons = ({'type': 'ineq', 'fun': cons_f})
    res = shgo(cpusum,bounds,iters=10,constraints=cons)
    print (res.x, cpusum(res.x))

    temp = np.concatenate((res.x,norm_vm,norm_workload), axis=None).reshape(1,length)
    y_pred, sigma = model_gp.predict(temp, return_std=True)
    print("response time=", y_pred, "stdev=", sigma, "target=", slo_target)
    cputhresholds = scaler.inverse_transform(temp)[0][0:half_cpu_length]
    networkthresholds = scaler.inverse_transform(temp)[0][half_cpu_length:CPU_length]
    all = scaler.inverse_transform(temp)[0][0:CPU_length]

    end = timer()
    print ("optimize time is ", end - start)
    print ("denormalized cpu utilization % thresholds=", cputhresholds)
    print ("sum of denormalized cpu utilization % =", sum(cputhresholds))
    print ("denormalized network Write % thresholds=", networkthresholds)
    print ("\n")
    print (cpu0.columns)
    print (np.divide(cpu0.to_numpy(), np.array(all)))
