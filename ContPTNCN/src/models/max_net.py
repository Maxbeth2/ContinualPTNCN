from models.model_utils.layers import *

import matplotlib.pyplot as plt

opt_type = "nag" #"sgd" # "nag"
alpha = 0.075
momentum = 0.95 # 0.99
update_radius = 1.0
param_radius = -30 #50 #-25.0 #-1.0
w_decay = -0.0001
hid_dim = 25 #250
wght_sd = 0.05
err_wght_sd = 0.05
beta = 0.1
gamma = 1
act_fun = "tanh"
alpha_e = 0.001 # set according to IEEE paper


###########################################################################################################
# initialize the program
###########################################################################################################
moment_v = tf.Variable( momentum )
alpha_v  = tf.Variable( alpha )

# prop up the update rule (or "optimizer" in TF lingo)
if opt_type == "nag":
    optimizer = tf.compat.v1.train.MomentumOptimizer(learning_rate=alpha_v,momentum=moment_v,use_nesterov=True)
elif opt_type == "momentum":
    optimizer = tf.compat.v1.train.MomentumOptimizer(learning_rate=alpha_v,momentum=moment_v,use_nesterov=False)
elif opt_type == "adam":
    optimizer = tf.compat.v1.train.AdamOptimizer(learning_rate=alpha_v)
elif opt_type == "rmsprop":
    optimizer = tf.compat.v1.train.RMSPropOptimizer(learning_rate=alpha_v)
else:
    optimizer = tf.compat.v1.train.GradientDescentOptimizer(learning_rate=alpha_v)


