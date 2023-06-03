import ema

class DisplayRange:
    '''
    Tracks inputs and attempts to choose a reasonable normalization for groups of numbers over time
    '''

    def __init__(self, num_groups):
        self.num_groups = num_groups
        self.last_max_group_power = [0] * self.num_groups
        self.last_min_group_power = [1 << 16] * self.num_groups
        self._mean_group_power_ema = []
        for i in range(0, num_groups):
            self._mean_group_power_ema.append(ema.EMA(500, 1.5))

    def add(self, group):
        '''
        There is some magic here.  The device exists in an environment with variable amount of noise.  We want the
        display to be relative to the ambient noise level.  So we track the min/max values, but have them slowly
        decay to the mean power level.  We also use the current group power to adjust the min/max if they exceed
        the current min/max values.
        '''
        if len(group) != self.num_groups:
            raise ValueError("Expected group length to match num_groups")

        for i, group_power in enumerate(group):
            self._mean_group_power_ema[i].add(group_power)

            self.last_min_group_power[i] = min(self.last_min_group_power[i] * 1.0005, group_power,
                                               self._mean_group_power_ema[i].ema_value)  # Slowly decay min/max
            self.last_max_group_power[i] = max(self.last_max_group_power[i] * .999, group_power,
                                               self._mean_group_power_ema[i].ema_value)

    def get_group_minmax(self, i) -> tuple(float, float):
        '''returns min/max values based on observed values'''
        min_val = self.last_min_group_power[i] * 1.05  # Use the last min/max value before updating them
        max_val = self.last_max_group_power[i] * 0.95
        return min_val, max_val