import analogio
import analogbufio
import array
import time
import ulab.numpy as np

def roll_buffer(buffer, amount: int) -> list:
    #new_buffer = [0] * (len(buffer) - amount)
    for i in range(len(buffer) - amount - 1, 0, -1):
        buffer[i] = buffer[i - amount]
    return buffer

def prepend_buffer(new_buffer, old_buffer) -> list:
    old_buffer[0:len(new_buffer)] = new_buffer
    return old_buffer
    #output = list(new_buffer)
    #output.extend(old_buffer)
    #return output

async def record_sample_array(adcbuf: analogbufio.BufferedIn, sample_size: int, sample_rate: int, buffer = None):
    if buffer is None:
        buffer = array.array("H", [0x0000] * sample_size)

    adcbuf.readinto(buffer)
    return buffer


async def record_sample_numpy(adc: analogio.AnalogIn, sample_size: int, sample_rate: int, buffer: np.array = None):
    #start = time.monotonic_ns()
    if buffer is None:
        buffer = np.zeros((sample_size))

    min_val = 1 << 16
    max_val = 0

    for i in range(0, sample_size-1):
        #print(f'{i}')
        value = adc.value
        buffer[i] = value
        min_val = value if value < min_val else min_val
        max_val = value if value > max_val else max_val

    #end = time.monotonic_ns()
    #elapsed_ns = end - start
    #print(f"Time to collect sample: {elapsed_ns / 1000000}ms sample_rate: {sample_size * (1 / (elapsed_ns / 1000000000))}")
    return buffer, min_val, max_val
