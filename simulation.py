import random
import pygame
import math
import matplotlib.pyplot as plt

pygame.init()
clock = pygame.time.Clock()
WIN_WIDTH = 2000
WIN_HEIGHT = 1200
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

obj_positions = []
pressed_flag = False


class Observer:
    def __init__(self, plants, current_population):
        self.plants = plants
        self.deaths = 0
        self.average_age = 0
        self.current_population = current_population
        self.max_population = current_population
        self.plantList = []
        self.populationList = []
        self.average_ageList = []

    def death(self):
        self.deaths += 1
        self.current_population -= 1

    def birth(self):
        self.current_population += 1
        if self.max_population < self.current_population:
            self.max_population = self.current_population

    def plant(self, eaten):
        if eaten: self.plants -= 1
        else: self.plants += 1

    def age(self, l):
        age_sum = 0
        for person in obj_positions:
            if type(person) == Person:
                age_sum += person.age
        if l:
            self.average_age = int(age_sum / l)

    def report(self):
        info = pygame.font.SysFont("arial", 25)
        text = info.render(("current popul: " + str(self.current_population) + "     max popul: " + str(self.max_population) + "     plants: " + str(self.plants) + "     deaths: " + str(self.deaths) + "     average age: " + str(self.average_age)), 1, (0, 0, 0))
        return text

    def collect_data(self):
        self.plantList.append(self.plants)
        self.populationList.append(self.current_population)
        self.average_ageList.append(self.average_age)

    def show_data(self):
        plt.plot(self.populationList)
        plt.plot(self.plantList)
        plt.plot(self.average_ageList)
        plt.show()

    def button(self, bx, by, l, h, color_normal, color_activ, action):
        global pressed_flag
        if maus[0] > bx and maus[0] < bx + l and maus[1] > by and maus[1] < by + h:
            pygame.draw.rect(win, color_normal, (bx, by, l ,h))
            
            if klick[0] == 1 and pressed_flag == False:
                pressed_flag = True
                pygame.draw.rect(win, color_activ, (bx, by, l ,h))
                print(action)

            if klick[0] == 0:
                pressed_flag = False
                
        else:
            pygame.draw.rect(win, color_normal, (bx, by, l ,h))


class Plant:
    def __init__(self, x, y):
        self.food = 40
        self.x = x
        self.y = y

    # def spawn(self):
    #     if random.randint(0,100) < 1:
    #         obj_positions.append(Plant(random.randint(0,2000), random.randint(0,1200)))

    def action(self):
        pass
        # self.spawn()
    
