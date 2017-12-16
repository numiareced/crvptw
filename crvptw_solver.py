from genetics import Chromosome as BaseChromosome
import populations
from customers import Deport, Customer, DistanceTable
from data_parser import read_data, write_output
from datetime import datetime

import sys

file_header = {
    'default_name': 'R101',
    'header_mapping': {
        'XCOORD.': 'x_coordinates',
        'YCOORD.': 'y_coordinates',
        'DEMAND': 'demand',
        'READY TIME': 'ready_time',
        'DUE DATE': 'due_time',
        'SERVICE TIME': 'service_time',
    }
}


class Chromosome(BaseChromosome):
    @staticmethod
    def get_distance(source: int, dest: int) -> float:
        global distances
        return distances.get_distance(source, dest)

    @staticmethod
    def get_node(index: int) -> Customer:
        global customers
        return customers[index]


populations.Chromosome = Chromosome



if len(sys.argv) < 2:
    print ("No argument is set, using R101.txt data file as default")
    filename = 'R101'
else:
    filename = sys.argv[1]
process_timer_start = datetime.now()
cust_data = read_data(filename)
customers = [Deport(**cust_data[0])]
customers += [Customer(**customer_dict) for customer_dict in cust_data]
distances = DistanceTable(customers)

ga_pop = populations.Population(chromosome_width=len(customers), **populations.population)
best_chrome = ga_pop.evolve()
print("final solution is:", best_chrome.routes_with_timings)
process_time = datetime.now() - process_timer_start
print ("Time elapsed:" + str(process_time))
write_output(filename, best_chrome.routes_with_timings)
