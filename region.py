from log import log

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
