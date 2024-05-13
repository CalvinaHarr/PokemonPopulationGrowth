import requests
import xlsxwriter
import random
import json

class Pokémon:
    def __init__(self, name):
        #gets the request information from the API
        self.name = name
        
        species_url = "https://pokeapi.co/api/v2/pokemon-species/" + name
        species_info = requests.get(species_url)
        species_data = json.loads(species_info.text)

        general_url = "https://pokeapi.co/api/v2/pokemon/" + name
        general_info = requests.get(general_url)
        general_data = json.loads(general_info.text)
        
        #determines the gender of this Pokémon
        #0 implies female, 1 implies male
        self.gender_rate = 1#species_data.get("gender_rate")
        gender_num = random.randint(1,8)
        self.gender = -1
        if(self.gender_rate > 0 and gender_num <= self.gender_rate):
            self.gender = 0
        else:
            self.gender = 1
        
        #self.egg_groups = species_data.get("egg_groups")

        #determines whether the pokémon is incubating an egg and the cycle it's on
        self.hatch_number = species_data.get("hatch_counter")
        self.held_egg = None #This is the egg that is held

        #gets the ability information, determining whether it has a heating ability
        self.abilities = general_data.get("abilities")
        self.heated = False

        for i in range(len(self.abilities)):
            if (self.abilities[i].get("ability").get("name") == "magma-armor" 
                or self.abilities[i].get("ability").get("name") == "flame-body" 
                or self.abilities[i].get("ability").get("name") == "steam-engine"):
                self.heated = True
        
    
    def __str__(self) -> str:
        return self.name + " " + self.gender
    
    def hasEgg(self) -> bool:
        if self.held_egg == None:
            return False
        else:
            return True
              
    #A Pokémon is holding an egg!
    def obtainEgg(self, egg):
        self.held_egg = egg

#Eggs are categorized by the name of the pokémon they hatch into
class Egg:
    def __init__(self, name):
        self.name = name
        self.cycle = 0
        #print(type(self.cycle))
        
    def addCycle(self):
        self.cycle += 1

    def hatch(self, name) -> Pokémon:
        return Pokémon(name)
    
    def __str__(self) -> str:
        return "Egg of " + self.name + ", current cycle: " + str(self.cycle)

#Starts a population of a number (base) of Pokémon (species)
#TODO throw an exception or cancel the program if the pokémon, can't breed, is genderless, or can only be one gender
def startPopulation(base: int, population: list[Pokémon], species_name: str) -> list[Pokémon]: 
    #determines the gender of every pokemon

    for i in range(base):
        new_pkmn = Pokémon(species_name)
        population.append(new_pkmn)
        
    return population

#Puts Pokémon into female-male pairs, leaving out any extras
def breed(population: list[Pokémon], eggs: list[Egg]):
    #checks to see if there is at least one male
    male_available = False
    for p in population:
        if p.gender == 1:
            male_available = True
            break
    #checks for eggs that are ready to hatch
    egg_index = 0
    for p in population:
        #print(p.hasEgg())
        if p.gender == 0:
            #Checks if conditions are right for egg to hatch
            if p.hasEgg() and p.held_egg.cycle >= p.hatch_number:
                #eggs.remove(p.held_egg)
                population.append(p.held_egg.hatch(p.name))
            elif (not p.hasEgg() and male_available):
                #this runs a 70% chance of getting an egg per cycle
                #TODO run a different chance for different species in the same egg group
                #print("trying to get an egg")
                breed_number = random.randint(1, 100)
                if breed_number <= 70:
                    p.obtainEgg(Egg(p.name))
                    eggs.append(p.held_egg)
                    eggs[egg_index] = p.held_egg
                    #print(eggs[index])
                    egg_index += 1

def runSimulation():    
    pkmn_name = "magikarp"#input("What Pokémon should we run this simulation with?\n")
    cycle_num = "20"#input("How many cycles should we run?\n")
    cycles = int(cycle_num)
    workbook = xlsxwriter.Workbook(pkmn_name + '(m-biased).xlsx')
    #TODO make it so that the sheet is the name of the Pokémon
    sheet = workbook.add_worksheet()

    #The independent variables we're keeping track of:
    #Pokémon population, females, males, eggs
    sheet.write(0, 0, "Cycle")
    sheet.write(0, 1, "Population")
    sheet.write(0, 2, "Females")
    sheet.write(0, 3, "Males")
    sheet.write(0, 4, "Eggs")
    
    #lists for tracking data
    pop = []
    pop = startPopulation(20, pop, pkmn_name)
    females = []
    males = []    
    eggs = []
    for c in range(1,cycles):
        sheet.write(c,0, str(c))
        breed(pop, eggs)
        sheet.write(c,1,len(pop))
        #gets all females
        females = [p for p in pop if p.gender == 0]
        sheet.write(c,2,len(females))
        #gets all males
        males = [p for p in pop if p.gender == 1]
        sheet.write(c,3,len(males))
        sheet.write(c,4,len(eggs))
        #adds cycles to all eggs
        for e in eggs:
            #print(e.cycle)
            e.addCycle()
    workbook.close()
runSimulation()
