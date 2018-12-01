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
        sum -= weighted - (nested_list[1]-1)
        if sum <= 0:
            return nested_list[0]

def generate_new(model):
    # output: newly generated midi file
    return
