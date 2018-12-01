import os

from mido import MidiFile

class Tick:
    """Represents a slice in time as a list of notes"""

    def __init__(self, notes):
        self.notes = sorted(notes)

    def __str__(self):
        return str(self.notes)
    
    def __eq__(self, other):
        if not isinstance(other, Tick):
            return False
        return self.notes == other.notes

    def __hash__(self):
        return hash(repr(str(self)))

class EncodedMidi:
    """Represents a midi file in our encoded version"""

    def __init__(self, midi_path):
        midi_in = MidiFile(midi_path)
        self.encoding = self.generate_encoding(midi_in.tracks[1])

    def generate_encoding(self, track):
        ticks = [[]]
        notes_to_add = []

        for msg in track:
            if not msg.is_meta:
                between_ticks = [ticks.pop()]*msg.time
                ticks = ticks + between_ticks
                if msg.type == 'note_on':
                    notes_to_add.append(msg.note)
                elif msg.type == 'note_off':
                    notes_to_add.remove(msg.note)
                
                ticks.append(Tick(notes_to_add[:]))
        
        return ticks
