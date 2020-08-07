import pywt
import pywt.data
import matplotlib.pyplot as plt
import numpy as np


matrix = pywt.dwt([1, 2, 3,4], 'db6')
result = pywt.idwt(cA=matrix[0],cD=matrix[1],wavelet='db6')
print(result)
