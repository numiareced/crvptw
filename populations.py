from genetics import  crossover, mutation, selection, couple
import genetics
import global_vars
from typing import List
from random import shuffle
from datetime import datetime

population = {
    'pop_size': 100,
    'crossover_method': staticmethod(crossover),
    'mutation_method': staticmethod(mutation),
    'removing_method': staticmethod(selection),
    'selection_method': staticmethod(selection),
    'selection_pressure': 2,
    'selection_repeat': False,
    'parent_selection_ratio': 0.75,
    'mutation_ratio': 0.1,
}

class Chromosome(genetics.Chromosome):
    pass


List_Chromosome = List[Chromosome]


class Population:
    generation = []     # type: List_Chromosome
    gen_index = 0   # type: int
    population_size = None    # type: int
    chromosome_width = None    # type: int
    chromosome_higher_value_fitter = None
    crossover_method = None
    mutation_method = None
    removing_method = None
    selection_method = None
    tournament_size = None
    selection_repeat = None
    parent_selection_ratio = None
    mutation_ratio = None
    genocide_ratio = 0

    #chromosome_class = None

    def __init__(self, pop_size: int, chromosome_width: int,
                 crossover_method: staticmethod, mutation_method: staticmethod,
                 removing_method: staticmethod, selection_method: staticmethod,
                 selection_pressure: int, selection_repeat: bool,
                 parent_selection_ratio: float, mutation_ratio: float):
        self.population_size = int(pop_size)
        self.chromosome_width = int(chromosome_width)
        self.chromosome_higher_value_fitter = False
        self.crossover_method = crossover_method.__func__
        self.mutation_method = mutation_method.__func__
        self.removing_method = removing_method.__func__
        self.selection_method = selection_method.__func__
        self.tournament_size = 2 if selection_pressure is None else int(selection_pressure)
        self.selection_repeat = bool(selection_repeat)
        self.parent_selection_ratio = float(parent_selection_ratio)
        self.mutation_ratio = float(mutation_ratio)
        self.generation = self.create_initial_gen()

    def create_initial_gen(self, init_size: int=None) -> List_Chromosome:
        if not init_size:
            init_size = self.population_size
        generation_holder = []
        random_indices = list(range(self.chromosome_width))
        for i in range(init_size):
            shuffle(random_indices)
            init_chromosome = Chromosome(random_indices)
            generation_holder.append(init_chromosome)
        return generation_holder

    def cross(self, parent1: Chromosome, parent2: Chromosome) -> (Chromosome, Chromosome):
        indices1, indices2 = self.crossover_method(list(parent1), list(parent2))
        child1 = Chromosome(indices1)
        child2 = Chromosome(indices2)
        return child1, child2

    def mutate(self, chromosome: Chromosome) -> Chromosome:

        muted_indices = self.mutation_method(list(chromosome))
        return Chromosome(muted_indices)

    def select_parent(self, generation: List_Chromosome) -> list:
        parent_selection_size = int(len(generation) * self.parent_selection_ratio)
        return self.selection_method(generation, parent_selection_size, k=self.tournament_size,
                                     repeat=self.selection_repeat, reverse=(not self.chromosome_higher_value_fitter))

    def mutation_index_selection(self, generation: List_Chromosome) -> list:
        mutation_selection_size = int(len(generation) * self.mutation_ratio)
        indices = list(range(len(generation)))
        shuffle(indices)
        return indices[:mutation_selection_size]

    def get_offsprings(self, generation: List_Chromosome) -> List_Chromosome:
        selected_parents = self.select_parent(generation)
        offsprings_holder = []
        for parent1, parent2 in couple(selected_parents):
            child1, child2 = self.cross(parent1, parent2)
            offsprings_holder += [child1, child2]
        return offsprings_holder

    def permute_generation(self, generation: List_Chromosome):
        mutation_indices = self.mutation_index_selection(generation)
        for index in mutation_indices:
            generation[index] = self.mutate(generation[index])

    def remove_less_fitters(self, generation: List_Chromosome, removing_size: int):
        selected_chromosomes = self.removing_method(generation, removing_size, k=self.tournament_size,
                                                    repeat=False, reverse=self.chromosome_higher_value_fitter)
        for ch in selected_chromosomes:
            generation.remove(ch)

    def create_next_generation(self) -> List_Chromosome:
        children = self.get_offsprings(self.generation)
        new_gen = self.generation + children    # type: List_Chromosome
        self.permute_generation(new_gen)
        deceasing_size = max(len(new_gen) - self.population_size, 0)
        self.remove_less_fitters(new_gen, deceasing_size)
        return new_gen

    def evolve(self) -> Chromosome:
        while self.gen_index < global_vars.MAX_GEN:
            if self.gen_index % 100 == 0:
                print (str(self.gen_index) + " generations passed")
                if self.genocide_ratio > 0 and min(self.generation).value == max(self.generation).value:
                    self.generation = self.genocide(self.generation)
            self.generation = self.create_next_generation()
            self.gen_index += 1
        return min(self.generation)

    def genocide(self, generation: List_Chromosome):
        new_gen_size = int(len(generation) * self.genocide_ratio)
        surviving_selection_size = len(generation) - new_gen_size
        survivors = self.selection_method(generation, surviving_selection_size, k=self.tournament_size,
                                          repeat=self.selection_repeat,
                                          reverse=(not self.chromosome_higher_value_fitter))
        new_gen = self.create_initial_gen(new_gen_size)
        return survivors + new_gen

