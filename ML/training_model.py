from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC, LinearSVC
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import cross_val_predict, RandomizedSearchCV, GridSearchCV, train_test_split, cross_val_score
from sklearn.preprocessing import normalize
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C, RationalQuadratic, WhiteKernel, Matern
from sklearn.neural_network import MLPRegressor
from sklearn import datasets
from sklearn import linear_model
from sklearn.ensemble import RandomForestRegressor
import joblib


#pandas
import pandas as pd
import math
from math import sqrt
from pandas import Series,DataFrame
import numpy as np
import matplotlib.pyplot as plt
import sys
from time import time
from enum import Enum

import warnings
warnings.filterwarnings('ignore')
from sklearn.ensemble import IsolationForest
from sklearn.covariance import EllipticEnvelope
from sklearn.neighbors import LocalOutlierFactor

def adj_r2_score(p,y,yhat):
    adj = 1 - float(len(y)-1)/(len(y)-p-1)*(1 - r2_score(y,yhat))
    return adj

def mean_absolute_percentage_error(y_true, y_pred): 
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

def mean_absolute_error(y_true, y_pred): 
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs(y_true - y_pred))

def report(results, n_top=3):
    for i in range(1, n_top + 1):
        candidates = np.flatnonzero(results['rank_test_score'] == i)
        for candidate in candidates:
            print("Model with rank: {0}".format(i))
            print("Mean validation score: {0:.3f} (std: {1:.3f})".format(
                  results['mean_test_score'][candidate],
                  results['std_test_score'][candidate]))
            print("Parameters: {0}".format(results['params'][candidate]))
            print("")

class predictY(Enum):
    CATALOGUE = 1
    CART = 2
    WEB = 3
    SHIPPING = 4

class X(Enum):
    PODCPU = 1
    PODCPU_VMCPU = 2
    PODCPU_VMCPI = 3

import matplotlib.pylab as pylab
import matplotlib as mpl
mpl.rcParams.update(mpl.rcParamsDefault)
mpl.rcParams['pdf.fonttype'] = 42
params = {'legend.fontsize': 'x-large',
         'figure.figsize': (4, 3),
         #'font.family': 'serif',
         'font.sans-serif': 'Arial', 
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         #'axes.labelweight':'bold', 
         'xtick.labelsize':'x-large',
         'ytick.labelsize':'x-large'}
pylab.rcParams.update(params)

latency_metrics = ["ratings_95th_latency", "cart_95th_latency",  "user_95th_latency",
                  "payment_95th_latency", "catalogue_95th_latency", "ratings_95th_latency",
                  "shipping_95th_latency", "web_95th_latency", "mysql_95th_latency",
                 "mongodb_95th_latency", "dispatch_95th_latency", "redis_95th_latency",
                 "rabbitmq_95th_latency"]

