### Multiprocessing training example for ffnet ###

from ffnet import ffnet, mlgraph
from scipy import rand

# Generate random training data (large)
input = rand(10000, 10)
target = rand(10000, 1)

# Define net (large one)
conec = mlgraph((10,300,1))
net = ffnet(conec)

# Test training speed-up
# Note that the below *if* is necessary only on Windows
if __name__=='__main__':    
    from time import time
    from multiprocessing import cpu_count
    
    # Preserve original weights
    weights0 = net.weights.copy()
    
    print "TRAINING, this can take a while..."
    for n in range(1, cpu_count()+1):
        net.weights[:] = weights0  #Start always from the same point
        t0 = time()
        net.train_tnc(input, target, nproc = n, maxfun=50, messages=0)
        t1 = time()
        print '%s processes: %s s' %(n, t1-t0)

