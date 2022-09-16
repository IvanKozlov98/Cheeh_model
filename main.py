from model import Model
import time
import numpy as np


if __name__ == '__main__':
    np.random.seed(42)
#    s = time.time()
    model = Model()
    # e = time.time()
    # print(f"Time: {e-s}")
    model.run(debug_mode=True)

