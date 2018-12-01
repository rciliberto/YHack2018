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

def save(song, file_name):
    mid = MidiFile(type=0)
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(Message('program_change', program=1, time=0))

    curr_tick = 1
    last_command = 1
    running_notes = []
    for tick in song:
        to_keep = []
        to_delete = []

        for note in running_notes:
            if note in tick.notes:
                to_keep.append(note)
            else:
                to_delete.append(note)

        for note in tick.notes:
            if not note in to_keep:
                to_keep.append(note)
                track.append(Message('note_on',
                    note=note,
                    velocity=(8 * random.randint(8, 16) - 1),
                    time=(curr_tick - last_command)
                ))
                last_command = curr_tick

        running_notes = to_keep
        for note in to_delete:
            track.append(Message('note_off',
                note=note,
                velocity=127,
                time=(curr_tick - last_command)
            ))
            last_command = curr_tick

        curr_tick += 1

    for note in running_notes:
        track.append(Message('note_off',
            note=note,
            velocity=127,
            time=(curr_tick - last_command)
        ))
        last_command = curr_tick
    mid.save(file_name)
