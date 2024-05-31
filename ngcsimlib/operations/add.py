from .summation import summation

class add(summation):
    """
    Not Compilable

    A subclass of summation that also adds the destinations value instead of overwriting it. For a compiler friendly
    version of this add the destination as a source to summation.
    """
    is_compilable = False

    def resolve(self, value):
        if self.destination is not None:
            self.destination.set(self.destination.value + value)


