def generate_model(fileName):
    # returns dictionary { note: [ [note, freq], [note, freq], ... ], ... }
    return

def get_next_note(prevNote, model):
    # returns next note based on previous
    return

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
