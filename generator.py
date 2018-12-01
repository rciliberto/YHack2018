from mido import Message, MidiFile, MidiTrack
import random

def generate_model(file_name):
    # returns dictionary { Tick: [ [ Tick, freq], ... ], ... }
    return

def get_next_note(prev_note, model):
    # returns next note based on previous
    sum = 0
    for nested_list in note_list:
        sum += nested_list[1]
    weighted_val = random.randint(0, sum)
    note_list = model[prev_note]
    for nested_list in note_list:
        sum -= weighted - (nested_list[1])
        if sum < 0:
            return nested_list[0]

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
            if note in tick:
                to_keep.append(note)
            else:
                to_delete.append(note)

        for note in tick:
            if not note in to_keep:
                to_keep.append(note)
                track.append(Message('note_on',
                    note=note,
                    velocity=127,
                    time=(curr_tick - last_command)
                ))
                print('note_on ' + str(note) + ' ' + str(curr_tick - last_command))
                last_command = curr_tick

        running_notes = to_keep
        for note in to_delete:
            track.append(Message('note_off',
                note=note,
                velocity=127,
                time=(curr_tick - last_command)
            ))
            print('note_off ' + str(note) + ' ' + str(curr_tick - last_command))
            last_command = curr_tick

        curr_tick += 1

    for note in running_notes:
        track.append(Message('note_off',
            note=note.note,
            velocity=127,
            time=(curr_tick - last_command)
        ))
        print('note_off ' + str(note) + ' ' + str(curr_tick - last_command))
        last_command = curr_tick
    mid.save(file_name)

model = generate_model('./01Minuetto1.mid')
song = generate_new(model)
save(song, './newsong.mid')
