from collections import namedtuple
from frozendict import frozendict
import itertools

Taxi = namedtuple('Taxi', ['name'])
Passenger = namedtuple('Passenger', ['name'])

X, Y = Taxi('X'),Taxi('Y'),
Taxis = set([X, Y])

A, B, C = [Passenger(name) for name in ['A','B','C']]
Passengers = set([A, B, C])

PassengerMaxPrice = 7
TaxiMinPrice = 6

class Coalition(namedtuple('Coalition', ['passengers', 'taxi'])):
    def valid(self):
        if len(self.passengers) == 0 and self.taxi is None:
            return False

        if self.taxi is None:
            return all(self.passengers[p] == 0 for p in self.passengers)
        else:
            return len(self.passengers) <= 2

    def utilities(self):
        assert self.valid()

        ret = {}
        for p in self.passengers:
            if self.taxi is None:
                ret[p] = 0
            else:
                ret[p] = PassengerMaxPrice - self.passengers[p]

        if self.taxi is not None:
            ret[self.taxi] = sum(self.passengers.values()) - TaxiMinPrice

    def remove_passenger(self, passenger):
        assert passenger in self.passengers

        new_passengers_list = [p for p in self.passengers if p != passenger]
        new_fares = {p:self.passengers[p] for p in new_passengers}

        return Coalition(passengers=frozendict(new_fares), taxi=self.taxi)

    def remove_taxi(self, taxi):
        assert self.taxi == taxi

        new_passengers = {p:0 for p in self.passengers}
        return Coalition(frozendict(new_passengers), None)

    def possible_removals(self):
        removals = []
        for p in self.passengers:
            removals.append( (p, self.remove_passenger(p)) )

        if self.taxi is not None:
            removals.append( (t, self.remove_taxi(t)) )

        return removals

class World(namedtuple('World', ['coalitions'])):
    def valid(self):
        for p in Passengers:
            coalitions = [c for c in self.coalitions if p in c.passengers]
            if len(coalitions) != 1:
                return False

        for t in Taxis:
            coalitions = [c for c in self.coalitions if c.taxi == t]
            if len(coalitions) != 1:
                return False

        return True

print 'Generating possible worlds...'

def partitions(arr, start=0):
    if start == len(arr):
        yield []
        return

    for end in range(start+1, len(arr)+1):
        slice = arr[start:end]
        for subparts in partitions(arr, start=end):
            yield [slice] + subparts
    return

def construct_worlds(partition):
    subset_ranges = []
    for subset in partition:
        passengers = [p for p in subset if p in Passengers]
        taxis = [t for t in subset if t in Taxis]
        assert len(taxis)+len(passengers) == len(subset)

        if len(taxis) > 1:
            return

        if len(taxis) == 1:
            taxi = taxis[0]
        else:
            taxi = None

        if taxi is None:
            subset_ranges.append([Coalition(frozendict({p:0 for p in passengers}), None)])
            continue

        coalitions = []
        for fares in itertools.product(range(PassengerMaxPrice+1), repeat=len(passengers)):
            coalitions.append(Coalition(frozendict(zip(passengers,fares)), taxi))
        subset_ranges.append(coalitions)

    for coalitions in itertools.product(*subset_ranges):
        yield World(frozenset(coalitions))

def gen_all_worlds():
    worlds = set()
    participants = list(Passengers) + list(Taxis)
    for partition in partitions(participants):
        for world in construct_worlds(partition):
            assert world not in worlds
            assert world.valid()
            worlds.add(world)
    return worlds

all_worlds = gen_all_worlds()
print len(all_worlds), 'possible worlds'
for w in all_worlds:
    print w
