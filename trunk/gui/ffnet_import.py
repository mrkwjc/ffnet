from ffnet import *


ffnet_orig = ffnet
# For <= ffnet08 replace multiprocessing methods
class ffnet(ffnet):
    def _train_tnc_mp(self, input, target, nproc = None, **kwargs):
        """
        Parallel training with TNC algorithm

        Standard multiprocessing package is used here.
        """
        #register training data at mpprop module level
        # this have to be done *BEFORE* creating pool
        from ffnet import _mpprop as mpprop
        try: key = max(mpprop.nets) + 1
        except ValueError: key = 0  # uniqe identifier for this training
        mpprop.nets[key] = self
        mpprop.inputs[key] = input
        mpprop.targets[key] = target

        # create processing pool
        from multiprocessing import Pool, cpu_count
        import sys
        if nproc is None: nproc = cpu_count()
        if sys.platform.startswith('win'):
            # we have to initialize processes in pool on Windows, because
            # each process reimports mpprop thus the registering
            # made above is not enough
            # WARNING: this might be slow and memory hungry
            # (no shared memory, all is serialized and copied)
            initargs = [key, self, input, target]
            pool = Pool(nproc, initializer = mpprop.initializer, initargs=initargs)
        else:
            pool = Pool(nproc)
        
        # save references for later cleaning
        self._mppool = pool
        self._mpprop = mpprop
        self._mpkey = key
        
        # generate splitters for training data
        splitters = mpprop.splitdata(len(input), nproc)

        # train
        func = mpprop.mpfunc
        fprime = mpprop.mpgrad

        #if 'messages' not in kwargs: kwargs['messages'] = 0
        #if 'bounds' not in kwargs: kwargs['bounds'] = ((-100., 100.),)*len(self.conec)
        from scipy import optimize
        res = optimize.fmin_tnc(func, self.weights, fprime = fprime, \
                                args = (pool, splitters, key), **kwargs)
        self.weights = res[0]

        # clean mpprop and pool
        self._clean_mp()


    def _clean_mp(self):
        pool = self._mppool
        mpprop = self._mpprop
        key = self._mpkey
        # clean mpprop
        del mpprop.nets[key]
        del mpprop.inputs[key]
        del mpprop.targets[key]
        del self._mpprop  # we do not want to keep this
        del self._mpkey
        # terminate and remove pool
        pool.terminate()
        del pool
        del self._mppool  # if not removed this class couldn't be pickled!

nums = [int(n) for n in version.split('.')]
if nums[1] > 8 or (nums[1] == 8 and nums[2] > 0):
    ffnet = ffnet_orig
