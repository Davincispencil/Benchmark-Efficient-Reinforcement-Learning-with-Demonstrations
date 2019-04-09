import tensorflow as tf
from common.models import get_network_builder

def leakyrelu(x, alpha=0.3, max_value=None):  #alpha need set
    '''ReLU.

    alpha: slope of negative section.
    '''
    negative_part = tf.nn.relu(-x)
    x = tf.nn.relu(x)
    if max_value is not None:
        x = tf.clip_by_value(x, tf.cast(0., dtype=tf.float32),
                            tf.cast(max_value, dtype=tf.float32))
    x -= tf.constant(alpha, dtype=tf.float32) * negative_part
    return x


class Model(object):
    def __init__(self, name, network='mlp', **network_kwargs):
        self.name = name
        self.network_builder = get_network_builder(network)(**network_kwargs)

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope=self.name)

    @property
    def trainable_vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

    @property
    def perturbable_vars(self):
        return [var for var in self.trainable_vars if 'LayerNorm' not in var.name]


class Actor(Model):
    def __init__(self, nb_actions, name='actor', network='mlp', **network_kwargs):
        super().__init__(name=name, network=network, **network_kwargs)
        self.nb_actions = nb_actions
        # print(self.nb_actions)
        # self.hidden_layer=1000
        self.hidden_layer=400


    def __call__(self, obs, reuse=False):
        with tf.variable_scope(self.name, reuse=tf.AUTO_REUSE):
            x = self.network_builder(obs)
            print('scope_name: ', self.name)


            x = tf.layers.dense(x, self.hidden_layer, kernel_initializer=tf.random_uniform_initializer(minval=-3e-3, maxval=3e-3))
            # x = 100*tf.nn.tanh(x)
            x = tf.nn.relu(x)
            x = tf.layers.dense(x, self.nb_actions, kernel_initializer=tf.random_uniform_initializer(minval=-3e-3, maxval=3e-3))

            # x=30*tf.tanh(x)
            x=tf.nn.leaky_relu(x)
            


        return x


class Critic(Model):
    def __init__(self, name='critic', network='mlp', **network_kwargs):
        super().__init__(name=name, network=network, **network_kwargs)
        self.layer_norm = True

        #added
        self.hidden_layer=400

    def __call__(self, obs, action, reuse=False):
        with tf.variable_scope(self.name, reuse=tf.AUTO_REUSE):
            x = tf.concat([obs, action], axis=-1) # this assumes observation and action can be concatenated
            x = self.network_builder(x)
            print('scope_name: ', self.name)

            x = tf.layers.dense(x, self.hidden_layer, kernel_initializer=tf.random_uniform_initializer(minval=-3e-3, maxval=3e-3))
            x = tf.nn.tanh(x)
            x = tf.layers.dense(x,  1, kernel_initializer=tf.random_uniform_initializer(minval=-3e-3, maxval=3e-3))

        return x

    @property
    def output_vars(self):
        output_vars = [var for var in self.trainable_vars if 'output' in var.name]
        return output_vars
