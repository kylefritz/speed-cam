import datetime
from region import Region

class Track:
    next_object_id = 0

    @staticmethod
    def get_next_id():
        id = Track.next_object_id
        Track.next_object_id += 1
        return id

    def __init__(self, region):
        self.id = Track.get_next_id()
        self.generation = 0
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
        self.region = region

    def update(self, region):
        # TODO: update track with region
        self.updated_at = datetime.datetime.now()

    def upload(self):
        pass

    def age(self):
        return datetime.datetime.now() - self.updated_at

    def inc_generation(self):
        self.generation += 1

    def to_pickle(self):
        pass
