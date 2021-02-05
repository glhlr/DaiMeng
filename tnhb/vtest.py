import random
from visualdl import LogWriter
import ca

logdir='./temp'
logger = LogWriter(logdir,sync_cycle=10)
with logger.mode('train'):
    scalar0 = logger.scalar('scalar0')
for step in range(0,1000):
    scalar0.add_record(step,random.random())