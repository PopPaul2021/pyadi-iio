import sys
import time
import adi
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import requests
import sys
import os

# device connections

ad3552r_1 = adi.ad3552r(uri="ip:169.254.99.22", device_name="axi-ad3552r")
ad3552r_2 = adi.ad3552r(uri="ip:169.254.52.216", device_name="axi-ad3552r")

# device configurations

ad3552r_1.tx_enabled_channels = [0]
ad3552r_2.tx_enabled_channels = [0]

ad3552r_1.tx_cyclic_buffer = True
ad3552r_2.tx_cyclic_buffer = True

# signal generation
fs = 3906250
# Signal frequency
fc = fs/160
# Number of samples
N = int(fs / fc)
# Period
ts = 1 / float(fs)
# Time array
t = np.arange(0, N * ts, ts)
# Sine generation
samples = signal.square(2 * np.pi * t * fc)
# Amplitude (full_scale / 2)
samples *= (2 ** 15) - 1
# Offset (full_scale / 2)
samples += 2 ** 15
# conversion to unsigned int and offset binary
samples = np.uint16(samples)

samples = np.bitwise_xor(32768, samples)


print("sample rate:", ad3552r_1.sample_rate)
print("Sample data min:", samples.min())
print("Sample data max:", samples.max())

# available options: "0/2.5V", "0/5V", "0/10V", "-5/+5V", "-10/+10V"

ad3552r_1.output_range = "-10/+10V"
ad3552r_2.output_range = "-10/+10V"
print("output_range:ad3552r_1:", ad3552r_1.output_range)
print("output_range:ad3552r_2:", ad3552r_2.output_range)

# available options:"adc_input", "dma_input", "ramp_input"

ad3552r_1.input_source = "dma_input"
ad3552r_2.input_source = "dma_input"

print("input_source:dac:", ad3552r_1.input_source)
print("input_source:dac:", ad3552r_2.input_source)

ad3552r_1.tx(samples)
ad3552r_2.tx(samples)

# available options:"start_stream_synced", "start_stream", "stop_stream"

ad3552r_1.stream_status = "start_stream_synced"
ad3552r_2.stream_status = "start_stream_synced"

###### switch configuration #####

start_stream_file = "start_synced.xml"
stop_stream_file  = "stop_synced.xml"

#Datastore path

sysrepoPath_ses1 = "http://127.0.0.1:50000/SR_CopyDatabase.cgi?dest=running&file="
sysrepoPath_ses2 = "http://127.0.0.1:50001/SR_CopyDatabase.cgi?dest=running&file="

#absolute path of the config file

fileAbsPath = os.path.abspath(start_stream_file)

#send the request to sysrepo to load the config file

response = requests.get(sysrepoPath_ses1 + fileAbsPath)
response = requests.get(sysrepoPath_ses2 + fileAbsPath)

###### switch configuration #####

plt.suptitle("AD355R Samples data")
plt.plot(t,samples)
plt.xlabel("Samples")
plt.show()

ad3552r_1.stream_status = "stop_stream"
ad3552r_2.stream_status = "stop_stream"

ad3552r_1.tx_destroy_buffer()
ad3552r_2.tx_destroy_buffer()

fileAbsPath = os.path.abspath(stop_stream_file)
#send the request to sysrepo to load the config file
response = requests.get(sysrepoPath_ses1 + fileAbsPath)
response = requests.get(sysrepoPath_ses2 + fileAbsPath)