class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y

      
class Person:
    def __init__(self, number, x, y):
        self.gender = random.randint(0,1)
        self.age = 0
        self.pregnant = 0
        self.number = number
        self.hunger = 60
        self.sight = 1200
        self.visible_objects = []
        self.x = x
        self.y = y
        self.velocity = 10
        self.points = 0

    def distance(self, objects):
        distance = math.sqrt(abs((objects.x - self.x)**2) + abs((objects.y - self.y)**2))
        return distance

    def gotTo(self, target, factor):
        dirvect = pygame.math.Vector2(target.x - self.x, target.y - self.y)
        if dirvect.x == 0 and dirvect.y == 0:
            dirvect.x += 1
        dirvect.normalize()

        if self.x != target.x and self.y != target.y:

            dirvect.scale_to_length(self.velocity*factor)
            self.x += round(dirvect.x, 0)
            self.y += round(dirvect.y, 0)

    def eat(self, Plant):
        self.hunger += Plant.food
        if Plant in self.visible_objects:
            self.visible_objects.remove(Plant)
            # print("Person", self.number, "has eaten a plant!")
        if Plant in obj_positions:
            obj_positions.remove(Plant)
            observer.plant(True)
        del Plant

    def scan(self):
        obj_unsorted = []
        self.visible_objects = []
        for objects in obj_positions:
            # distance of all objects on the map
            if self.distance(objects) <= self.sight:
                # add the object to visible objects if in sight range
                obj_unsorted.append((self.distance(objects),objects))
         
        tmp = sorted(obj_unsorted,key=lambda tup: tup[0])
        for sets in tmp:
            self.visible_objects.append(sets[1])

    def find_food(self):
        for food in self.visible_objects:
            if type(food) == Plant:
                if self.distance(food) <= 12:
                    self.eat(food)
                    break
                else:
                    self.gotTo(food, 1)
                    break

    def scout(self):
        w = random.randint(0,4)
        if w == 0 and self.x <= 2000: self.x += self.velocity 
        if w == 1 and self.x >= 0: self.x -= self.velocity 
        if w == 2 and self.y <= 1200: self.y += self.velocity 
        if w == 3 and self.x >= 0: self.y -= self.velocity 


    def dead(self):
        if self.hunger <= 0 or self.age > 80:
            print(self.number, " ist gestorben!")
            obj_positions.remove(self)
            observer.death()
            del self

    def mate(self):
        if self.gender == 1:
            for female in self.visible_objects:
                if type(female) == Person:
                    if female.gender == 0 and female.pregnant == 0:
                        self.gotTo(female, 2)
                        if self.distance(female) <= 12:
                            female.pregnant = 1
                            self.hunger -= 1
                            self.points += 10
                            obj_positions.append(Person(4, self.x+1, self.y))
                            observer.birth()
                            break
                        else:
                            self.find_food()
                            #self.gotTo(female, 2)    
        else: self.scout()


    def __repr__(self):
        return "Number: " + str(self.number) + "\nHunger: " + str(self.hunger) + "\nPosition: " + str(self.x) + ", " + str(self.y)

    def action(self):
        self.dead()
        self.age += 0.05
        self.hunger -= 0.3
        self.scan()

        if self.gender == 0:
            if self.pregnant is not 0:
                self.pregnant -= 0.003
                if self.pregnant <= 0.2:
                    self.pregnant = 0

        if self.hunger <= 60:
            self.find_food()
            
        else:
            self.mate()


def draw_simulation(obj):
    if type(obj) == Plant:
        pygame.draw.rect(win, (120, 120, 120), (obj.x, obj.y, 8, 8))
    else:
        if obj.gender == 1:
            pygame.draw.rect(win, (0, 0, 200), (obj.x, obj.y, 8, 8))
        else:
            pygame.draw.rect(win, (255, 105, 180), (obj.x, obj.y, 8, 8))
    
    pygame.draw.rect(win, (238, 207, 161), (0, WIN_HEIGHT-40, 2000, 40))
    win.blit(observer.report(), (0, WIN_HEIGHT-40))

    
def information():
    l = sum(isinstance(x, Person) for x in obj_positions)
    observer.age(l)
    #print("Personen: ", l)
    #print("Plants: ", len(obj_positions)-l)
    if l == 0:
        return False
    else: 
        return True

p1 = Person(1,100,100)
p1.gender = 1
p2 = Person(2,1000,200)
p2.gender = 0
p3 = Person(3, 500, 500)
p4 = Person(4, 600, 600)
pl1 = Plant(10,10)
pl2 = Plant(20, 24)
pl3 = Plant(80, 80)
pl4 = Plant(random.randint(0,2000), random.randint(0,1200))
pl5 = Plant(random.randint(0,1000), random.randint(0,1200))
pl6 = Plant(random.randint(0,1000), random.randint(0,1200))

obj_positions = [p1, p2, p3, p4, pl1, pl2, pl3, pl4, pl5, pl6]
observer = Observer(4, 6)

run = True
count = 0
while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # update observer informations
    if count >= 3000:
        run = information()
        #print(p1)
        observer.collect_data()
        count = 0

    ticks = clock.tick(60)
    count += ticks

    # background color
    win.fill((20, 120, 20))

    # food spawn
    if random.randint(0,100) < 12:
        obj_positions.append(Plant(random.randint(0,2000), random.randint(0,1200)))
        observer.plant(False)

    # actions and drawing
    for obj in obj_positions:
        obj.action()
        draw_simulation(obj)
    
    # buttons
    maus = pygame.mouse.get_pos()
    klick = pygame.mouse.get_pressed()
    observer.button(WIN_WIDTH/2, WIN_HEIGHT-35, 80, 30, (0,255,0), (255,0,0), "increase_vel")

    pygame.display.update()

# plot data
observer.show_data()
pygame.quit()