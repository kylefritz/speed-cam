import datetime

from region import Region
from track import Track
from log import log


class ObjectTracker:
    ttl = datetime.timedelta(seconds=10)

    def __init__(self):
        self.tracks = []

    def process(self, region_proposals):
        birthed, promoted, reaped = [], [], []

        region_proposals = Region.merge_regions(region_proposals)
        for region in region_proposals:
            if not region.is_car():
                continue

            # associate with existing track
            for track in self.tracks:
                if track.matches(region):
                    track.update(region)
                    continue

            birthed.append(Track(region))

        # existing tracks are either promoted or reaped
        for track in self.tracks:
            if track.age() > ObjectTracker.ttl:
                reaped.append(track)
            else:
                promoted.append(track.promote())

        log.info(f'birthed={len(birthed)} promoted={len(promoted)} reaped={len(reaped)}')
        self.tracks = birthed + promoted

        # return the reaped tracks so they can be saved
        return reaped
