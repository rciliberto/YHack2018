import os

from mido import MidiFile, tempo2bpm

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
        self.ticks_per_beat = midi_in.ticks_per_beat
        self.encoding = self.generate_encoding(midi_in.tracks)
        
    def generate_encoding(self, tracks):
        merged_ticks = []
        track_ticks = []
        
        longest_track = 0
        longest_track_length = 0
        track_index = 0
        for track in tracks:
            ticks = [[]]
            notes_to_add = []
            num_ticks = 0

            lowest = 127
            highest = 0

            for msg in track:
                if not msg.is_meta:
                    num_ticks += msg.time

                    between_ticks = [ticks.pop()]*msg.time
                    ticks = ticks + between_ticks
                    if msg.type == 'note_on':
                        notes_to_add.append(msg.note)

                        if msg.note > highest:
                            highest = msg.note
                        if msg.note < lowest:
                            lowest = msg.note
                        #print("add", notes_to_add)
                    elif msg.type == 'note_off':
                        notes_to_add.remove(msg.note)
                        #print("rm", notes_to_add)
                    
                    #print("actual", notes_to_add)
                    ticks.append(notes_to_add[:])
                    #print(Tick(notes_to_add[:]).notes)
            if highest > lowest:
                track_ticks.append(ticks) 
                if num_ticks > longest_track_length:
                    longest_track_length = num_ticks
                    longest_track = track_index

                track_index += 1

        for i in range(0, longest_track_length):
            notes = []
            for track in track_ticks:
                if len(track) > i and len(track) != 1:
                    notes += track[i]
            merged_ticks.append(Tick(notes))
        return merged_ticks
