import collections
import datetime


class Track:
    next_object_id = 0

    @staticmethod
    def get_next_id():
        id = Track.next_object_id
        Track.next_object_id += 1
        return id

    def __init__(self, region):
        self.id = Track.get_next_id()
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
        self.region = region

    def update(self, region):
        # TODO: update track with region
        self.updated_at = datetime.datetime.now()


class Region:
    @staticmethod
    def can_merge(r1, r2):
        # TODO: compare regions
        return False

    @staticmethod
    def merge(r1, r2):
        # TODO: merge regions
        return r1

    @staticmethod
    def merge_regions(regions):
        already_merged = set()
        for i in range(len(regions)):
            if i + 1 > len(regions):
                break

            for j in range(i + 1, len(regions)):
                if i in already_merged or j in already_merged:
                    continue

                r1 = regions[i]
                r2 = regions[j]

                if Region.can_merge(r1, r2):
                    already_merged.add(i)
                    already_merged.add(j)
                    yield Region.merge(r1, r2)

        # also return anything that wasn't merged
        for index, region in enumerate(regions):
            if index in already_merged:
                continue
            yield region

    def __init__(self, geometry):
        self.geometry = geometry

    def is_car(self):
        # TODO: return False if primary color indicates region is just headlights
        return True


class ObjectTracker:
    def __init__(self):
        self.tracks = []

    def process(self, region_proposals):
        unmerged_regions = [Region(r) for r in region_proposals]
        regions = Region.merge_regions(unmerged_regions)

        # associate with existing track
        for region in regions:
            if not region.is_car():
                continue

            # associate with existing track
            for track in self.tracks:
                if track.matches(region):
                    track.update(region)
                    continue

            # birth new track
            self.tracks.append(Track(region))
