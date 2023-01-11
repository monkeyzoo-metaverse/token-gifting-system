import logging
from logging.handlers import TimedRotatingFileHandler
import datetime


filename = "log" + str(datetime.datetime.now()) + ".log"
#f_handler = TimedRotatingFileHandler("./logs/"+filename, when='h', interval=3)
f_handler = logging.FileHandler("./logs/" + filename)
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s in %(filename)s %(funcName)s')

c_handler = logging.StreamHandler()
c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s in %(filename)s %(funcName)s')

d_handler = logging.StreamHandler()

c_handler.setLevel(logging.WARNING)
f_handler.setLevel(logging.DEBUG)

c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

log = logging.getLogger()

log.setLevel(logging.INFO)
log.addHandler(f_handler)
log.addHandler(c_handler)
#log.addHandler(d_handler)

log.info('Logging setup') 
