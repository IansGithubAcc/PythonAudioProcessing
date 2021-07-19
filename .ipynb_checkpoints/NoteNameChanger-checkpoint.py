# Changing the note names to midi number
from pandas import read_csv
import glob
import os

vels = 'loud','med','soft'

for k in range(1,3):
    names = read_csv('midi_nr_names.csv').iloc[:,3]
    index = read_csv('midi_nr_names.csv').iloc[:,0]
    for i in range(len(names)):
        if (type(names[i]) == str):
            if (len(names[i])>2):
                names[i] = names[i][-3:]
    files = glob.glob('./bigcat UoIMIS Piano samples/piano '+vels[k]+'/*.wav')
    table = []
    for i in range(len(files)):
        for j in range(len(names)):
            if (type(names[j]) == str):
                if (names[j] in files[i]):
                    table.append((index[j], files[i]))
    for i in range(len(table)):
        os.rename(table[i][1],'./bigcat UoIMIS Piano samples/piano '+vels[k]+'/'+str(table[i][0])+'.wav')