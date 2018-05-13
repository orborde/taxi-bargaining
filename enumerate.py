from collections import namedtuple
from frozendict import frozendict
import itertools

Taxi = namedtuple('Taxi', ['name'])
Passenger = namedtuple('Passenger', ['name'])

X, Y = Taxi('X'),Taxi('Y'),
Taxis = [X, Y]

A, B, C = [Passenger(name) for name in ['A','B','C']]
Passengers = [A, B, C]

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

# https://docs.python.org/2/library/itertools.html#recipes
def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))

print 'Generating possible coalitions'
def all_coalitions():
    def generator():
        for passengers in powerset(Passengers):
            for taxi in [None] + Taxis:
                if taxi is None:
                    fare_range = [0]
                else:
                    fare_range = range(PassengerMaxPrice+1)

                for fares in itertools.product(fare_range, repeat=len(passengers)):
                    yield Coalition(frozendict(zip(passengers, fares)), taxi)
    return itertools.ifilter(lambda c: c.valid(), generator())

coalitions = list(all_coalitions())
assert len(coalitions) == len(set(coalitions))
coalitions = set(coalitions)
print len(coalitions), 'coalitions'
