import numpy as np
import random

def prep_file(file_name):
  file = open(file_name, "r")
  lines = [i.rstrip('\n') for i in file]
  num_cities = lines[0]
  cities = lines[1:]
  all_cities = [i.split() for i in cities]
  return all_cities


def nearest_city(cities):
    num_cities = len(cities)
    unvisited_cities_index = set(range(num_cities))
    path = [] 
    
    current_city_index = random.choice(list(unvisited_cities_index))
    path.append(current_city_index)
    unvisited_cities_index.remove(current_city_index)
    
    for i in range(1, num_cities):
        nearest_city_index = min(unvisited_cities_index, key=lambda city: distance_calc(cities[current_city_index], cities[city]))
        path.append(nearest_city_index) 
        current_city_index = nearest_city_index
        unvisited_cities_index.remove(current_city_index)

    path.append(path[0])
    return [cities[i] for i in path]


def create_populations(nums, cities):
    initial_population = []
    for _ in range(nums):
        initial_tour = nearest_city(cities)
        if initial_tour not in initial_population:
          initial_population.append(initial_tour)
    return initial_population


def distance_calc(fr,to):
    dist = np.sqrt((float(fr[0])-float(to[0]))**2 + (float(fr[1])-float(to[1]))**2 + (float(fr[2])-float(to[2]))**2)
    return dist

def calculate_fitness(population):
    fitness = []
    for route in population:
      total_dist = 0
      for i in range(len(route)-1):
        total_dist += distance_calc(route[i],route[i+1])
      fitness.append(1/total_dist)
    return fitness

def rank_routes(fitness):
  position_in_population = []
  fitness_values = []
  for i in sorted(fitness, reverse = True):
    idx = fitness.index(i)
    fitness_values.append(i)
    position_in_population.append(idx)
  return position_in_population, fitness_values


def select_parents(routes_ranking, fitness_values, tournament_size, number_of_parents, retention_size):
    selected_parents = []
    for i in range(retention_size):
      selected_parents.append(routes_ranking[i])

    if(tournament_size>number_of_parents-retention_size):
      tournament_size = number_of_parents-retention_size
      
    while len(selected_parents) <= number_of_parents-retention_size:
        tournament_indices = random.sample(range(len(routes_ranking[retention_size:])), tournament_size)
        best_index = min(tournament_indices, key=lambda i: fitness_values[i])
        selected_parents.append(routes_ranking[best_index])
    return selected_parents


def mating_pool(population, ranks):
    matingpool = []
    for i in ranks:
      matingpool.append(population[i])
    return matingpool


def crossover(parent1,parent2):
    start_idx, end_idx = sorted(random.sample(range(1,len(parent1)-1), 2)) 
    child = [-1] * len(parent1)
    sub_array_1 = parent1[start_idx:end_idx+1]
    child[start_idx:end_idx+1] = sub_array_1
    for i in parent2:
      if i not in child:
        initial = i
        break
    child[0], child[-1] = initial, initial

    unused = []
    for gene in parent2+parent1:
      if (gene not in child) and (gene not in unused):
        unused.append(gene)

    for i in range(len(child)):
      if(child[i]==-1):
        child[i] = unused[0]
        unused.pop(0)

    return child

def crossover_entire_pop(mating_pool, crossover_rate, ret_size):
    children = mating_pool[:ret_size]  
    for i in range(ret_size, len(mating_pool) - 1):
        if random.random() > crossover_rate:
            child = crossover(mating_pool[i], mating_pool[i + 1])
            children.append(child)
        else:
            children.append(mating_pool[i])
    return children


def mutate(each_pop,mutation_rate):
    for i in range(1,len(each_pop)-1):
      if(random.random()>mutation_rate):
        j = random.randint(1,len(each_pop)-2)
        each_pop[i],each_pop[j] = each_pop[j], each_pop[i]
    return each_pop

def mutate_entire_pop(population, mutation_rate, ret_size):
    mutated_pop = population[:ret_size]  
    for i in range(ret_size, len(population)-ret_size):
      mutated = mutate(population[i],mutation_rate)
      mutated_pop.append(mutated)
    return mutated_pop

def new_generation(current_gen, crossover_rate, mutation_rate, number_of_parents, retention_size):
    fitness = calculate_fitness(current_gen)
    ranking, fitness_values = rank_routes(fitness)
    selection_results = select_parents(ranking, fitness_values, 5, number_of_parents, retention_size)
    matingpool = mating_pool(current_gen, selection_results)
    children = crossover_entire_pop(matingpool,crossover_rate, retention_size)
    next_generation = mutate_entire_pop(children, mutation_rate, retention_size)
    return next_generation


def genetic_algorithm(fname, population_size, crossover_rate, mutation_rate, number_of_parents, generations):
    all_cities = prep_file(fname)
    population = create_populations(population_size,all_cities)
    retention_size = 2
    final_dist = np.inf
    fafa = []

    for i in range(generations):
        population = new_generation(population, crossover_rate, mutation_rate, number_of_parents, retention_size)
        fitness = calculate_fitness(population)
        ranking, fitness_values = rank_routes(fitness)
        fd = 1 / fitness_values[0]
        final_dist = min(fd,final_dist)
        if(fd == final_dist):
          fafa = population[ranking[0]]
    
    return final_dist,fafa


dist, best_route = genetic_algorithm(fname = 'input.txt', population_size=300, crossover_rate=0.4, mutation_rate = 0.7, number_of_parents=250, generations=100)

with open('output.txt', 'w') as f:
    f.writelines(str(dist))
    f.write('\n')
    for i in best_route:
      f.write(str(i[0]))
      f.write(' ')
      f.write(str(i[1]))
      f.write(' ')
      f.write(str(i[2]))
      f.write(' ')
      f.write('\n')
