from typing import List
import math


class Customer:
    x = None
    y = None
    demand = None
    ready_time = None
    due_time = None
    service_time = None

    def __init__(self, x: int, y: int, demand: int, ready_time: int, due_time: int,
                 service_time: int, **kwargs):
        self.x = int(float(x))
        self.y = int(float(y))
        self.demand = int(float(demand))
        self.ready_time = int(float(ready_time))
        self.due_time = int(float(due_time))
        self.service_time = int(float(service_time))




customer_list = List[Customer]


class Deport(Customer):
    def __init__(self, x: int, y: int, due_time: int, **kwargs):
        super(Deport, self).__init__(x, y, demand=0, ready_time=0, due_time=due_time,
                                     service_time=0)


def get_distance_customers_pair(c1: Customer, c2: Customer) -> float:
    return math.hypot(c2.x - c1.x, c2.y - c1.y)


class DistanceTable:
    distance_table = None

    def get_distance(self, source: int, dest: int) -> float:
        return self.distance_table[source][dest]

    def __init__(self, customer_list: customer_list):
        self.distance_table = []

        for index, cust in enumerate(customer_list):
            self.distance_table.append([])
            for stack_index, stuck_cust in enumerate(customer_list):

                if index == stack_index:
                    cost = 0
                elif index > stack_index:
                    cost = self.distance_table[stack_index][index]
                else:
                    cost = get_distance_customers_pair(cust, stuck_cust)
                self.distance_table[index].append(cost)
