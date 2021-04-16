import numpy as np
import matplotlib.pyplot as plt
import json
import scipy.stats as stats
import pandas as pd
import statsmodels.api as sm
import os

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.utils import resample
from sklearn.model_selection import cross_val_score
from sklearn.metrics import confusion_matrix
'''
LOCATORS' POSITION:
           X      Y      Z
LAUNCH1:  3.80   3.15   1.20
LAUNCH2:  0.15   1.87   1.20
LAUNCH3:  4.05   0.65   1.20
'''

'''
BUILDING THE DATASET
'''

#create dataset
data = pd.DataFrame(columns=['Anchor_name', 'RSSI', 'distance'])

# Reading gathered data files
files_list = sorted(list(filter(lambda x: ("detectedDevs" in x), os.listdir("/home/aaron/Trabajo/interaction-tracker-updated/PositionTracker/src/Data_Collection/Offline/3anchor_1movil/proximity"))))

#concatenate file's data to build the dataset
for file in files_list:
    filename_split = file.split('_')
    distance = float(filename_split[2]) / 100
    df = pd.read_json('/home/aaron/Trabajo/interaction-tracker-updated/PositionTracker/src/Data_Collection/Offline/3anchor_1movil/proximity/'+file)

    df.drop(['devname'], axis=1, inplace=True)
    df.rename(columns={'launchpadId':'Anchor_name'}, inplace=True)
    df.insert(loc=2, column='distance', value=np.repeat(distance, df.shape[0]))

    data = data.append(df)

data.reset_index(drop=True, inplace=True)
print(data.to_string())

'''
PREPROCESSING
'''
#create the column "dist_<_1m" to allow performing classification
data.insert(3, 'dist_<_1m', data['distance'].apply(lambda dist: 1 if dist < 1.0 else 0))

print(data['dist_<_1m'].value_counts())

#imbalanced dataset. down-sample majority class
data_maj = data[data['dist_<_1m'] == 1]
data_min = data[data['dist_<_1m'] == 0]

data_maj_downsampled = resample(data_maj, replace=False, n_samples=data_min.shape[0], random_state=176341)

data = pd.concat([data_maj_downsampled, data_min])
print(data)
print(data['dist_<_1m'].value_counts())

#show boxplot

#Mixing data from all anchors
fig, ax = plt.subplots()
data.boxplot(column='RSSI', by='distance', ax=ax)
ax.set_title("Mixed data")
plt.show()

#boxplot for each anchor
fig, ax = plt.subplots(1,3)
anchor_names_list = data['Anchor_name'].unique()

data[data['Anchor_name'] == anchor_names_list[0]].boxplot(column='RSSI', by='distance', ax=ax[0])
data[data['Anchor_name'] == anchor_names_list[1]].boxplot(column='RSSI', by='distance', ax=ax[1])
data[data['Anchor_name'] == anchor_names_list[2]].boxplot(column='RSSI', by='distance', ax=ax[2])
ax[0].set_title(anchor_names_list[0])
ax[1].set_title(anchor_names_list[1])
ax[2].set_title(anchor_names_list[2])

plt.show()

#Remove distance=0 outliers
indexnames = data[(data.distance == 0) & (data.RSSI < -35)].index
data.drop(indexnames, inplace=True, axis=0)

'''
DATA PROCESSING
'''

#split in train and test data
train, test = train_test_split(data, test_size=data.shape[0]//3)

#apply a gaussian naive-bayes
NB_model = GaussianNB()
NB_model.fit(np.array(train['RSSI']).reshape(-1,1), train['dist_<_1m'])

#using cross validation
NB_model_cv = GaussianNB()
scores = cross_val_score(NB_model_cv, np.array(train['RSSI']).reshape(-1,1), train['dist_<_1m'], cv=10)

#compute confusion matrix

y_test_pred = NB_model.predict(np.array(test['RSSI']).reshape(-1,1))
print(confusion_matrix(test['dist_<_1m'], y_test_pred))

print(scores.mean(), scores.std())
print("----------------------------------------------------------------------------------------------------------")
#print(data.sort_values('RSSI',ascending=False).to_string())


