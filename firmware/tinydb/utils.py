"""
Utility functions.
"""

from collections import OrderedDict


__all__ = ('LRUCache', 'freeze')


class LRUCache():
    """
    A least-recently used (LRU) cache with a fixed cache size.

    This class acts as a dictionary but has a limited size. If the number of
    entries in the cache exeeds the cache size, the leat-recently accessed
    entry will be discareded.

    This is implemented using an ``OrderedDict``. On every access the accessed
    entry is moved to the front by re-inserting it into the ``OrderedDict``.
    When adding an entry and the cache size is exceeded, the last entry will
    be discareded.
    """

    def __init__(self, capacity=None):
        self.capacity = capacity
        self.cache = OrderedDict() 

    @property
    def lru(self):
        return list(self.cache.keys())

    @property
    def length(self) -> int:
        return len(self.cache)

    def clear(self) -> None:
        self.cache.clear()

    def __len__(self) -> int:
        return self.length

    def __contains__(self, key: object) -> bool:
        return key in self.cache

    def __setitem__(self, key, value) -> None:
        self.set(key, value)

    def __delitem__(self, key) -> None:
        del self.cache[key]

    def __getitem__(self, key):
        value = self.get(key)
        if value is None:
            raise KeyError(key)

        return value

    def __iter__(self):
        return iter(self.cache)

    def move_to_end(self, key):
        temp = self.cache.get(key)
        del self.cache[key]
        self.cache[key] = temp

    def get(self, key, default = None):
        value = self.cache.get(key)

        if value is not None:
            self.move_to_end(key)

            return value

        return default

    def set(self, key, value):
        if self.cache.get(key):
            self.move_to_end(key)

        else:
            self.cache[key] = value

            # Check, if the cache is full and we have to remove old items
            # If the queue is of unlimited size, self.capacity is NaN and
            # x > NaN is always False in Python and the cache won't be cleared.
            if self.capacity is not None and self.length > self.capacity:
                del self.cache[list(self.cache.keys())[0]]


class FrozenDict(dict):
    """
    An immutable dictoinary.

    This is used to generate stable hashes for queries that contain dicts.
    Usually, Python dicts are not hashable because they are mutable. This
    class removes the mutability and implements the ``__hash__`` method.
    """

    def __hash__(self):
        # Calculate the has by hashing a tuple of all dict items
        return hash(tuple(sorted(self.items())))

    def _immutable(self, *args, **kws):
        raise TypeError('object is immutable')

    # Disable write access to the dict
    __setitem__ = _immutable
    __delitem__ = _immutable
    clear = _immutable
    setdefault = _immutable
    popitem = _immutable

    def update(self, e=None, **f):
        raise TypeError('object is immutable')

    def pop(self, k, d=None):
        raise TypeError('object is immutable')


def freeze(obj):
    """
    Freeze an object by making it immutable and thus hashable.
    """
    if isinstance(obj, dict):
        # Transform dicts into ``FrozenDict``s
        return FrozenDict((k, freeze(v)) for k, v in obj.items())
    elif isinstance(obj, list):
        # Transform lists into tuples
        return tuple(freeze(el) for el in obj)
    elif isinstance(obj, set):
        # Transform sets into ``frozenset``s
        return frozenset(obj)
    else:
        # Don't handle all other objects
        return obj
