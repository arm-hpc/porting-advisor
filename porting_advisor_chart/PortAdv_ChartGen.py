import matplotlib.pyplot as plt
import numpy as np
import csv
import sys

"""calculate number of coloumn for csv file"""
file = open(sys.argv[1], 'r')
reader = csv.reader(file,delimiter=',')
ncol = len(next(reader))
file.seek(0)

"""collect data from csv file for plotting the graph"""
data = np.loadtxt(sys.argv[1], delimiter=',', skiprows = 1, usecols = range(1, ncol))

with open(sys.argv[1]) as csvFile:
    reader = csv.reader(csvFile)
    field_names_list = next(reader)
    field_names_list.pop(0)


"""X is the number of evenly spaced group of AVX intructions for each file"""
X = np.arange(ncol-1)
fig, ax = plt.subplots()

"""Each bar will have a thickness of 0.25 units.
Each bar chart will be shifted 0.25 units from the previous one."""
ax.bar(X + 0.00, data[0], color = 'b', width = 0.25)
ax.bar(X + 0.25, data[1], color = 'g', width = 0.25)
ax.bar(X + 0.50, data[2], color = 'r', width = 0.25)

ax.set_xticks(X + 0.25 / 2) #markers denoting data points on axes
ax.set_ylabel('Number of AVX instructions') #set Y axis label
ax.set_title('AVX INSTRUCTIONS CHART REPRESENTATION')  #set title of the chart
ax.set_xticklabels(field_names_list) #add filenames at xticks marked
ax.legend(labels = ('AVX_256', 'AVX_512', 'TOTAL_AVX'), loc = 'upper left') #add chart legends and set position for it

plt.show()
