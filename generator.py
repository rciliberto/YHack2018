import random
def generate_model(file_name):
    # returns dictionary { note: [ [note, freq], [note, freq], ... ], ... }
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
    while ((next_note = get_next_note(prev_note, model)) != 'END'):
        ticks.append(next_note)
        prev_note = next_note
    return ticks

def save(song, file_name):
    mid = MidiFile(type=0)
    track = MidiTrack()
    mid.tracks.append(track)

    tick = 0
    last_command = 0
    running_notes = []
    for tick in song:
        tick ++ 1
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
                    note=note.note,
                    velocity=note.velocity,
                    time=(tick - last_command)
                ))
                last_command = tick

        running_notes = to_keep
        for note in to_delete:
            track.append(Message('note_off',
                note=note.note,
                velocity=127,
                time=(tick - last_command)
            ))
            last_command = tick

    mid.save(file_name)

model = generate_model('./01Minuetto1.mid')
song = generate_new(model)
save(song, './newsong.mid')
