### Inporting required packages
from apscheduler.schedulers.background import BackgroundScheduler
import time
import numpy as np
import pygame
from datetime import datetime, timedelta
from pandas import read_csv

### Loading variables from input.txt
with open(r'input.txt') as f:
    lines = f.read().splitlines()

instruments = []
instrument_paths = []
Velocity_subfolders = []
Velocity_bounds = []
midi_paths = []
Note_file_types = []

for i in range(len(lines)):
    if (lines[i][:11] == 'Instruments'):
        n_instruments = int(lines[i][11:])    
    if (lines[i][:4] == 'Name'):
        instruments.append(lines[i][22:])
    if (lines[i][:15] == 'Instrument_path'):
        instrument_paths.append(lines[i][22:])
    if (lines[i][:15] == 'Velocity_bounds'):
        Velocity_bounds.append(lines[i][22:])
    if (lines[i][:19] == 'Velocity_subfolders'):
        Velocity_subfolders.append(lines[i][22:])
    if (lines[i][:9] == 'Midi_path'):
        midi_paths.append(lines[i][22:])
    if (lines[i][:len('Note_file_type')] == 'Note_file_type'):
        Note_file_types.append(lines[i][22:])
        
for i in range(n_instruments):
    Velocity_subfolders[i] = Velocity_subfolders[i].split(", ")
    Velocity_bounds[i] = np.float_(Velocity_bounds[i].split(", "))


### Loading functions
def note_path(midi_nr, vel, instrument):
    for i in range(len(Velocity_bounds[instrument])-1):
        if (midi_nr <= 108 and midi_nr >= 23):
            if (vel <= Velocity_bounds[instrument][i+1]):
                return instrument_paths[instrument]+Velocity_subfolders[instrument][i]+"/" + str(midi_nr) + "." + Note_file_types[instrument]
        else: 
            print("warning note missing")
            return -99

def player(Note, Volume,n):
    if (Note!=-99):
        channel = pygame.mixer.Channel(n)
        effect = pygame.mixer.Sound(Note)
        channel.set_volume(Volume)
        channel.play(effect)
    return 

def make_recipe(path, echo_time = None, play_all_instruments = False,BPM_override = None):
    song = read_csv(path, skipinitialspace=True,usecols=np.arange(6),header=None,skiprows=0, encoding='ISO-8859-1')
    if (BPM_override != None):
        BPS = BPM_override/60
    else:
        BPS = 1e6/float(song[np.logical_or(song.iloc[:,2] == " Tempo", song.iloc[:,2] == "Tempo")].iloc[0,3])
    print("BPM = "+str(round(BPS*60,1)))
    multi = (read_csv(path,usecols=np.arange(6),skiprows = 0,header=None,nrows=1).iloc[0,-1]*BPS)

    instruments = song[song.iloc[:,2] == "Program_c"] # reading instrument types
    i_play = [] # list of pianno tracks
    for i in range(len(instruments)):
        if (float(instruments.iloc[i,4]) <= 7):
            i_play.append(instruments.iloc[i,0])

    if (play_all_instruments==False):
        song = song[[song.iloc[i,0] in i_play for i in range(len(song))]] # Selecting only active instruments
        print("playing "+str(len(i_play))+" out of "+str(len(instruments))+" instruments")
    else:
        print("playing "+str(len(instruments))+" out of "+str(len(instruments))+" instruments")
    song = song[np.logical_or(song.iloc[:,2]=="Note_on_c", song.iloc[:,2]=="Note_off_c")] # Selecting only playing commands
    return song, multi

def play_recipe(recipe,vol=1,instrument=0):#                         Change Volume!!!
    song, multi = recipe
    pygame.mixer.init()
    pygame.init()

    scheduler = BackgroundScheduler()
    timenow = datetime.now()

    channel_note = [[None,None],[None,None]]
    free_channels = list(np.arange(8))

    for i in range(len(song)):
        if any(np.array(channel_note)[:,1] == int(song.iloc[i,4])):
            free_channels.insert(0,np.array(channel_note)[np.array(channel_note)[:,1] == int(song.iloc[i,4])][0][0])
            channel_note.remove(channel_note[int(np.where(np.array(channel_note)[:,1] == int(song.iloc[i,4]))[0])])
        if (len(free_channels) == 0):
            free_channels.append(channel_note[2][0])
        channel_note.append([int(free_channels[0]),int(song.iloc[i,4])])

        if (echo_time!=None):
            if (int(song.iloc[i,5])!=0):
                scheduler.add_job(player, 'date',[note_path(int(song.iloc[i,4]),int(song.iloc[i,5]),instrument),vol,free_channels[0]], run_date=timenow + timedelta(seconds=int(song.iloc[i,1])/multi),misfire_grace_time=3,max_instances=8)
            else:
                scheduler.add_job(player, 'date',[note_path(int(song.iloc[i,4]),int(song.iloc[i,5]),instrument),vol,free_channels[0]], run_date=timenow + timedelta(seconds=int(song.iloc[i,1])/multi+echo_time),misfire_grace_time=3,max_instances=8)
        else:
            if (int(song.iloc[i,5])!=0):
                scheduler.add_job(player, 'date',[note_path(int(song.iloc[i,4]),int(song.iloc[i,5]),instrument),vol,free_channels[0]], run_date=timenow + timedelta(seconds=int(song.iloc[i,1])/multi),misfire_grace_time=3,max_instances=8)
        free_channels = free_channels[1:]
    scheduler.start()
    input('Press enter to stop: ')
    scheduler.shutdown()

def true_or_false(string):
    if (string=="Yes" or string=="yes" or string=="Y" or string=="y"):
        return True
    elif (string=="No" or string=="no" or string=="n" or string=="N"):
        return False
    else:
        print("try again")
        true_or_false(input())
    
echo_time = None # how long notes agiare played. Use None for as long as possible
instrument = 0

print('playing '+instruments[instrument])
for i in range(len(midi_paths)):
    play_all_instruments = true_or_false(input("Play all instruments? y/n")) # plays instrument whether it is classified as pianno or not
    play_recipe(make_recipe(midi_paths[i],echo_time,play_all_instruments),vol=1, instrument=instrument)
