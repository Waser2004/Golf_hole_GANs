import random

from procedural_golf_hole_generator import Golf_Hole_Generator
from tkinter import *
import timeit

root = Tk()
root.geometry("600x600+100+100")
canvas = Canvas(root, width=1000, height=1000)
canvas.place(x=-2, y=-2)

generator = Golf_Hole_Generator(canvas)


def code():
    generator.generate_hole(par=4, distance=420, dog_leg=55, visualise=True, seed=1)


execution_time_ms = timeit.timeit(code, number=1) * 1000
print(f"Execution time: {execution_time_ms} milliseconds")


root.mainloop()