import math
import random
import numpy as np
import sys
import re

def parse_arg():

    ### default parameter ###
    tsp = "rl11849.tsp"
    num_population = 100
    num_generation = 3000

    num_elite = 30
    num_parent = 5
    selection = "lr"
    linear_raking_parameter = 2.0
    mutate_rate = 0.2
    ##########################

    argv = sys.argv

    tsp = argv[1]

    for i in range(2, len(argv), 2):
        if(argv[i] == "-p"):
            assert re.match("\d", argv[i+1]), "population must be non-negative integer"
            num_population = int(argv[i+1])
        elif(argv[i] == "-f"):
            assert re.match("\d", argv[i+1]), "number of fitness evaluate limit must be non-negative integer"
            num_generation = int(argv[i+1])
        else :
            raise Exception("Not a valid parameter")

        
    return "./"+tsp, num_population, num_generation, selection, num_parent, num_elite, linear_raking_parameter, mutate_rate


### load tsp file and return tuple (number, x, y)
def load_tsp(filename):
    with open(filename, 'r') as f:
        cities = []
        # remove metadata
        while True:
            l = f.readline()
            city = l.strip().split()
            if(city[0] == "1"):
                cities.append((int(city[0]), float(city[1]), float((city[2]))))
                break
        for l in f:
            city = l.strip().split()
            if city[0] == "EOF":
                break
            cities.append((int(city[0]), float(city[1]), float((city[2]))))
        
    return np.array(cities)

## calculate travel distance of route
def dist(route):
    ret = 0

    start = route[:]
    dest = np.roll(route, 1, axis=0)

    diff = np.subtract(cities[start, 1:3], cities[dest, 1:3])
    
    return np.sum(np.sqrt(np.sum(np.square(diff), axis=1)))

def crossover(p1, p2):

    cut1, cut2 = np.random.randint(0, len_city), np.random.randint(0, len_city)
    while(cut1 == cut2) : cut2 = np.random.randint(0, len_city)
    if(cut1 > cut2) : cut1, cut2 = cut2, cut1

    crossing_route = travel_route[p1, cut1:cut2]
    missing_route = travel_route[p2, np.isin(travel_route[p2], crossing_route, invert=True)]

    crossing_route2 = travel_route[p2, cut1:cut2]
    missing_route2 = travel_route[p1, np.isin(travel_route[p1], crossing_route2, invert=True)]
    
    return np.vstack((np.concatenate((crossing_route, missing_route)), np.concatenate((crossing_route2, missing_route2))))


def mutate(route, p):
    mutant = route[p, :]
    g1, g2 = np.random.randint(0, len_city-1), np.random.randint(0, len_city-1)
    mutant[g1], mutant[g2] = mutant[g2], mutant[g1] 
    return mutant


##################
###    main    ###
##################

tsp, num_population, num_generation, selection, num_parent, num_elite, linear_raking_parameter, mutate_rate = parse_arg()
cities = load_tsp(tsp)
len_city = len(cities)

## initial population
travel_route = np.random.choice(range(len_city), len_city, replace=False)
for i in range(num_population-1):
    travel_route = np.vstack((travel_route, np.random.choice(range(len_city), len_city, replace=False)))
## load population
'''
travel_route = np.loadtxt("solution.csv", delimiter=",", dtype=np.float)
travel_route = travel_route.astype(int)
'''

gene = 0
while gene < num_generation:

    gene += 1

    ### evaluate distance of individual
    dist_route = np.zeros(num_population)

    for r, j in enumerate(travel_route):
        dist_route[r] = dist(j)

    ### fitness function
    fitness = 1 / dist_route

    ### Selection Operators

    ranking = np.argsort(dist_route)

    if(selection == "fw"):
        # fps windowing
        proba = fitness - np.min(fitness)

    elif(selection == "fs"):
        # fps sigma scaling
        fps_mean = np.mean(fitness)
        fps_std = np.std(fitness)
        proba = np.max(np.vstack((fitness - (fps_mean - fps_std * 2), np.zeros(num_population))), axis=0)
    elif(selection == "lr"):
        # linear ranking selection
        proba = (2-linear_raking_parameter) / num_population + 2 * ranking * (linear_raking_parameter - 1) / (num_population-1) * num_population
    elif(selection == "er"):
        # exponential ranking selection
        proba = (1 - math.e ** -ranking) / np.sum(1 - math.e ** - ranking)
    
    ### Select Fitter Individuals as Parents
    parent = np.zeros(num_parent)
    
    ### Stochastic Universal Sampling
    current_mem = k = 0
    proba = proba / np.sum(proba)
    r = 1 / (num_parent+1)
    pointer0 = np.random.random() * r

    while current_mem < num_parent :
        while r <= sum(proba[:k+1]):
            parent[current_mem] = k 
            r += 1 / num_parent
            current_mem += 1
        k += 1

    ### create Offsprings from parents
    offsprings = travel_route[ranking[:num_elite]]

    for j in range((num_population - num_elite)//2):
        p1, p2 = random.randint(0, num_parent-1), random.randint(0, num_parent-1)
        while(p1 == p2): p2 = random.randint(0, num_parent-1)

        offsprings = np.vstack((offsprings, crossover(p1, p2)))
    if(len(offsprings) != num_population): 
        offsprings = np.vstack((offsprings, travel_route[ranking[num_elite]]))

    ## mutate offsprings
    for j in range(num_population):
        if(random.random() < mutate_rate): offsprings[j] = mutate(offsprings, j)

    ## form next generation of population
    travel_route = offsprings[:]

    #print("[%d] [%f]"%(gene, np.min(dist_route)))

sol = travel_route[np.argmin(dist_route)] + 1
np.savetxt("solution.csv", sol.reshape(-1, 1), delimiter=",", fmt="%d")

