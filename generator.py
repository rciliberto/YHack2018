from encoding import EncodedMidi, Tick
from mido import Message, MidiFile, MidiTrack
import random

def generate_model(file_name):
    ticks = EncodedMidi(file_name).encoding
    
    model = {}
    prev_tick = 'FIRST'
    for tick in ticks:
        frequencies = model.get(prev_tick, {})
        frequencies[tick] = frequencies.get(tick, 0) + 1
        model[prev_tick] = frequencies
        prev_tick = tick

    frequencies = model.get(prev_tick, {})
    frequencies['END'] = 1
    model[prev_tick] = frequencies

    return model

def get_next_note(prev_note, model):
    # returns next note based on previous
    #print('prev', prev_note)
    note_list = model[prev_note]
    #print(note_list)
    sum = 0
    for tick, freq in note_list.items():
        sum += freq
    weighted_val = random.randint(0, sum)
    #print(weighted_val)
    for tick, freq in note_list.items():
        weighted_val -= freq
        #print('asdf', weighted_val)
        if weighted_val <= 0:
            #print(tick)
            return tick
    print("NONE")

# returns list of notes by tick
def generate_new(model):
    prev_note = 'FIRST'
    ticks = []
    next_note = get_next_note('FIRST', model)
    while (next_note != 'END'):
        ticks.append(next_note)
        prev_note = next_note
        next_note = get_next_note(prev_note, model)
    return ticks

def save(song, ticks_per_beat, file_name):
    mid = MidiFile(type=0)
    track = MidiTrack()
    track.append(Message('program_change', program=1, time=0))
    mid.ticks_per_beat = ticks_per_beat

    time_since_last_command = 0
    running_notes = []
    for tick in song:
        to_delete = [t for t in running_notes if t not in tick.notes]
        to_add = [t for t in tick.notes if t not in running_notes]

        for note in to_add:
            running_notes.append(note)
            track.append(Message('note_on',
                note=note,
                velocity=64,
                time=time_since_last_command
            ))
            time_since_last_command = 0

        for note in to_delete:
            running_notes.remove(note)
            track.append(Message('note_off',
                note=note,
                velocity=64,
                time=time_since_last_command
            ))
            time_since_last_command = 0
        time_since_last_command += 1
    
    mid.tracks.append(track)
    mid.save(file_name)
