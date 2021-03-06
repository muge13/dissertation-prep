
import numpy as np
import keras
from tqdm import trange


class Layer:
    def __init__(self):
        pass

    def forward(self, input):
        return input

    def backward(self, input, grad_output):
        num_units = input.shape[1]
        d_layer_d_input = np.eye(num_units)
        return np.dot(grad_output, d_layer_d_input)


class ReLU(Layer):
    def __init__(self):
        pass

    def forward(self, input):
        relu_forward = np.maximum(0, input)
        return relu_forward

    def backward(self, input, grad_output):
        relu_grad = input > 0
        return grad_output * relu_grad


class Sigmoid(Layer):
    def __init__(self):
        pass

    def forward(self, input):
        return 1 / (1 + np.exp(-input))

    def backward(self, input, grad_output):
        return grad_output*input * (1 - input)


class Dense(Layer):
    def __init__(self, input_units, output_units, learning_rate=0.1):
        self.learning_rate = learning_rate
        self.weights = np.random.normal(loc=0.0,
                                        scale=np.sqrt(2 / (input_units + output_units)),
                                        size=(input_units, output_units))
        self.biases = np.zeros(output_units)

    def forward(self, input):
        return np.dot(input, self.weights) + self.biases

    def backward(self, input, grad_output):
        grad_input = np.dot(grad_output, self.weights.T)
        grad_weights = np.dot(input.T, grad_output)
        grad_biases = grad_output.mean(axis=0) * input.shape[0]

        assert grad_weights.shape == self.weights.shape and grad_biases.shape == self.biases.shape
        self.weights = self.weights - self.learning_rate * grad_weights
        self.biases = self.biases - self.learning_rate * grad_biases

        return grad_input


class MLP:
    def __init__(self):
        pass

    def softmax_crossentropy_with_logits(self,logits, reference_answers):
        logits_for_answers = logits[np.arange(len(logits)), reference_answers]
        xentropy = - logits_for_answers + np.log(np.sum(np.exp(logits), axis=-1))
        return xentropy

    def grad_softmax_crossentropy_with_logits(self,logits, reference_answers):
        ones_for_answers = np.zeros_like(logits)
        ones_for_answers[np.arange(len(logits)), reference_answers] = 1
        softmax = np.exp(logits) / np.exp(logits).sum(axis=-1, keepdims=True)
        return (- ones_for_answers + softmax) / logits.shape[0]

    def load_dataset(self, x_train, y_train, x_test, y_test , subset=None):
        # (x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()

        x_train = x_train.astype(float) / 255
        x_test = x_test.astype(float) / 255

        x_train = x_train.reshape([x_train.shape[0], -1])

        x_test = x_test.reshape([x_test.shape[0], -1])
        if subset is not None:
            x_train = x_train[:subset[0]]
            y_train = y_train[:subset[0]]
            x_test = x_test[:subset[1]]
            y_test = y_test[:subset[1]]

        return x_train, y_train, x_test, y_test

    def forward(self,network, X):
        activations = []
        input = X
        # Looping through each layer
        for l in network:
            activations.append(l.forward(input))
            # Updating input to last layer output
            input = activations[-1]
        assert len(activations) == len(network)
        return activations

    def predict(self,network, X):
        logits = self.forward(network, X)[-1]
        return logits.argmax(axis=-1)

    def train(self,network, X, y):
        layer_activations = self.forward(network, X)
        layer_inputs = [X] + layer_activations
        logits = layer_activations[-1]

        # Compute the loss and the initial gradient
        loss = self.softmax_crossentropy_with_logits(logits, y)
        loss_grad = self.grad_softmax_crossentropy_with_logits(logits, y)

        for layer_index in range(len(network))[::-1]:
            layer = network[layer_index]
            loss_grad = layer.backward(layer_inputs[layer_index], loss_grad)
        return np.mean(loss)

    def iterate_minibatches(self, inputs, targets, batchsize):
        assert len(inputs) == len(targets)
        indices = np.random.permutation(len(inputs))
        for start_idx in trange(0, len(inputs) - batchsize + 1, batchsize):
            excerpt = indices[start_idx:start_idx + batchsize]
            yield inputs[excerpt], targets[excerpt]

