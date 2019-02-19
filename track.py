import datetime
from region import Region
from log import log

class Track:
    def __init__(self, region):
        self.id = Track.get_next_id()
        self.generation = 0
        self.regions = [region]

    def matches(self, region):
        # TODO: check features of proposed region to see if matches
        # for now, just rely on the TLL
        return True

    def update(self, region):
        self.regions.append(region)

    def age(self):
        return datetime.datetime.now() - self.regions[-1].frame.captured_at

    def promote(self):
        self.generation += 1
        return self

    def to_dict(self):
        return {
            'local_id': self.id,
            'generation': self.generation,
            'regions': [r.to_dict() for r in self.regions],
        }

    next_object_id = 0
    @staticmethod
    def get_next_id():
        id = Track.next_object_id
        Track.next_object_id += 1
        return id
