"""
Copyright 2020 Arm Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

SPDX-License-Identifier: Apache-2.0
"""
import matplotlib.pyplot as plt
import numpy as np
import csv
import sys

file = open(sys.argv[1],'r')
reader = csv.reader(file,delimiter=',')
ncol = len(next(reader))
file.seek(0)

data = np.loadtxt(sys.argv[1], delimiter=',', skiprows = 1, usecols = range(1,ncol))

with open(sys.argv[1]) as csvFile:
    reader = csv.reader(csvFile)
    field_names_list = next(reader)
    field_names_list.pop(0)


X = np.arange(ncol-1)
fig, ax = plt.subplots()
ax.bar(X + 0.00, data[0], color = 'b', width = 0.25)
ax.bar(X + 0.25, data[1], color = 'g', width = 0.25)
ax.bar(X + 0.50, data[2], color = 'r', width = 0.25)



ax.set_xticks(X + 0.25 / 2)
ax.set_ylabel('Number of AVX instructions')
ax.set_title('AVX INSTRUCTIONS CHART REPRESENTATION')
ax.set_xticklabels(field_names_list)
ax.legend(labels = ('AVX_256', 'AVX_512', 'TOTAL_AVX'), loc = 'upper left') 



plt.show()
