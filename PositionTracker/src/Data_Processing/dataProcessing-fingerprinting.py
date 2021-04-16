import numpy as np
import matplotlib.pyplot as plt
import json
import scipy.stats as stats
import pandas as pd
import statsmodels.api as sm
import os

'''
LOCATORS' POSITION:
           X      Y      Z
LAUNCH1:  3.80   3.15   1.20
LAUNCH2:  0.15   1.87   1.20
LAUNCH3:  4.05   0.65   1.20
'''
launch1_pos = (3.8, 3.15)
launch2_pos = (0.15, 1.87)
launch3_pos = (4.05, 0.65)

# array of 2-tuples (x, y).  Z coord is 0.60, the same for all positions
grid_positions = [(0, 0), (0, 1.25), (1.2, 0), (1.2, 1.25), (1.2, 2.5), (2.4, 0), (2.4, 1.25), (2.4, 2.5), (3.6, 0),
                  (3.6, 1.25), (3.6, 2.5)]

files_list = sorted(list(filter(lambda x: ("detectedDevs" in x), os.listdir("../Data_Collection/3LP_1M/fingerprinting"))))
print(files_list)

# it holds a dictionary for each
array_of_dict = []

# for each file
for file in files_list:

    filename_split = file.split('_')

    tag_pos_x = float(filename_split[3])
    tag_pos_y = float(filename_split[5])
    locator_name = filename_split[1]

    grid_pos_dict = dict()
    grid_pos_dict["tag_pos"] = (tag_pos_x, tag_pos_y)
    grid_pos_dict["locator"] = locator_name

    if locator_name == "LAUNCH1":
        # Calculate distance from tag_pos to LAUNCH1 locator
        grid_pos_dict["dist_to_loc"] = np.sqrt(pow(launch1_pos[0] - tag_pos_x, 2) + pow(launch1_pos[1] - tag_pos_y, 2) + pow(1.2 - 0.6, 2))
    elif locator_name == "LAUNCH2":
        # Calculate distance from tag_pos to LAUNCH2 locator
        grid_pos_dict["dist_to_loc"] = np.sqrt(pow(launch2_pos[0] - tag_pos_x, 2) + pow(launch2_pos[1] - tag_pos_y, 2) + pow(1.2 - 0.6, 2))
    else:
        # Calculate distance from tag_pos to LAUNCH3 locator
        grid_pos_dict["dist_to_loc"] = np.sqrt(pow(launch3_pos[0] - tag_pos_x, 2) + pow(launch3_pos[1] - tag_pos_y, 2) + pow(1.2 - 0.6, 2))

    # Get the RSSI values
    with open(f'../Data_Collection/3LP_1M/{file}', 'r') as file:
        python_obj = json.load(file)
        grid_pos_dict["RSSI_list"] = [int(sample['RSSI']) for sample in python_obj]

    array_of_dict.append(grid_pos_dict)

for elem in sorted(array_of_dict, reverse=True, key=(lambda x: x['dist_to_loc'])):
    print(elem)

# boxplot por cada LAUNCHPAD

# LAUNCH1
fig, ax = plt.subplots(1,1)
positions_list = [elem['dist_to_loc'] for elem in filter(lambda x: x['locator'] == 'LAUNCH1', sorted(array_of_dict, reverse=False, key=(lambda x: x['dist_to_loc'])))]
ax.set_title("LAUNCH1")
ax.boxplot([elem['RSSI_list'] for elem in filter(lambda x: x['locator'] == 'LAUNCH1', sorted(array_of_dict, reverse=False, key=(lambda x: x['dist_to_loc'])))])
plt.xticks(range(1,len(positions_list)+1), [round(elem,5) for elem in positions_list], rotation='vertical')
ax.set_xlabel("Distancias")
ax.set_ylabel("RSSI")
#plt.show()

#LAUNCH2
fig, ax = plt.subplots(1,1)
ax.set_title("LAUNCH2")
positions_list = [elem['dist_to_loc'] for elem in filter(lambda x: x['locator'] == 'LAUNCH2', sorted(array_of_dict, reverse=False, key=(lambda x: x['dist_to_loc'])))]
ax.boxplot([elem['RSSI_list'] for elem in filter(lambda x: x['locator'] == 'LAUNCH2', sorted(array_of_dict, reverse=False, key=(lambda x: x['dist_to_loc'])))])
plt.xticks(range(1,len(positions_list)+1), [round(elem,5) for elem in positions_list], rotation='vertical')
ax.set_xlabel("Distancias")
ax.set_ylabel("RSSI")
#plt.show()

#LAUNCH3
fig, ax = plt.subplots(1,1)
ax.set_title("LAUNCH3")
positions_list = [elem['dist_to_loc'] for elem in filter(lambda x: x['locator'] == 'LAUNCH3', sorted(array_of_dict, reverse=False, key=(lambda x: x['dist_to_loc'])))]
ax.boxplot([elem['RSSI_list'] for elem in filter(lambda x: x['locator'] == 'LAUNCH3', sorted(array_of_dict, reverse=False, key=(lambda x: x['dist_to_loc'])))])
plt.xticks(range(1,len(positions_list)+1), [round(elem,5) for elem in positions_list], rotation='vertical')
ax.set_xlabel("Distancias")
ax.set_ylabel("RSSI")

plt.show()