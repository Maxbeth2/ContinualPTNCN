import time as t

class BeatSampler:
    """
        Samples whatever value occurs at a beat defined by a fixed interval
    """
    def __init__(self, bpm=120, tolerance_ms=50, sample_interval_ms=5):
        self.interval_ms = (1 /(bpm / 60)) * 1000
        self.data = []
        self.raw = []
        self.last_time = t.time()
        self.currval = 0
        # tolerance_ms milliseconds corresponds to n entries
        self.tolerance_windowsize = 0

    def sample(self, samp):
        self.raw.append((samp, t.time()))
        if abs(t.time() - self.last_time) > self.interval:
            self.data.append((samp, t.time()))
            self.currval = samp
            return True
        return False
    


    def sample_and_transfer(self, samp, pipe):
        pass

# class AvgSampler:
#     """
#         Waits a given amount of ms and samples 
#     """
#     def __init__(self):
#         pass

#     def sample(self):
#         pass

# print(t.ctime(t.time()))