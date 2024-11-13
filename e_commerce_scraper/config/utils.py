from .mappers import mappings


class Mapper:
    def __init__(self):
        self.mappings = mappings

    def __call__(self, item):
        try:
            return self.mappings[item]
        except Exception:
            return item


mapper = Mapper()
