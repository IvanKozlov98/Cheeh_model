from util import *

class Location:

    def __init__(self):
        self.id = get_random_id()
        self.population = 100
        # self.age_distrib = np.random.lognormal(3, 1, self.population) # norminvgauss.rvs(60, 1, size= self.population)
        #social status; gender