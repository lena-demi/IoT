# Для масштабируемости: реальная 1 секунда = 1 минуте эмулятора

from datetime import datetime, timedelta

import bus_stop
import bus
import emulators

min = 480 # Характеризует время в эмуляторе: [min]=[минуты], 480 минут = 8 ч - соответствует 8 утра
