import numpy as np
import pandas as pd
import math
from sklearn.utils import shuffle
from sklearn.linear_model import Ridge
from numpy import nan as na
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
#df = pd.read_csv('Train.csv')
def generate_features(df):
    df['percent_change_24h']=df['percent_change_24h']/100.0
    df['p24'] = df.open * ((df.percent_change_24h/24)+1) # prediction using 24 hour value
    df.market_cap=df.market_cap/1000000000.0
    df.market_cap_global=df.market_cap_global/1000000000.0
    df['mid'] = (df['high'] * 0.5) + (df['low']* 0.5) 
    df['mo'] = df.mid / df.open # MO IS MID DIV BY OPEN
    df['ho'] = df.high / df.open
    df['mr'] = df.market_cap / df.market_cap_global # MR IS MARKET RATIO
    df['meanmo'] =  df[['mid','open']].mean(axis=1) # MEAN OF MID AND OPEN
    df['predmr'] = df.open * df.mr
    df['predmeanmo'] = df.open * df.meanmo
    df['e'] = (df.mid>df.open).astype('int') # MID GREATER THAN OPEN?
    df.fillna(0, inplace=True)
    return df
#train_df = generate_features(df)
#train_df = train_df[train_df['close'].notna()]
#train_df = train_df[train_df.close <= train_df.high]
#train_df = train_df[train_df.close >= train_df.low]
#cols =['open', 'predmeanmo', 'market_cap_global', 'e','percent_change_24h' ,'p24' ,'ho' ,'mo' ,'mid', 'market_cap', 'predmr' ,'mr'] 
#pf = PolynomialFeatures(degree = 2, include_bias = False, interaction_only = False)
#sc = StandardScaler()
#model = Ridge(alpha=0, copy_X=True, fit_intercept=True, max_iter=None, normalize=False,    random_state=None, solver='auto', tol=0.001)
#model.fit(sc.fit_transform(pf.fit_transform(train_df[cols])),train_df.close)   
#import pickle
#pickle_out = open("predictor.pkl","wb")
#pickle.dump(model, pickle_out)
#pickle_out.close()
def clip_prediction(test_df):
    test_df.pred[(test_df.pred<test_df.low)] = test_df.low
    test_df.pred[(test_df.pred>test_df.high)] = test_df.high
    test_df.pred[(test_df.open<=0)&(test_df.high<=0)&(test_df.low<=0)] = 0
    return test_df