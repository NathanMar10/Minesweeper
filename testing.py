import numpy as np
from autosweep_circuit import create_XOR_blocks

shape = (3, 3)
clicked = np.zeros(shape=shape)
adjacent = np.zeros(shape=shape)


clicked[1, 1] = 1
clicked[0, 1] = 2
adjacent[1, 1] = 1
if False:
    print(adjacent)
    print(clicked)
print(create_XOR_blocks(clicked, adjacent, 1, 1))