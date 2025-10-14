class Prism:
    def __init__(self, prism_type, initial_offset):
        self.prism_type = prism_type
        self.offset = initial_offset

        self.direction = True

        self.current_min = initial_offset
        self.current_max = initial_offset
        self.break_recovery_pairs = []