class PTNCN_MAX:
    '''0th layer = top layer\n
    -1th layer = input layer\n
    self.layers[n]'''
    def __init__(self, lrs, gamma=0.1, beta=0.1, out_fx="softmax"):
        self.in_dim = lrs[-1]
        self.layers = []

        self.gamma = gamma
        self.beta = beta

        self.layers.append(ZT(sdim=lrs[0]))
        for lr in range(1, len(lrs)-1):
            self.layers.append(ZZ(sdim=lrs[lr]))
        self.layers.append(ZB(sdim=lrs[-1]))

        for lr in range(1, len(self.layers)):
            self.layers[lr].set_parent(self.layers[lr-1])

        for lr in range(0, len(self.layers)-1):
            self.layers[lr].set_child(self.layers[lr+1])

        self.param_var = []
        lr = self.layers[0]
        lr : ZT
        self.param_var.append(lr.W)
        self.param_var.append(lr.E)
        self.param_var.append(lr.M)
        self.param_var.append(lr.V)
        for l in range(1, len(lrs)-1):
            lr = self.layers[l]
            self.param_var.append(lr.W)
            self.param_var.append(lr.E)
            self.param_var.append(lr.M)
            self.param_var.append(lr.V)
            self.param_var.append(lr.U)

        if out_fx == "softmax":
            self.out_fx = softmax
            

    def _set_input(self, inp):
        lr = self.layers[-1]
        lr: Z
        lr.set_val(inp)
    
    def _fwd(self):
        for lr in self.layers[:-1]:
            lr: Z
            lr.beta = self.beta
            lr.gamma = self.gamma
            lr.pred()
            # print("a")
        return self.layers[-1].pred()

    def _calc_errs(self):
        for lr in self.layers:
            lr: Z
            lr.calc_err()

    def _corr(self):
        for lr in self.layers:
            lr: Z
            lr.corr()

    def _update(self):
        delta = []
        for lr in self.layers:
            lr: Z
            for d in lr.update():
                delta.append(d)
        N_mb = self.in_dim
        for p in range(len(delta)):
            delta[p] = delta[p] * (1.0/(N_mb * 1.0))
        optimizer.apply_gradients(zip(delta, self.param_var))

    def step(self, inp=tf.constant([[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])):
        self._set_input(inp=inp)
        x_mu = self._fwd()

        self._calc_errs()
        self._corr()
        self._update()
        out_lr = self.layers[-2]
        out_lr : Z
        return x_mu


    def _settle(self, inp, K=5):
        self.set_input(inp)
        for k in range(K):
            self.fwd()
            self.calc_errs()
            self.corr()
        self.update()


# from models.model_utils.s_a import Sensor, Actuator
# ncn = PTNCN_MAX([20,20,9])

# # actuator = Actuator()
# # sensor = Sensor()


# while True:
#     pass

# # or try beta fluctuations




    
if __name__ == '__main__':
    ncn = PTNCN_MAX([20,20,9])
    print("start")
    ncn.step()
    print("done")
    # ncn.step()
    # ncn.step()
    # ncn.step()
    # ncn.step()
    exit()
            






# def collect_params(self):
#     """
#         Routine for collecting all synaptic weight matrix/vectors from
#         transformer model in a named dictionary (for norm printing)
#     """
#     theta = dict()
#     theta["W1"] = self.W1
#     theta["W2"] = self.W2
#     theta["E1"] = self.E1
#     theta["E2"] = self.E2
#     theta["M1"] = self.M1
#     theta["M2"] = self.M2
#     theta["U1"] = self.U1
#     theta["V1"] = self.V1
#     theta["V2"] = self.V2
#     return theta



# class PTNCN:
#     def __init__(self, name, x_dim, hid_dim, wght_sd=0.025, err_wght_sd=0.025,act_fun="tanh", init_type="normal",
#                  out_fun="identity",in_dim=-1,zeta=1.0): # constructor
#         self.name = name
#         self.act_fun = act_fun
#         self.hid_dim = hid_dim
#         self.x_dim = x_dim
#         self.L1 = 0 #0.002 # lateral neuron penalty to encourage sparsity in representations
#         self.init_type = init_type
#         self.standardize = False # un-tested
#         self.use_temporal_error_rule = True # Note: works better w/o temporal error rule in discrete-valued input space
#         self.zeta = zeta # leave zeta = 1
#         self.in_dim = x_dim

#         self.balance = np.array([1.0, 0.0])
#         self.state = STATE()
#         self.params = PARAMS(wght_sd=wght_sd, 
#                              err_wght_sd=err_wght_sd, 
#                              init_type=init_type, 
#                              hid_dim=hid_dim, 
#                              x_dim=x_dim)
        
#         self.act_fx = None
#         if self.act_fun == "gelu":
#             self.act_fx = gelu1
#         elif self.act_fun == "relu6":
#             self.act_fx = tf.nn.relu6
#         elif self.act_fun == "relu":
#             self.act_fx = tf.nn.relu
#         elif self.act_fun == "sigmoid":
#             self.act_fx = tf.nn.sigmoid
#         elif self.act_fun == "sign":
#             self.act_fx = tf.sign
#         elif self.act_fun == "tanh":
#             self.act_fx = tf.nn.tanh
#         elif self.act_fun == "ltanh":
#             self.act_fx = ltanh
#         else:
#             self.act_fx = gte

#         self.out_fx = tf.identity
#         if out_fun == "softmax":
#             self.out_fx = softmax
#         elif out_fun == "tanh":
#             self.out_fx = tf.nn.tanh
#         elif out_fun == "sigmoid":
#             self.out_fx = tf.nn.sigmoid
    
#     def set_confidence(self, c):
#         self.balance[1] = c
#         self.balance[0] = 1.0 - c


#     def forward(self, x, K=5, beta=0.2, alpha=1, is_eval=True):

#         x_ = tf.cast(x, dtype=tf.float32)
#         self.x_mu = tf.zeros([len(x), self.in_dim]) #x_ * 0
#         self.zf0_tm1 = tf.zeros([len(x), self.in_dim]) #x_ * 0
#         self.zf1_tm1 = tf.zeros([len(x), self.hid_dim])
#         self.zf2_tm1 = tf.zeros([len(x), self.hid_dim])
#         self.e1v_tm1 = tf.zeros([len(x), self.hid_dim])
#         self.e2v_tm1 = tf.zeros([len(x), self.hid_dim])
#         self.z1 = tf.zeros([len(x), self.hid_dim])
#         self.z2 = tf.zeros([len(x), self.hid_dim])
#         self.z3 = tf.zeros([len(x), self.hid_dim])
#         self.e1 = tf.zeros([len(x), self.hid_dim])
#         self.e2 = tf.zeros([len(x), self.hid_dim])
#         self.ex = self.zf0_tm1
            
            

#         # init states of variable at layer 0
#         # self.zf0 = x_ #tf.cast(tf.greater(x_, 0.0), dtype=tf.float32)
#         self.zf0 = tf.add(x_*self.balance[0], self.x_mu*self.balance[1])#tf.cast(tf.greater(x_, 0.0), dtype=tf.float32)

#         # compute new states
#         if self.zeta > 0.0:
#             self.z2 = tf.add(tf.matmul(self.zf1_tm1, self.M2), tf.matmul(self.zf2_tm1, self.V2))
#         else:
#             self.z2 = tf.matmul(self.zf2_tm1, self.V2)
#         #self.z2 = tf.add(tf.matmul(self.zf1_tm1, self.M2), tf.matmul(self.zf2_tm1, self.V2))
#         if self.standardize == True:
#             self.z2 = standardize( self.z2 )
#         self.zf2 = self.act_fx(self.z2)
#         z1_mu = tf.matmul(self.zf2, self.W2)

#         if self.zeta > 0.0:
#             self.z1 = tf.add(tf.add(tf.matmul(self.zf0_tm1, self.M1), tf.matmul(self.zf2_tm1, self.U1)), tf.matmul(self.zf1_tm1, self.V1))
#         else:
#             self.z1 = tf.add(tf.matmul(self.zf0_tm1, self.M1), tf.matmul(self.zf1_tm1, self.V1))
#         if self.standardize == True:
#             self.z1 = standardize( self.z1 )
#         self.zf1 = self.act_fx(self.z1)
#         x_logits = tf.matmul(self.zf1, self.W1)
#         self.x_mu = self.out_fx( x_logits ) #tf.nn.sigmoid( x_logits )

#         # compute local errors and state perturbations
#         self.e1 = tf.subtract(z1_mu, self.zf1)# * m
#         self.ex = tf.subtract(self.x_mu, self.zf0)# * m
        
#         d2 = tf.matmul(self.e1, self.E2)
#         d1 = tf.subtract(tf.matmul(self.ex, self.E1), self.e1 * alpha)
#         if self.L1 > 0.0:# inject the weak lateral sparsity prior here
#             d2 = tf.add(d2, tf.sign(self.z2) * self.L1)
#             d1 = tf.add(d1, tf.sign(self.z1) * self.L1)
#         # compute state targets
#         self.y2 = self.act_fx( tf.subtract(self.z2, d2 * beta) )
#         self.y1 = self.act_fx( tf.subtract(self.z1, d1 * beta) )
#         # compute temporal weight corrections
#         self.e2v = tf.subtract(self.zf2, self.y2)# * m
#         self.e1v = tf.subtract(self.zf1, self.y1)# * m

#         '''
#         # no need to waste the multiplications to mask these out as only the error neurons drive weight updates in this case
#         self.y1 = self.y1 * m
#         self.y2 = self.y2 * m
#         self.zf1 = self.zf1 * m
#         self.zf2 = self.zf2 * m
#         '''

#         return x_logits, self.x_mu

#     def compute_updates(self, gamma=1.0, update_radius=-1.0):
#         """
#             Computes the perturbations needed to adjust P-TNCN's synaptic weight parameters
#         """
#         delta_list = []
#         # W1
#         dW = tf.matmul(self.zf1, self.ex, transpose_a=True)
#         if update_radius > 0.0:
#             dW = tf.clip_by_norm(dW, update_radius)
#         delta_list.append(dW)

#         # E1
#         if self.use_temporal_error_rule == True:
#             dW = None
#             dW = tf.matmul(self.ex, tf.subtract(self.e1v, self.e1v_tm1), transpose_a=True) * -gamma
#         else:
#             dW = tf.transpose(dW) * gamma
#         if update_radius > 0.0:
#             dW = tf.clip_by_norm(dW, update_radius)
#         delta_list.append(dW )

#         # W2
#         dW = None
#         dW = tf.matmul(self.zf2, self.e1v, transpose_a=True)
#         if update_radius > 0.0:
#             dW = tf.clip_by_norm(dW, update_radius)
#         delta_list.append(dW )

#         # E2
#         if self.use_temporal_error_rule == True:
#             dW = None
#             dW = tf.matmul(self.e1, tf.subtract(self.e2v, self.e2v_tm1), transpose_a=True) * -gamma
#         else:
#             dW = tf.transpose(dW) * gamma
#         if update_radius > 0.0:
#             dW = tf.clip_by_norm(dW, update_radius)
#         delta_list.append(dW )

#         if self.zeta > 0.0:
#             # U1
#             dW = None
#             dW = tf.matmul(self.zf2_tm1, self.e1v, transpose_a=True)
#             if update_radius > 0.0:
#                 dW = tf.clip_by_norm(dW, update_radius)
#             delta_list.append(dW )

#         # M1
#         dW = None
#         dW = tf.matmul(self.zf0_tm1, self.e1v, transpose_a=True)
#         if update_radius > 0.0:
#             dW = tf.clip_by_norm(dW, update_radius)
#         delta_list.append(dW )
#         # M2
#         dW = None
#         dW = tf.matmul(self.zf1_tm1, self.e2v, transpose_a=True)
#         if update_radius > 0.0:
#             dW = tf.clip_by_norm(dW, update_radius)
#         delta_list.append(dW )

#         # V1
#         dW = None
#         dW = tf.matmul(self.zf1_tm1, self.e1v, transpose_a=True)
#         if update_radius > 0.0:
#             dW = tf.clip_by_norm(dW, update_radius)
#         delta_list.append(dW )

#         # V2
#         dW = None
#         dW = tf.matmul(self.zf2_tm1, self.e2v, transpose_a=True)
#         if update_radius > 0.0:
#             dW = tf.clip_by_norm(dW, update_radius)
#         delta_list.append(dW )

#         return delta_list

#     def clear_var_history(self):
#         """
#             Variable-clearing function -- helps to reset P-TNCN state to NULL for new disjoint sequences,
#             otherwise, the model will continue to update its stateful dynamical variables
#         """
#         self.zf0 = None
#         self.zf1 = None
#         self.zf2 = None
#         self.zf0_tm1 = None
#         self.zf1_tm1 = None
#         self.z1 = None
#         self.z2 = None
#         self.y1 = None
#         self.y2 = None
#         self.ex = None
#         self.e1 = None
#         self.e1v = None
#         self.e2v = None
#         self.e1v_tm1 = None
#         self.e2v_tm1 = None
#         self.x = None
