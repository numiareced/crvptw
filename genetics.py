from random import randint, shuffle
from typing import List
from customers import Customer as Destination
import global_vars

List_Node = List[Destination]


class Chromosome:
    route = []
    value = None
    vehicles_count = None
    route_per_vehicle = None
    total_travel_dist = None
    current_load = None
    elapsed_time = None
    max_elapsed_time = None
    distance_table = None
    routes_with_timings = None

    def __init__(self, route: iter):
        self.route = list(route)
        self.value = self.get_cost()

    def initial_port(self):
        self.vehicles_count = 1
        self.route_per_vehicle = [[0]]
        self.routes_with_timings = [[0, 0]]
        self.current_load = 0
        self.elapsed_time = 0
        self.max_elapsed_time = 0
        self.total_travel_dist = 0
        self.total_elapsed_time = 0

    @staticmethod
    def get_distance(source: int, dest: int) -> float:
        pass

    @staticmethod
    def get_node(index: int) -> Destination:
        pass

    @staticmethod
    def get_travel_time(distance: float) -> float:
        return distance / global_vars.vehicle_speed_avg

    @staticmethod
    def get_travel_cost(distance: float) -> float:
        return distance * global_vars.vehicle_cost_per_dist

    def check_time(self, source: int, dest: int, distance: float=None) -> bool:
        if distance is None:
            distance = self.get_distance(source, dest)
        dest_customer = self.get_node(dest)  # type: Node
        elapsed_new = self.get_travel_time(distance) + self.elapsed_time
        if elapsed_new <= dest_customer.due_time:
            return_time = self.get_travel_time(self.get_distance(dest, 0))
            deport_due_time = self.get_node(0).due_time
            return elapsed_new + dest_customer.service_time + return_time <= deport_due_time
        else:
            return False

    def check_capacity(self, dest: int) -> bool:
        dest_customer = self.get_node(dest)  # type: Node
        return self.current_load + dest_customer.demand <= global_vars.vehicle_capacity

    @staticmethod
    def get_vehicle_count_preference_cost(vehicles_count: int, deport_working_hours: int) -> float:
        return global_vars.vehicles_count_over_deport_hours_preference * vehicles_count + deport_working_hours

    def move_vehicle(self, source: int, dest: int, distance: float=None):
        if distance is None:
            distance = self.get_distance(source, dest)
        self.total_travel_dist += distance
        self.elapsed_time += self.get_travel_time(distance)
        self.max_elapsed_time = max(self.elapsed_time, self.max_elapsed_time)
        self.route_per_vehicle[-1].append(dest)
        self.routes_with_timings[-1].append(dest)
        self.routes_with_timings[-1].append(self.elapsed_time)
        if dest != 0:
            dest_customer = self.get_node(dest)  # type: Node
            self.current_load += dest_customer.demand
        else:
            self.current_load = 0

    def add_vehicle(self):
        self.vehicles_count += 1
        self.route_per_vehicle.append([0])
        self.routes_with_timings.append([0])
        self.elapsed_time = 0
        self.routes_with_timings[-1].append(self.elapsed_time)
        self.current_load = 0

    def get_cost(self) -> float:
        self.initial_port()
        for source, dest in pair([0] + self.route + [0]):
            if self.check_capacity(dest):
                if self.check_time(source, dest):
                    # ok to go from source to dest
                    self.move_vehicle(source, dest)
                else:
                    #send this one to depot and create new vehicle
                    self.move_vehicle(source, 0)
                    if (self.vehicles_count < global_vars.max_vehicles_num):
                        self.add_vehicle()
                        self.move_vehicle(0, dest)
            else:
                #no capacity
                self.move_vehicle(source, 0)
                distance = self.get_distance(0, dest)
                if self.check_time(0, dest, distance):
                    self.move_vehicle(0, dest, distance)
                else:
                    # too late to go to depo, create new vehicle
                    if (self.vehicles_count < global_vars.max_vehicles_num):
                        self.add_vehicle()
                        self.move_vehicle(0, dest, distance)


        total_travel_cost = Chromosome.get_travel_cost(self.total_travel_dist)
        total_vehicles_and_deport_working_hours_cost = self.get_vehicle_count_preference_cost(
            vehicles_count=self.vehicles_count,
            deport_working_hours=self.max_elapsed_time)
        return total_travel_cost + total_vehicles_and_deport_working_hours_cost

    def __iter__(self):
        for r in self.route:
            yield r

    def __lt__(self, other):
        return self.value < other.value

    def __eq__(self, other):
        return self.value == other.value


def pair(a: list) -> iter:
    return zip(a[:-1], a[1:])


def couple(iterable):
    a = iter(iterable)
    return zip(a, a)


def selection(population: list, selection_size: int, k: int=2, repeat: bool=False,
              reverse: bool=False) -> list:
    pop_copy = list(population)
    selection = []
    for selection_index in range(selection_size):
        shuffle(pop_copy)
        tournament = pop_copy[:k]
        if reverse:
            selected = min(tournament)
        else:
            selected = max(tournament)
        if not repeat:
            pop_copy.remove(selected)
            selection.append(selected)
    return selection



def crossover(parent1: list, parent2: list) -> (list, list):
    length = len(parent1)
    p1 = {}
    p2 = {}
    p1_inv = {}
    p2_inv = {}
    for i in range(length):
        p1[i] = parent1[i]
        p1_inv[p1[i]] = i
        p2[i] = parent2[i]
        p2_inv[p2[i]] = i

    cycles_indices = []
    while p1 != {}:
        i = min(list(p1.keys()))
        cycle = [i]
        start = p1[i]
        check = p2[i]
        del p1[i]
        del p2[i]

        while check != start:
            i = p1_inv[check]
            cycle.append(i)
            check = p2[i]
            del p1[i]
            del p2[i]

        cycles_indices.append(cycle)

    child = ({}, {})

    for run, indices in enumerate(cycles_indices):
        first = run % 2
        second = (first + 1) % 2

        for i in indices:
            child[first][i] = parent1[i]
            child[second][i] = parent2[i]

    child1 = []
    child2 = []
    for i in range(length):
        child1.append(child[0][i])
        child2.append(child[1][i])

    return child1, child2


### Mutation
def slice(chromosome_len: int) -> (int, int):
    slice_point_1 = randint(0, chromosome_len - 3)
    slice_point_2 = randint(slice_point_1 + 2, chromosome_len - 1)
    return slice_point_1, slice_point_2


def mutation(chromosome: list) -> list:
    slice_point_1, slice_point_2 = slice(len(chromosome))
    return chromosome[:slice_point_1] + list(reversed(chromosome[slice_point_1:slice_point_2])) + chromosome[slice_point_2:]

