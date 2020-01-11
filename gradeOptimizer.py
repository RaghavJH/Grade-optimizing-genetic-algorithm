from constrainedRandom import *


def get_random_weight():
    """
    Select a random type of weight (used for mutation)
    :return: the string of the randomly selected weight
    """
    rand = random.randint(0, 2)
    if rand == 0:
        return rand, 'assignment'
    elif rand == 1:
        return rand, 'quiz'
    elif rand == 2:
        return rand, 'project'


class DNA:
    """
    Three weightings for the course that need to be adjusted
    Should be the grade achieved in each component (e.g. 80, 90, 70)
    """
    assignment_grade = -1
    quizzes_grade = -1
    project_grade = -1
    """
    Limits to each weight defined as variables
    """
    limits = {
        'assignment': (40, 60),
        'quiz': (10, 30),
        'project': (20, 40)
    }
    """
    Mutation rate by %
    """
    mutation_rate = 0.05

    def __init__(self, weights):
        self.weights = {
            'assignment': float(weights[0]),
            'quiz': float(weights[1]),
            'project': float(weights[2])
        }
        self.fitness = self.calculate_fitness()

    def calculate_fitness(self):
        """
        Calculates the fitness of the current DNA
        :return: the fitness (i.e. overall grade)
        """
        return \
            DNA.assignment_grade * self.weights['assignment'] + \
            DNA.quizzes_grade * self.weights['quiz'] + \
            DNA.project_grade * self.weights['project']

    def mate(self, dna):
        """
        Mate with another DNA object to create a child
        :param dna: the other parent
        :return: a DNA object (child) that is the cross over of both DNAs
        """
        new_assignment_weight = (self.weights['assignment'] + dna.weights['assignment']) / 2
        new_quizzes_weight = (self.weights['quiz'] + dna.weights['quiz']) / 2
        new_project_weight = (self.weights['project'] + dna.weights['project']) / 2
        return DNA([new_assignment_weight, new_quizzes_weight, new_project_weight])

    def mutate(self):
        """
        Mutate the DNA. Picks a random weight, modifies it by 10% (+ or -).
        Then, takes the difference of the new and old one and randomly modifies another weight
        (that is not the same) by -1 * the difference. If the constraints are not met,
        mutation is cancelled.
        :return: None
        """
        # 5% chance of mutation
        if random.uniform(0, 1) <= DNA.mutation_rate:
            random_index, random_weight = get_random_weight()
            limits = tuple(map(lambda x: x/100, DNA.limits[random_weight]))
            old_val = self.weights[random_weight]
            new_val_upper = old_val * 1.1
            new_val_lower = old_val * 0.9
            new_val = -1
            if new_val_upper <= limits[1]:
                new_val = new_val_upper
            elif new_val_lower >= limits[0]:
                new_val = new_val_lower

            # Make sure new value is not -1
            if new_val != -1:
                self.weights[random_weight] = new_val
                if not self.randomly_modify(-(new_val-old_val), random_index):
                    self.weights[random_weight] = old_val
                else:
                    self.fitness = self.calculate_fitness()

    def randomly_modify(self, increment, constraint_index):
        """
        Randomly modify a grade weight
        :param increment: the increment to modify by (can be negative)
        :param constraint_index: the index that shouldn't be modified
        :return: True if successful (i.e. within constraint), else False
        """
        i, to_modify = get_random_weight()
        while i == constraint_index:
            i, to_modify = get_random_weight()
        limits = tuple(map(lambda x: x/100, DNA.limits[to_modify]))
        change = self.weights[to_modify] + increment
        if limits[0] <= change <= limits[1]:
            self.weights[to_modify] = change
            return True

        return False

    def __repr__(self):
        """
        :return: the string format of the DNA object
        """
        return \
            f"DNA ({self.weights['assignment']}, {self.weights['quiz']}, {self.weights['project']}), Fit: {self.fitness}"


class Population:
    def __init__(self, pop_size, mutation_prob):
        """
        Initialize a population with the given population size
        :param pop_size: the size of the population
        :param mutation_prob: the probability of mutation
        """
        self.mutation_prob = mutation_prob
        self.pop = []
        self.create_first_generation(pop_size)
        self.best_dna = None
        self.generation = 1

    def create_first_generation(self, pop_size):
        """
        Creates the initial generation by randomly generating
        grade weights.
        :param pop_size: the size of the population
        :return: None
        """
        ranges = [DNA.limits['assignment'], DNA.limits['quiz'], DNA.limits['project']]
        cr = ConstrainedRandom(ranges, 100)
        for x in range(pop_size):
            reduced = list(map(lambda i: i/100, cr.next()))
            self.pop.append(DNA(reduced))

    def crossover(self):
        """
        Crosses over all current DNA to create a new population with better (higher fitness) children
        :return: None
        """
        # Create mating pool
        mating_pool = []
        best_dna = self.pop[0]
        if self.best_dna is None:
            self.best_dna = self.pop[0]
        for x in range(len(self.pop)):
            # record best DNA for generation
            if self.pop[x].fitness > best_dna.fitness:
                best_dna = self.pop[x]
            # record best DNA all time
            if self.pop[x].fitness > self.best_dna.fitness:
                self.best_dna = self.pop[x]
            fitness_smaller = int(self.pop[x].fitness / 10)
            for i in range(fitness_smaller):
                mating_pool.append(self.pop[x])

        print(f'Best of ALL TIME: {self.best_dna}')
        print(f'    Best DNA of generation {self.generation}: {best_dna}')
        # Create new population
        new_pop = []
        for x in range(len(self.pop)):
            parent_1 = random.choice(mating_pool)
            parent_2 = random.choice(mating_pool)
            child = parent_1.mate(parent_2)
            new_pop.append(child)

        self.pop = new_pop
        self.generation += 1

    def mutate(self):
        for x in range(len(self.pop)):
            self.pop[x].mutate()


# Set grades
DNA.assignment_grade = 73
DNA.quizzes_grade = 64
DNA.project_grade = 55

population = Population(500, 0.05)

# Keep running forever until user stops
while True:
    population.crossover()
    population.mutate()
