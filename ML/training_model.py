from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC, LinearSVC
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import cross_val_predict,cross_validate, RandomizedSearchCV, GridSearchCV, train_test_split, cross_val_score
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

# In[120]:


hidden_layer_sizes=(5,3, 3)

def training_by_different_model(dfnorm, y, name):
    svr = svm.SVR(kernel='linear')
    lr = LinearRegression()
    dt = DecisionTreeRegressor()
    rf = RandomForestRegressor()
    #kernel = C(1.0, (1e-3, 1e3)) * RBF(10, (1e-2, 1e2)) + WhiteKernel(noise_level=0.5)
    kernel =  50.0**2 * RBF(length_scale=50.0) + 0.5**2 * RationalQuadratic(length_scale=1.0) + WhiteKernel(noise_level=0.1)
    gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10,normalize_y=True)

    nn = MLPRegressor(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=hidden_layer_sizes, random_state=1, max_iter=1000, activation='relu',learning_rate_init='0.01',momentum=0.9)

    cv = 3
    n_jobs=3
    predicted_lr = cross_val_predict(lr, dfnorm, y, cv=cv,n_jobs=n_jobs )
    predicted_svr = cross_val_predict(svr, dfnorm,y,cv=cv,n_jobs=n_jobs )
    predicted_dt = cross_val_predict(dt, dfnorm, y, cv=cv,n_jobs=n_jobs )
    predicted_rf = cross_val_predict(rf, dfnorm, y, cv=cv,n_jobs=n_jobs )
    predicted_gp = cross_val_predict(gp, dfnorm, y, cv=cv,n_jobs=n_jobs )
    predicted_nn = cross_val_predict(nn, dfnorm, y, cv=cv,n_jobs=n_jobs )
    #predicted_nn = 100
    # do not run until the previous step finishes execution. gaussian process and neural network cross validation takes some time.

    result = cross_validate(gp, dfnorm, y,n_jobs=n_jobs, cv=cv, return_estimator=True)
    for i, score in enumerate(result["test_score"]):
        if score == max(result["test_score"]):
            gp = result["estimator"][i]
        
    print(gp)

    joblib.dump(gp, 'models/gp_{}.model'.format(name)) 

    print("\tLR\tSVR\tDT\tRF\tNN\tGP")
    cv_lr = mean_absolute_error(y, predicted_lr)
    cv_svr = mean_absolute_error(y, predicted_svr)
    cv_dt = mean_absolute_error(y, predicted_dt)
    cv_rf = mean_absolute_error(y, predicted_rf)
    cv_nn = mean_absolute_error(y, predicted_nn)
    cv_gp = mean_absolute_error(y, predicted_gp)
    
    print("mae\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f" % (cv_lr, cv_svr, cv_dt, cv_rf, cv_nn, cv_gp))
    cv_lr = mean_absolute_percentage_error(y, predicted_lr)
    cv_svr = mean_absolute_percentage_error(y, predicted_svr)
    cv_dt = mean_absolute_percentage_error(y, predicted_dt)
    cv_rf = mean_absolute_percentage_error(y, predicted_rf)
    cv_nn = mean_absolute_percentage_error(y, predicted_nn)
    cv_gp = mean_absolute_percentage_error(y, predicted_gp)
    ##cv_gp = 0
    print("mape\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f" % (cv_lr, cv_svr, cv_dt, cv_rf, cv_nn, cv_gp))
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
    return 
    
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
def FeatureSelection(rdf, y1, alpha, name):
    #feature importance
    #rlasso = RandomizedLasso(alpha=0.025, selection_threshold=0.2)
    reg = linear_model.Lasso(alpha=alpha)
    reg.fit(rdf, y1)
    #print(reg.coef_)


    ret = []
    column = rdf.columns.tolist()
    for i in range(len(reg.coef_)):
        if abs(reg.coef_[i]) > 0.05:
            ret.append(column[i])

    print("feature selection length is ", len(ret), ret)
    with open("models/selected_feature_{}.txt".format(name), "w") as outfile:
        outfile.write("\n".join(ret))

    data = [line.strip() for line in open("models/selected_feature_{}.txt".format(name), 'r')]
    return ret

# In[ ]:


rdf_all = pd.read_csv('../training_data/bigtable.csv')

hidden_layer_sizes=(5,3, 3)
def rdf_filter(rdf):
    
    # outlier removal
    rdf = rdf[~rdf.test_id.str.contains('Jun13')]
    new = rdf["test_id"].str.split("_", n = 4, expand = True)
    rdf = rdf.drop(columns=['test_id'])
    rdf['thread'] = new[2]
    rdf = rdf.fillna(0)
    rdf = rdf.dropna()
    #subset=filter_metrics)
    return rdf

def OutLierRemove(X_train, y_train):
    #iso = IsolationForest(contamination=0.1)
    #yhat = iso.fit_predict(X_train)

    #ee = EllipticEnvelope(contamination=0.01)
    #yhat = ee.fit_predict(X_train)

    lof = LocalOutlierFactor(contamination=0.05)
    yhat = lof.fit_predict(X_train)
    mask = yhat != -1
    X_train, y_train = X_train[mask], y_train[mask]
    X_train = X_train[np.abs(y_train - y_train.mean()) <= (2*y_train.std())]
    y_train = y_train[np.abs(y_train - y_train.mean()) <= (2*y_train.std())]
    X_train = X_train[y_train<1000]
    y_train = y_train[y_train<1000]
    return X_train, y_train




def filter_new(rdf, workflow):
    columns = rdf.columns.tolist()
    ret = ["thread"]
    
    for col in columns:
        pod = col.split("_")[0]
        if pod in workflow:
            ret.append(col)    
    return rdf[ret]

pod_list = ["ratings", "cart",  "user","payment", "catalogue", "shipping", "web", "mysql","mongodb",
            "dispatch", "redis","rabbitmq",]
no_metrics = []
for name in ["_workload_fail"]:
    no_metrics += [ pod + name for pod in pod_list] 

workflow_pod = [["catalogue", "mongodb", "web", "ratings"],
    ["web", "payment", "dispatch", "cart", "rabbitmq"],
    ["web", "payment", "user", "mongodb", ],
    ["web", "cart", "mysql", "shipping"],
    ["catalogue", "mysql", "web", "ratings"],
    ["web", "payment", "cart", "redis", "shipping"]]


rdf_all = rdf_filter(rdf_all)


predict_list_y = [ "cart_95th_latency",  "catalogue_95th_latency","payment_95th_latency","ratings_95th_latency", "user_95th_latency",
 "shipping_95th_latency", ]


print(rdf_all.shape)

hidden_layer_sizes=(5,3, 3)

for i, workflow in enumerate(predict_list_y):
    #print("training ", locals()[y])
    #outlier removing 

    name = workflow.split("_")[0]
    

    
    X1 = rdf_all.drop(latency_metrics+no_metrics, axis=1)
    
    X1 = filter_new(X1, workflow_pod[i])
    
    
    y = rdf_all[workflow]

    X = X1
    X, y = OutLierRemove(X, y)

    X = X[FeatureSelection(X, y, 0.1, name,)]
    # filter some bad y value
    X = X[y>0]
    y = y[y>0]

    # standard scaler
    scaler = StandardScaler()
    scaler.fit(X)
    print(scaler.mean_, scaler.var_, )
    X = scaler.transform(X)
   
    # training
    training_by_different_model(X, y, name)

    joblib.dump(scaler, 'models/scaler_{}.sav'.format(name))