filter_metrics = [
        'cart_cont_cpu5s_avg','web_cont_cpu5s_avg','catalogue_cont_cpu5s_avg', 'ratings_cont_cpu5s_avg',
        'mysql_cont_cpu5s_avg', 'mongodb_cont_cpu5s_avg', 'dispatch_cont_cpu5s_avg', 'payment_cont_cpu5s_avg',
        'rabbitmq_cont_cpu5s_avg', 'user_cont_cpu5s_avg','shipping_cont_cpu5s_avg','redis_cont_cpu5s_avg',

        'catalogue_vm_netW', 'ratings_vm_netW', 'cart_vm_netW', 'web_vm_netW',
        'mysql_vm_netW','mongodb_vm_netW', 'dispatch_vm_netW', 'payment_vm_netW',
        'rabbitmq_vm_netW','shipping_vm_netW','redis_vm_netW', 'user_vm_netW',

        'catalogue_vm_netR', 'ratings_vm_netR', 'cart_vm_netR', 'web_vm_netR',
        'mysql_vm_netR','mongodb_vm_netR', 'dispatch_vm_netR', 'payment_vm_netR',
        'rabbitmq_vm_netR','shipping_vm_netR','redis_vm_netR', 'user_vm_netR',

        'mysql_vm_util', 'ratings_vm_util','cart_vm_util','catalogue_vm_util',
        'web_vm_util','mongodb_vm_util', 'dispatch_vm_util', 'payment_vm_util',
        'rabbitmq_vm_util','shipping_vm_util', 'redis_vm_util', 'user_vm_util',

        'user_perf_cpi', 'redis_perf_cpi','mysql_perf_cpi', 'ratings_perf_cpi',
        'cart_perf_cpi','catalogue_perf_cpi','web_perf_cpi','mongodb_perf_cpi',
        'dispatch_perf_cpi', 'payment_perf_cpi','rabbitmq_perf_cpi','shipping_perf_cpi',


        'redis_perf_llc', 'user_perf_llc','mysql_perf_llc', 'ratings_perf_llc',
        'cart_perf_llc','catalogue_perf_llc','web_perf_llc','mongodb_perf_llc',
        'dispatch_perf_llc', 'payment_perf_llc','rabbitmq_perf_llc','shipping_perf_llc',

        'cart_cont_netW5s_avg', 'web_cont_netW5s_avg','ratings_cont_netW5s_avg','mysql_cont_netW5s_avg',
        'catalogue_cont_netW5s_avg','mongodb_cont_netW5s_avg', 'dispatch_cont_netW5s_avg', 'payment_cont_netW5s_avg',
        'rabbitmq_cont_netW5s_avg','shipping_cont_netW5s_avg','redis_cont_netW5s_avg', 'user_cont_netW5s_avg',
    
        'cart_cont_netR5s_avg', 'web_cont_netR5s_avg','ratings_cont_netR5s_avg','mysql_cont_netR5s_avg',
        'catalogue_cont_netR5s_avg','mongodb_cont_netR5s_avg', 'dispatch_cont_netR5s_avg', 'payment_cont_netR5s_avg',
        'rabbitmq_cont_netR5s_avg','shipping_cont_netR5s_avg','redis_cont_netR5s_avg', 'user_cont_netR5s_avg',
    
        'cart_cont_memR5s_avg', 'web_cont_memR5s_avg','ratings_cont_memR5s_avg','mysql_cont_memR5s_avg',
        'catalogue_cont_memR5s_avg','mongodb_cont_memR5s_avg', 'dispatch_cont_memR5s_avg', 'payment_cont_memR5s_avg',
        'rabbitmq_cont_memR5s_avg','shipping_cont_memR5s_avg','redis_cont_memR5s_avg', 'user_cont_memR5s_avg',
    
            'cart_cont_memW5s_avg', 'web_cont_memW5s_avg','ratings_cont_memW5s_avg','mysql_cont_memW5s_avg',
        'catalogue_cont_memW5s_avg','mongodb_cont_memW5s_avg', 'dispatch_cont_memW5s_avg', 'payment_cont_memW5s_avg',
        'rabbitmq_cont_memW5s_avg','shipping_cont_memW5s_avg','redis_cont_memW5s_avg', 'user_cont_memW5s_avg',
]

# In[120]:


hidden_layer_sizes=(5,3, 3)

