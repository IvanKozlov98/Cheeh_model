from model import Model
import time


if __name__ == '__main__':
    s = time.time()
    model = Model()
    e = time.time()
    print(f"Time: {e-s}")
    # model.run(debug_mode=True)

