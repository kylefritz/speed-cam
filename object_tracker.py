import datetime
from region import Region
from track import Track


class ObjectTracker:
    def __init__(self):
        self.tracks = []

    def process(self, image, region_proposals):
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

        # split tracks into next generation and ones ready to reap
        next_generation, reaped = [], []
        for track in self.tracks:
            if track.age() > datetime.timedelta(seconds=10):
                reaped.append(track)
            else:
                track.inc_generation()
                next_generation.append(track)

        self.tracks = next_generation

        # return the reaped tracks so they can be saved
        # TODO: this api is a little weird
        return reaped
