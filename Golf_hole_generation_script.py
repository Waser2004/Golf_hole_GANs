import random
from procedural_golf_hole_generator import Golf_Hole_Generator
import time

generator = Golf_Hole_Generator()

start = time.time()
i = 0
loops = 10_000 - 2_390
while i < loops:
    print(f"Hole: {i + 1} / {loops}")
    random.seed(i)
    par = 4
    if par == 3:
        distance = random.randint(150, 220)
    elif par == 4:
        distance = random.randint(280, 420)
    else:
        distance = random.randint(450, 550)
    dogleg = random.randint(-distance//4, distance//4) if par != 3 else 0
    try:
        generator.generate_hole(par=par, distance=distance, dog_leg=dogleg, visualise=False, seed=i)
    except:
        loops += 1
    i += 1

print(time.time()-start)
