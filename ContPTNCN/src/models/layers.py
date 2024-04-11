import tensorflow as tf
import sys
from utils.utils import gelu1, softmax, init_weights, gte, ltanh, d_relu6, standardize
import numpy as np

seed = 1234
tf.random.set_seed(seed=seed)
np.random.seed(seed)

sys.path.insert(0,'utils/')

class E:
    def __init__(self, sdim):
        self.e = tf.zeros([1,sdim])
        self.v = tf.zeros([1,sdim])
        self.v_tm = tf.zeros([1,sdim])

class Z:
    def __init__(self, sdim, act_fx="identity", init_type="normal"):
        self.sdim = sdim
        self.init_type = init_type
        
        self.L1 = 0.0
        self.beta = 0.2

        self.a = tf.zeros([1,sdim])
        self.f = tf.zeros([1,sdim])
        self.f_tm = tf.zeros([1,sdim])
        self.y = tf.zeros([1,sdim])

        self.e = E(sdim=sdim)

        def idt(inp):
            return inp

        if act_fx == "identity":
            self.act_fx = idt

    def set_parent(self, p):
        self.parent = p
        self.U = tf.Variable( init_weights(self.init_type, [p.sdim, self.sdim], stddev=0.025, seed=seed) )
        
    def set_child(self, c):
        self.child = c
        self.W = tf.Variable( init_weights(self.init_type, [self.sdim, c.sdim], stddev=0.025, seed=seed) )
        self.M = tf.Variable( init_weights(self.init_type, [c.sdim, self.sdim], stddev=0.025, seed=seed) )
        self.E = tf.Variable( init_weights(self.init_type, [c.sdim, self.sdim], stddev=0.025, seed=seed) )

    def pred(self, t=None, b=None):
        self.p = self.act_fx(tf.matmul(self.a, self.W)) # activate??
        # print(f"layer with dim {self.sdim}")
        print(self.y)

    def calc_err(self):
        self.e.e = tf.subtract(self.parent.p, self.f)
        # print(self.e.e)

    def corr(self):
        d = tf.matmul(self.child.e.e, self.E)
        if self.L1 > 0.0:
            d = tf.add(d, tf.sign(self.a) * self.L1)
        self.f_tm = self.y
        self.y = self.act_fx( tf.subtract(self.a, d * self.beta))
        # print(f"\n\nY:{self.y}\n\n")
        self.e.v_tm = self.e.v
        self.e.v = tf.subtract(self.f, self.y)


    def update(self, gamma=1.0, update_radius=1.0):
        local_d = []
        # W
        dW = tf.clip_by_norm(tf.matmul(self.f, self.child.e.e, transpose_a=True), update_radius)
        local_d.append(dW)
        # E
        dW = None
        dW = tf.matmul(self.child.e.e, tf.subtract(self.e.v, self.e.v_tm), transpose_a=True) * -gamma
        dW = tf.clip_by_norm(dW, update_radius)
        local_d.append(dW)
        # M
        dW = None
        dW = tf.matmul(self.child.f_tm, self.e.v, transpose_a=True)
        dW = tf.clip_by_norm(dW, update_radius)
        local_d.append(dW)
        # V
        dW = None
        dW = tf.matmul(self.f_tm, self.e.v, transpose_a=True) 
        dW = tf.clip_by_norm(dW, update_radius)
        local_d.append(dW)
        # print("ld:",local_d)
        return local_d


    def set_val(self, val):
        self.f = val



class ZT(Z):
    def __init__(self, sdim, init_type="normal"):
        super().__init__(sdim=sdim)
        self.V = tf.Variable( init_weights(self.init_type, [sdim, sdim], stddev=0.025, seed=seed) )
        self.M = None
        self.W = None
        self.E = None

    def pred(self):
        self.a = tf.add(tf.matmul(self.y, self.V), tf.matmul(self.child.y, self.M))
        super().pred(self)
    
    def calc_err(self):
        pass

    def corr(self):
        super().corr()
    
    def update(self):
        return super().update()



class ZZ(Z):
    def __init__(self, sdim, init_type="normal"):
        super().__init__(sdim=sdim)
        self.V = tf.Variable( init_weights(self.init_type, [sdim, sdim], stddev=0.025, seed=seed) )
        self.M = None
        self.U = None
        self.W = None
        self.E = None

    def pred(self):
        self.a = tf.add(
            tf.add(
                tf.matmul(self.child.y, self.M),
                tf.matmul(self.parent.y, self.U)
            ),
            tf.matmul(self.y, self.V),
            )
        self.p = tf.matmul(self.a, self.W)
        super().pred(self)

    def calc_err(self):
        super().calc_err()

    def corr(self):
        super().corr()
    
    def update(self, update_radius=1.0):
        local_d = super().update()
        dW = None
        dW = tf.matmul(self.parent.f_tm, self.e.v, transpose_a=True)
        dW = tf.clip_by_norm(dW, update_radius)
        local_d.append(dW)
        return local_d
        # U



class ZB(Z):
    def __init__(self, sdim,init_type="normal"):
        super().__init__(sdim=sdim)
        # no params

    def pred(self):
        pass
    
    def calc_err(self):
        super().calc_err()

    def corr(self):
        # self.f_tm = self.y
        pass
    
    def update(self):
        return []

        
