import tensorflow as tf

a = tf.ones([1,2]) * 2
b = tf.ones([1,2])


print(a)
print(b)

print(tf.add(a, b) / 2)