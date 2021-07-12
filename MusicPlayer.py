### Inporting required packages
from apscheduler.schedulers.background import BackgroundScheduler
import time
import numpy as np
import pygame
from datetime import datetime, timedelta
from pandas import read_csv

### Loading functions
def note_path(midi_nr, vel):
    levels = "soft","med","loud"
    if (midi_nr <= 108 and midi_nr >= 22):
        if (vel <= 48):
            return "bigcat UoIMIS Piano samples/piano "+levels[0]+"/" + str(midi_nr) + ".wav"
        else: 
            if (vel <= 96):
                return "bigcat UoIMIS Piano samples/piano "+levels[1]+"/" + str(midi_nr) + ".wav"
            else:
                return "bigcat UoIMIS Piano samples/piano "+levels[2]+"/" + str(midi_nr) + ".wav"
    else: 
        print("warning note missing")
        return -99

def note_path_old(midi_nr):
    note_names = np.array(np.loadtxt("test.txt",str))
    midi_nrs = [int(note_names[i][16:18]) for i in range(len(note_names))]
    note_names = [x for _, x in sorted(zip(midi_nrs, note_names))] # sorted note names based on midi index nr
    if (midi_nr-9 < len(note_names)):
        return note_names[midi_nr-9]
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

def play_recipe(recipe,vol=1):
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
                scheduler.add_job(player, 'date',[note_path(int(song.iloc[i,4]),int(song.iloc[i,5])),vol,free_channels[0]], run_date=timenow + timedelta(seconds=int(song.iloc[i,1])/multi),misfire_grace_time=3,max_instances=8)
            else:
                scheduler.add_job(player, 'date',[note_path(int(song.iloc[i,4]),int(song.iloc[i,5])),vol,free_channels[0]], run_date=timenow + timedelta(seconds=int(song.iloc[i,1])/multi+echo_time),misfire_grace_time=3,max_instances=8)
        else:
            if (int(song.iloc[i,5])!=0):
                scheduler.add_job(player, 'date',[note_path(int(song.iloc[i,4]),int(song.iloc[i,5])),vol,free_channels[0]], run_date=timenow + timedelta(seconds=int(song.iloc[i,1])/multi),misfire_grace_time=3,max_instances=8)
        free_channels = free_channels[1:]
    scheduler.start()
    input('Press enter to stop: ')
    scheduler.shutdown()

### Input
# path = "midicsv-1.1/Tetris Theme.csv"
# path = "midicsv-1.1/Billy_Joel_-_Piano_Man.csv"
# path = "midicsv-1.1/for_elise_by_beethoven.csv"
# path = "midicsv-1.1/deb_prel.csv"
# path = "midicsv-1.1/Henry Mancini - Pink Panther.csv"
# path = "midicsv-1.1/Beethoven-Moonlight-Sonata.csv"
# path = "midicsv-1.1/Sia - Elastic Heart.csv"
path = "midicsv-1.1/Pirates of the Caribbean - He's a Pirate.csv"
# path = "midicsv-1.1/joe_hisaishione_summers_day.csv"
# path = "midicsv-1.1/pachelbel_canon.csv"

echo_time = None # how long notes agiare played. Use None for as long as possible
play_all_instruments = False # plays instrument whether it is classified as pianno or not

play_recipe(make_recipe(path,echo_time,play_all_instruments))