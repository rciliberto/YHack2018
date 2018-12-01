import random
def generate_model(file_name):
    # returns dictionary { note: [ [note, freq], [note, freq], ... ], ... }
    return

def get_next_note(prev_note, model):
    # returns next note based on previous
    sum = 0
    for nested_list in note_list:
        sum += nested_list[1]
    weighted_val = random.randint(0,sum)
    note_list = model[prev_note]
    for nested_list in note_list:
        sum -= weighted - (nested_list[1])
        if sum < 0:
            return nested_list[0]

# returns list of notes by tick
def generate_new(model):
    prev_note = 'FIRST'
    notes = []
    while ((next_note = get_next_note(prev_note, model)) != 'END'):
        notes.append(next_note)
        prev_note = next_note
    return

def save(song, file_name):
    # write output

model = generate_model('./01Minuetto1.mid')
song = generate_new(model)
save(notes, './newsong.mid')
