class Tick:
    """Represents a slice in time as a list of notes"""

    def __init__(self, *notes):
        self.notes = sorted(notes)

    def __str__(self):
        return str(self.notes)
    
    def __eq__(self, other):
        return self.notes == other.notes