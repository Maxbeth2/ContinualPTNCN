import os
#os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"]="2"
"""
Trains a P-TNCN as a discrete token prediction model -- forecasting over sequences
of one-hot encoded integer symbols.
Implementation of the proposed model in Ororbia et al., 2019 IEEE TNNLS.

@author: Ankur Mali

"""

import sys

sys.path.insert(0, 'models/')
sys.path.insert(0, 'utils/')

import tensorflow as tf
import numpy as np
from max_ptncn import PTNCN

seed = 1234
tf.random.set_seed(seed=seed)
np.random.seed(seed)

# train_fname = "../data/ptb_char/trainX.txt"
train_fname = "../data/recs/recordingA.npy"
out_dir = "../output/"#"/data_reitter/ago109/data/ptb_char/modelA/"
accum_updates = False
out_fun = "identity"
t_prime = 1 #0

# meta-parameters for model itself --> manhattan distance
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

out_dim = 1


def get_data():
    data = np.load(train_fname)
    max = np.amax(data)
    data = (data / max)
    datat = [i for i in range(data.shape[0])]
    return data, datat





model = PTNCN("ptncn", out_dim, hid_dim, wght_sd=wght_sd, err_wght_sd=err_wght_sd,act_fun=act_fun,out_fun=out_fun,in_dim=-1)
print(" Model.Complexity = {0} synapses".format(model.get_complexity()))



from plotting_process import PlottingProcess
from input_process import InputProcess

import multiprocessing as mp
from pynput import keyboard

data, datat = get_data()
preds = []
if __name__ == '__main__':
    snd, rec = mp.Pipe()

    isnd, irec = mp.Pipe()

    plot = PlottingProcess(input_pipe=rec)
    inpp = InputProcess(out_pipe=isnd)

    plot.start()
    inpp.start()
    t = 0
    # for t in range(len(data)):
    global confidence
    confidence = 0.0
    def on_press(key):
            global confidence
            try:
                # print(f"alphanumeric key {key.char} pressed")
                if key.char == 'o':
                    confidence = 1.0
                if key.char =='l':
                    confidence = 0.0
                # confidence = max(0.0, confidence)
                # confidence = min(1.0, confidence)
                print(f"c: {confidence}")
            except AttributeError:
                print(f"special key {key} pressed")

    def on_release(key):
        # print(f"{key} relesased")
        if key == keyboard.Key.esc:
            return False
        
    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release
    )
    listener.start()
    
    while True:
        for t in range(len(datat)):
            # if irec.poll():
            #     idat = irec.recv()
            #     idat -= 97
            #     idat /= (257 - 97)
                # print(idat)
                # model.set_confidence(confidence)
                # x_t = tf.expand_dims([idat], axis=0)
            x_t = tf.expand_dims([data[t]], axis=0)
            x_logits, x_mu = model.forward(x_t, is_eval=False, beta=beta, alpha=alpha_e)
            preds.append(x_mu)
            # print(x_mu.numpy()[0])
            datadict = {"x": x_t.numpy()[0][0], "mu": x_mu.numpy()[0][0]}
            # snd.send(x_mu.numpy()[0][0])
            snd.send(datadict)



            if t >= t_prime and confidence < 0.5:
                delta = model.compute_updates(gamma=gamma, update_radius=update_radius)
                N_mb = x_t.shape[0]
                for p in range(len(delta)):
                    print(delta[p])
                    delta[p] = delta[p] * (1.0/(N_mb * 1.0))
                    exit()

                if accum_updates == False:
                    optimizer.apply_gradients(zip(delta, model.param_var))
        t+=1
        model.clear_var_history()




                # if w_decay > 0.0:
                #     for p in range(len(delta)):
                #         delta_var = delta[p]
                #         delta[p] = tf.subtract(delta_var,(delta_var * w_decay))
                # if param_radius > 0.0:
                #     for p in range(len(model.param_var)):
                #         old_var = model.param_var[p]
                #         old_var.assign(tf.clip_by_norm(old_var, param_radius, axes=[1]))



    # import matplotlib.pyplot as plt
    # preds = np.reshape(np.array(preds),(len(datat)))

    # plt.plot(datat, preds)
    # plt.plot(datat, data)
    # plt.show()





