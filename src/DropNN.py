# https://github.com/mnielsen//neural-networks-and-deep-learning/ all the credit to this guy
# testing for overfit: p lot training set and validation set error as a function of training set size.
# If they show a stable gap at the right end of the plot, you're probably overfitting.
import gzip
import pickle
import random
import numpy as np
np.seterr(all='ignore')


class Network(object):
    def __init__(self, sizes):
        self.num_layers = len(sizes)
        self.sizes = sizes
        self.biases = [np.random.randn(y, 1) for y in sizes[1:]]
        self.weights = [np.random.randn(y, x) for x, y in zip(sizes[:-1], sizes[1:])]

    def backprop_with_mini_batch(self, mini_batch, eta=3, epoch=0, pseu=False):
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        # activations = []
        for x, y in mini_batch:
            delta_nabla_b, delta_nabla_w = self.backprop(x, y)
            nabla_b = [nb + dnb for nb, dnb in zip(nabla_b, delta_nabla_b)]
            nabla_w = [nw + dnw for nw, dnw in zip(nabla_w, delta_nabla_w)]
        self.weights = [w - (eta / len(mini_batch)) * nw for w, nw in zip(self.weights, nabla_w)]
        self.biases = [b - (eta / len(mini_batch)) * nb for b, nb in zip(self.biases, nabla_b)]

    def backprop(self, x, y):

        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]

        # feedforward phase
        activation = x
        activations = [x]
        zs = []
        layer = 0
        for b, w in zip(self.biases, self.weights):
            # TODO drop out here(9) drop out making things worse not better  drop out rates: 50 % dropout for all hidden units;  20 % dropout for visible units
            activation = np.multiply(activation, dropout(0.2, np.shape(activation)))
            z = np.dot(w, activation) + b
            zs.append(z)
            # TODO use differnet active functions return all WRONG label ! WHY ??
            # todo also add drop out on the hidd
            if layer == 0:
                # activation = rectifier(z)
                activation = sigmoid(z)
            else:
                activation = sigmoid(z)
            layer += 1
            activations.append(activation)

        # backward phase
        delta = self.cost_derivative(activations[-1], y)
        nabla_b[-1] = delta
        nabla_w[-1] = np.dot(delta, activations[-2].transpose())

        for l in range(2, self.num_layers):
            z = zs[-l]
            delta = np.dot(self.weights[-l + 1].transpose(), delta) * sigmoid_prime(z)
            # TODO different active function in the hidden layer, different prime(3)(BP2 in Ref)
            # delta = np.dot(self.weights[-l + 1].transpose(), delta) * rectifier_prime(z)
            nabla_b[-l] = delta
            nabla_w[-l] = np.dot(delta, activations[-l - 1].transpose())
        return nabla_b, nabla_w

    def feedforward(self, a):
        layer = 0
        for b, w in zip(self.biases, self.weights):
            z = np.dot(w, a) + b
            if layer == 0:
                # a = rectifier(z) # for hidden layers
                a = sigmoid(z)
            else:
                a = sigmoid(z)  # for output layer
            layer += 1
        return a

    def evaluate(self, test_data):
        test_results = [(np.argmax(self.feedforward(x)), y) for (x, y) in test_data]
        return sum(int(x == y) for (x, y) in test_results)

    def cost_derivative(self, output_activations, y):
        return output_activations - y

    def alfaCoefficient(self, currentEpoch, DAE=False):
        if DAE:
            epochT1, epochT2 = 200, 800
        else:
            epochT1, epochT2 = 100, 600
        if currentEpoch < epochT1:
            return 0
        elif epochT1 <= currentEpoch & currentEpoch < epochT2:
            return ((currentEpoch - epochT1) * 0.4) / epochT2 - epochT1
        elif epochT2 <= currentEpoch:
            return 3

    def SGD_DropNN(self, training_data, epochs, mini_batch_size, eta, test_data=None):
        for j in range(epochs):
            random.shuffle(training_data)
            mini_batches = [training_data[k:k + mini_batch_size] for k in range(0, len(training_data), mini_batch_size)]

            for mini_batch in mini_batches:
                self.backprop_with_mini_batch(mini_batch, eta)

            if test_data:
                print("Epoch {0}: {1} / {2}".format(j, self.evaluate(test_data), len(test_data)))
            else:
                print("Epoch {0} complete".format(j))


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def sigmoid_prime(z):
    return sigmoid(z) * (1.0 - sigmoid(z))


def rectifier(z):  # f(x)=max(0,x)
    return np.maximum(np.reshape(np.zeros((z.shape)), z.shape), z)


def rectifier_prime(z):  # f'(x)=(max(0,x))'  http://kawahara.ca/what-is-the-derivative-of-relu/
    new_z = np.zeros(np.shape(z))
    for i in range(np.shape(z)[0]):
        if z[i] > 0.:
            new_z[i] = 1
    return new_z


def dropout(probability, shape):
    return np.random.binomial(1, probability, shape)


def vectorized_result(j):
    e = np.zeros((10, 1))
    e[j] = 1.0
    return e


def load_data():
    f = gzip.open('mnist.pkl.gz', 'rb')
    training_data, validation_data, test_data = pickle.load(f, encoding='latin1')
    f.close()
    return (training_data, validation_data, test_data)


def load_data_wrapper():
    tr_d, va_d, te_d = load_data()
    training_inputs = [np.reshape(x, (784, 1)) for x in tr_d[0]]
    training_results = [vectorized_result(y) for y in tr_d[1]]
    training_data = list(zip(training_inputs, training_results))
    validation_inputs = [np.reshape(x, (784, 1)) for x in va_d[0]]
    validation_data = list(zip(validation_inputs, va_d[1]))
    test_inputs = [np.reshape(x, (784, 1)) for x in te_d[0]]
    test_data = list(zip(test_inputs, te_d[1]))
    return (training_data, validation_data, test_data)


if __name__ == "__main__":
    training_data, validation_data, test_data = load_data_wrapper();

    # DROP NN
    DropNN = Network([784, 5000, 10])
    DropNN.SGD_DropNN(training_data, epochs=10, mini_batch_size=32, eta=3.0, test_data=test_data)