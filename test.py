from mido import MidiFile

for msg in MidiFile('./ai.mid'):
    print(msg)

