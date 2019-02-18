from log import log


class Region:
    def __init__(self, rectange, frame):
        self.rectange = rectange
        self.frame = frame

    def is_car(self):
        # TODO: return False if primary color indicates region is just headlights
        return True

    def to_dict(self):
        (x,y, height, width) = self.rectange
        return {
            'x': x, 'y': y,
            'height': height, 'width': width,
            's3_key': self.frame.s3_key,
        }

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

                if can_merge(r1, r2):
                    already_merged.add(i)
                    already_merged.add(j)
                    yield merge(r1, r2)

        # also return anything that wasn't merged
        for index, region in enumerate(regions):
            if index in already_merged:
                continue
            yield region


def can_merge(r1, r2):
    # TODO: compare regions
    return False


def merge(r1, r2):
    # TODO: merge regions
    return r1
