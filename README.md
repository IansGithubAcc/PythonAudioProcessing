# Python Audio Processing
Welcome to my Python Audio Processing (PAP) hobby project GitHub page.

The purpose of PAP is threefold:
- Analyse raw audio music files using Fourier transformation and transform it to a recipe of individual musical notes.
- Play such a recipe back to illustrate the quality of the interpretation.
- Reproduce musical paterns by implemeting some form of AI such as for example a neural network or a Baysian process emulator.

## Current progress
The first phase of this project focusses on the ability to play recipes with individual notes as coherend songs. The music industries MIDI file standard is used as the backbone of these recipes. Since MIDI files are difficult to interpret without specialized libraries, this projects will apply MIDI files converted to the CSV format. Such a tranformation can be achieved using the [MIDICSV](https://www.fourmilab.ch/webtools/midicsv/) tool. 

The files currently published allow the user to interpret such MIDI-converted-CSV files and play them back provided a musical note audio set is given. An example of such an audio set are the [University of Iowa Steinway (pianno) recordings](http://theremin.music.uiowa.edu/MISpiano.html). In its current form the code only plays pianno type instruments, however the format allows for easy inclusion of other/multiple instruments.

The MIDICSV player can easilly be used by downloading the .exe file from the dist folder and using the input to define file paths. Instrument note files are ecpected to be named by their MIDI number. The code as currently written seems to perform reasonably well, to the point where you can enjoyably listen to most pianno songs.

## Next steps
The second phase of the project will delve into the analyses and interpretation of raw audio files in order convert them the MIDI-converted-CSV format.

The last phase of the project goes a step further and will attempt to generate music using interpreted music
