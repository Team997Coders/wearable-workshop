import ulab.numpy as np


class IDisplay:
    def show(self, power_spectrum: np.array):
        raise NotImplementedError()