def training_by_different_model(dfnorm, y, name):
    svr = svm.SVR(kernel='linear')
    lr = LinearRegression()
    dt = DecisionTreeRegressor()
    rf = RandomForestRegressor()
    #kernel = C(1.0, (1e-3, 1e3)) * RBF(10, (1e-2, 1e2)) + WhiteKernel(noise_level=0.5)
    #kernel = 0.5**2 * RationalQuadratic(length_scale=1.0) + WhiteKernel(noise_level=0.1)
    #kernel = 0.75**2 * RationalQuadratic(length_scale=1.0) + WhiteKernel(noise_level=0.1)
    kernel =  50.0**2 * RBF(length_scale=50.0) + 0.5**2 * RationalQuadratic(length_scale=1.0)# + WhiteKernel(noise_level=0.1)
    gp = GaussianProcessRegressor(kernel=kernel,n_restarts_optimizer=10,normalize_y=True)

    nn = MLPRegressor(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=hidden_layer_sizes, random_state=1, max_iter=1000, activation='relu',learning_rate_init='0.01',momentum=0.9)

    predicted_lr = cross_val_predict(lr, dfnorm, y, cv=10)
    predicted_svr = cross_val_predict(svr, dfnorm, y, cv=10)
    predicted_dt = cross_val_predict(dt, dfnorm, y, cv=10)
    predicted_rf = cross_val_predict(rf, dfnorm, y, cv=10)
    predicted_gp = cross_val_predict(gp, dfnorm, y, cv=10)
    #predicted_nn = cross_val_predict(nn, dfnorm, y, cv=10)
    predicted_nn = 100
    # do not run until the previous step finishes execution. gaussian process and neural network cross validation takes some time.

    joblib.dump(gp, 'models/gp_{}.model'.format(name)) 

    print("\tLR\tSVR\tDT\tRF\tNN\tGP")
    cv_lr = mean_absolute_error(y, predicted_lr)
    cv_svr = mean_absolute_error(y, predicted_svr)
    cv_dt = mean_absolute_error(y, predicted_dt)
    cv_rf = mean_absolute_error(y, predicted_rf)
    cv_nn = mean_absolute_error(y, predicted_nn)
    cv_gp = mean_absolute_error(y, predicted_gp)
    cv_gp = 0
    
    print("mae\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f" % (cv_lr, cv_svr, cv_dt, cv_rf, cv_nn, cv_gp))
    cv_lr = mean_absolute_percentage_error(y, predicted_lr)
    cv_svr = mean_absolute_percentage_error(y, predicted_svr)
    cv_dt = mean_absolute_percentage_error(y, predicted_dt)
    cv_rf = mean_absolute_percentage_error(y, predicted_rf)
    cv_nn = mean_absolute_percentage_error(y, predicted_nn)
    cv_gp = mean_absolute_percentage_error(y, predicted_gp)
    ##cv_gp = 0
    print("mape\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f" % (cv_lr, cv_svr, cv_dt, cv_rf, cv_nn, cv_gp))
    return 
    cv_lr = sqrt(mean_squared_error(y, predicted_lr))
    cv_svr = sqrt(mean_squared_error(y, predicted_svr))
    cv_dt = sqrt(mean_squared_error(y, predicted_dt))
    cv_rf = sqrt(mean_squared_error(y, predicted_rf))
    cv_nn = sqrt(mean_squared_error(y, predicted_nn))
    cv_gp = sqrt(mean_squared_error(y, predicted_gp))
    #cv_gp = 0

    print("rmse\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f" % (cv_lr, cv_svr, cv_dt, cv_rf, cv_nn, cv_gp))


    print("r2\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f" % (r2_score(y, predicted_lr), r2_score(y, predicted_svr), r2_score(y, predicted_dt), r2_score(y, predicted_rf), r2_score(y, predicted_nn), r2_score(y, predicted_gp)))
    #print("r2\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f" % (adj_r2_score(p, y, predicted_lr), r2_score(y, predicted_svr), r2_score(y, predicted_dt), r2_score(y, predicted_rf), r2_score(y, predicted_nn)))
    
    fig, ax = plt.subplots()
    #plt.title('Cross-validated predictions of 95th percentile latency (ms)')
    ax.scatter(y, predicted_gp, edgecolors=(0, 0, 0))
    ax.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=4)
    ax.set_xlabel('Measured tail latency (ms)')
    ax.set_ylabel('Predicted tail latency (ms)')
    #ax.set_xlim(50,500)
    #ax.set_ylim(50,500)
    plt.grid(True)
    #plt.xticks(np.arange(0, 501, step=100))
    #plt.yticks(np.arange(0, 501, step=100))
    plt.tight_layout()
    plt.show()
    return 
    fig, ax = plt.subplots()
    #plt.title('Cross-validated predictions of 95th percentile latency (ms)')
    ax.scatter(y, predicted_nn, edgecolors=(0, 0, 0))
    ax.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=4)
    ax.set_xlabel('Measured tail latency (ms)')
    ax.set_ylabel('Predicted tail latency (ms)')
    #ax.set_xlim(50,500)
    #ax.set_ylim(50,500)
    plt.grid(True)
    #plt.xticks(np.arange(0, 501, step=100))
    #plt.yticks(np.arange(0, 501, step=100))
    plt.tight_layout()
    plt.show()


