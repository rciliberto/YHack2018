import os

from mido import MidiFile

class Tick:
    """Represents a slice in time as a list of notes"""

    def __init__(self, *notes):
        self.notes = sorted(notes)

    def __str__(self):
        return str(self.notes)
    
    def __eq__(self, other):
        return self.notes == other.notes

class EncodedMidi:
    """Represents a midi file in our encoded version"""

    def __init__(self, midi_path):
        self.midi_in = MidiFile(midi_path)
        self.encoding = generate_encoding(self.midi_in.tracks[1])

    def generate_encoding(track):
        ticks = [[]]
        notes_to_add = []

        for msg in track:
            if not msg.is_meta:
                between_ticks = [ticks.pop()]*msg.time
                ticks = ticks + between_ticks
                if msg.type == 'note_on':
                    notes_to_add.append(msg.note)
                    #print("add", notes_to_add)
                elif msg.type == 'note_off':
                    notes_to_add.remove(msg.note)
                    #print("rm", notes_to_add)
                
                #print("actual", notes_to_add)
                ticks.append(notes_to_add[:])
        
        return ticks
