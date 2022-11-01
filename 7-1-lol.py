import RPi.GPIO as GPIO
import time
from dec2bin import d2b
import matplotlib.pyplot as plt

dac = [26, 19, 13, 6, 5, 11, 9, 10]
leds = [21, 20, 16, 12, 7, 8, 25, 24]
comp = 4
troyka = 17
max_voltage = 3.3

GPIO.setmode(GPIO.BCM)
GPIO.setup(dac, GPIO.OUT)
GPIO.setup(leds, GPIO.OUT)
GPIO.setup(troyka, GPIO.OUT)
GPIO.setup(comp, GPIO.IN)

def adc():
    for i in range(0, 2 ** len(dac)):
        GPIO.output(dac, d2b(i))
        time.sleep(0.001)
        if GPIO.input(comp) == 0:
            return i
    raise ValueError

def adc_bin():
    result = 0
    for i in range(len(dac) - 1, -1, -1):
        result += 2 ** i
        GPIO.output(dac, d2b(result))
        time.sleep(0.005)
        if GPIO.input(comp) == 0:
            result -= 2 ** i
    return result

try:
    data = []
    start = time.time()

    GPIO.output(troyka, 1)
    while True:
        digital_volt = adc_bin()
        GPIO.output(leds, d2b(digital_volt))
        voltage = digital_volt / 2 ** len(dac) * max_voltage
        data.append(voltage)
        print(voltage)
        if voltage / max_voltage > 0.97:
            break

    GPIO.output(troyka, 0)
    while True:
        digital_volt = adc_bin()
        GPIO.output(leds, d2b(digital_volt))
        voltage = digital_volt / 2 ** len(dac) * max_voltage
        data.append(voltage)
        print(voltage)
        if voltage / max_voltage < 0.02:
            break
    
    end = time.time()

    measures = range(1, len(data) + 1)
    figure, ax = plt.subplots()
    ax.plot(measures, data)
    ax.set_xlabel('N')
    ax.set_ylabel('voltage')

    time_duration = end - start
    measurment_time = time_duration / len(data)
    sampling_frequency = 1 / measurment_time
    quantization_step = max_voltage / 2 ** len(leds)
    print("Experiment duration: {}, one measurment took this long: {}".format(time_duration, measurment_time))
    print("Sampling frequency: {}, quantization step: {}".format(sampling_frequency, quantization_step))

    with open("data.txt", "w") as file:
        file.write("\n".join([str(measure) for measure in data]))
    with open("settings.txt", "w") as file:
        file.write(str(sampling_frequency))
        file.write("\n")
        file.write(str(quantization_step))

    plt.show()

finally:
    GPIO.output(dac, 0)
    GPIO.output(leds, 0)
    GPIO.output(troyka, 0)
    GPIO.cleanup()