# In[126]:


# feature selection
def FeatureSelection(rdf, y1, alpha):
    #feature importance
    #rlasso = RandomizedLasso(alpha=0.025, selection_threshold=0.2)
    reg = linear_model.LassoLars(alpha=alpha)
    reg.fit(rdf, y1)
    print(reg.coef_)


    ret = []
    column = rdf.columns.tolist()
    for i in range(len(reg.coef_)):
        if abs(reg.coef_[i]) > 0.01:
            ret.append(column[i])
    print("feature selection length is ", len(ret))
    return ret

# In[ ]:


rdf_all = pd.read_csv('../training_data/bigtable.csv')

hidden_layer_sizes=(5,3, 3)
def rdf_filter(rdf):
    
    # outlier removal
    rdf = rdf[rdf.test_id.str.contains('.*_[0-6]_*')]
    new = rdf["test_id"].str.split("_", n = 4, expand = True)
    rdf = rdf.drop(columns=['test_id'])
    rdf['thread'] = new[2]
    rdf = rdf.fillna(0)
    rdf = rdf.dropna()
    rdf = rdf.sample(3384)
    #subset=filter_metrics)
    return rdf

def OutLierRemove(X_train, y_train):
    #iso = IsolationForest(contamination=0.2)
    #yhat = iso.fit_predict(X_train)

    #ee = EllipticEnvelope(contamination=0.01)
    #yhat = ee.fit_predict(X_train)

    lof = LocalOutlierFactor(contamination=0.25)
    yhat = lof.fit_predict(X_train)
    mask = yhat != -1
    X_train, y_train = X_train[mask], y_train[mask]
    return X_train, y_train


rdf_all = rdf_filter(rdf_all)

caseY = predictY.CATALOGUE
#caseY = predictY.WEB
#caseY = predictY.CART
#caseY = predictY.SHIPPING

#y  = rdf.catalogue_95th_latency

predict_list_y = ["catalogue_95th_latency", "user_95th_latency","cart_95th_latency", "ratings_95th_latency", "payment_95th_latency",]

# catalogue use catalogue/catagories/ 
# cart use all cart data

#predict_list_y = ["cart_95th_latency",
#                   "ratings_95th_latency"]


print(rdf_all.shape)

hidden_layer_sizes=(5,3, 3)

for workflow in predict_list_y:
    #print("training ", locals()[y])
    #outlier removing 

    X = rdf_all.drop(latency_metrics, axis=1)
    y = rdf_all[workflow]
    print(X.columns)

    print(X.shape)
    X, y = OutLierRemove(X, y)
    
    # feature selection
    feature_selected =FeatureSelection(X, y, 0.1)
    X = X[feature_selected]
    X= X[y > 0]
    y = y[y > 0]
    print(X.shape, y.shape)
    # standard scaler
    scaler = StandardScaler()
    dfnorm = scaler.fit_transform(X)
   
    # training
    name = workflow.split("_")[0]
    training_by_different_model(dfnorm, y, name)

    joblib.dump(scaler, 'models/scaler_{}.sav'.format(name))
