from collections import namedtuple
from frozendict import frozendict
import itertools

Taxi = namedtuple('Taxi', ['name'])
Passenger = namedtuple('Passenger', ['name'])

X, Y = Taxi('X'),Taxi('Y'),
Taxis = set([X, Y])

A, B, C = [Passenger(name) for name in ['A','B','C']]
Passengers = set([A, B, C])

Participants = Taxis.union(Passengers)

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

    def remove(self, participant):
        assert participant in Participants
        if participant in Passengers:
            return self.remove_passenger(participant)
        else:
            return self.remove_taxi(participant)

    def __in__(self, x):
        assert x is not None
        return (x in self.passengers) or (taxi == x)

    def possible_removals(self):
        removals = []
        for p in self.passengers:
            removals.append( (p, self.remove_passenger(p)) )

        if self.taxi is not None:
            removals.append( (t, self.remove_taxi(t)) )

        return removals


# https://docs.python.org/2/library/itertools.html#recipes
def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))

def assemble_coalition(participants):
    passengers = [p for p in participants if p in Passengers]
    taxis = [t for t in participants if t in Taxis]
    assert len(taxis)+len(passengers) == len(participants)

    if len(taxis) > 1:
        return None

    if len(taxis) == 1:
        taxi = taxis[0]
    else:
        taxi = None

    if len(passengers) == 0 and taxi is None:
        return None

    return passengers, taxi

def fares_for_coalition(passengers, taxi):
    assert (len(passengers) > 0) or (taxi is not None)

    if taxi is None or len(passengers) == 0:
        yield Coalition(frozendict({p:0 for p in passengers}), taxi)
        return

    for fares in itertools.product(range(PassengerMaxPrice+1), repeat=len(passengers)):
        yield Coalition(frozendict(zip(passengers,fares)), taxi)

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

    def possible_new_worlds(self):
        prev_coalition = {}
        def record_in(x, c):
            assert x not in prev_coalition
            prev_coalition[x] = c

        for c in self.coalitions:
            for p in c.passengers:
                record_in(p, c)
            if c.taxi is not None:
                record_in(c.taxi, c)

        for defectors in powerset(Participants):
            coalition = assemble_coalition(defectors)
            if coalition is None:
                continue

            passengers, taxi = coalition
            revised_old_coalitions = []
            for c in self.coalitions:
                for x in defectors:
                    if x in c:
                        c = c.remove(x)
                revised_old_coalitions.append(c)

            for new_coalition in fares_for_coalition(passengers, taxi):
                new_coalitions = revised_old_coalitions + [new_coalition]
                new_world = World(frozenset(new_coalitions))
                assert new_world.valid()
                yield defectors, new_world


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
        coalition = assemble_coalition(subset)
        if coalition is None:
            return

        passengers, taxi = coalition
        subset_ranges.append(fares_for_coalition(passengers, taxi))

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

print 'Checking...'
for w in all_worlds:
    for defectors, new_world in w.possible_new_worlds():
        assert new_world in all_worlds
