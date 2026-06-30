"""
직접 구현한 피드포워드 신경망 (numpy only).

원래는 PyTorch로 LSTM/BERT 파인튜닝을 하려 했으나, 이 환경의 Python이
3.14라서 PyTorch/Tensorflow 휠이 아직 배포되지 않아 설치가 안 됐다.
대안으로 프레임워크 없이 numpy로 순전파/역전파를 직접 구현했다.
입력은 TF-IDF sparse 행렬을 그대로 사용한다 (scipy sparse @ dense 행렬곱 지원).

구조: input(TF-IDF) -> Dense(128, ReLU) -> Dense(64, ReLU) -> Dense(3, Softmax)
학습: mini-batch SGD + momentum, cross entropy loss
"""
import numpy as np
from scipy import sparse


def relu(x):
    return np.maximum(0, x)


def relu_grad(x):
    return (x > 0).astype(x.dtype)


def softmax(x):
    x = x - x.max(axis=1, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=1, keepdims=True)


class FeedForwardNN:
    def __init__(self, input_dim, hidden1=128, hidden2=64, n_classes=3, seed=42):
        rng = np.random.default_rng(seed)
        self.W1 = rng.normal(0, np.sqrt(2 / input_dim), size=(input_dim, hidden1)).astype(np.float32)
        self.b1 = np.zeros(hidden1, dtype=np.float32)
        self.W2 = rng.normal(0, np.sqrt(2 / hidden1), size=(hidden1, hidden2)).astype(np.float32)
        self.b2 = np.zeros(hidden2, dtype=np.float32)
        self.W3 = rng.normal(0, np.sqrt(2 / hidden2), size=(hidden2, n_classes)).astype(np.float32)
        self.b3 = np.zeros(n_classes, dtype=np.float32)

        self.vW1 = np.zeros_like(self.W1); self.vb1 = np.zeros_like(self.b1)
        self.vW2 = np.zeros_like(self.W2); self.vb2 = np.zeros_like(self.b2)
        self.vW3 = np.zeros_like(self.W3); self.vb3 = np.zeros_like(self.b3)

    def forward(self, X):
        z1 = X @ self.W1 + self.b1
        a1 = relu(z1)
        z2 = a1 @ self.W2 + self.b2
        a2 = relu(z2)
        z3 = a2 @ self.W3 + self.b3
        out = softmax(z3)
        return z1, a1, z2, a2, out

    def predict_proba(self, X):
        if sparse.issparse(X):
            X = X.astype(np.float32)
        _, _, _, _, out = self.forward(X)
        return out

    def predict(self, X):
        return self.predict_proba(X).argmax(axis=1)

    def train_step(self, X, y_onehot, lr=0.05, momentum=0.9, l2=1e-5):
        n = X.shape[0]
        z1, a1, z2, a2, out = self.forward(X)

        dz3 = (out - y_onehot) / n
        dW3 = a2.T @ dz3 + l2 * self.W3
        db3 = dz3.sum(axis=0)

        da2 = dz3 @ self.W3.T
        dz2 = da2 * relu_grad(z2)
        dW2 = a1.T @ dz2 + l2 * self.W2
        db2 = dz2.sum(axis=0)

        da1 = dz2 @ self.W2.T
        dz1 = da1 * relu_grad(z1)
        if sparse.issparse(X):
            dW1 = X.T.dot(dz1) + l2 * self.W1
        else:
            dW1 = X.T @ dz1 + l2 * self.W1
        db1 = dz1.sum(axis=0)

        self.vW3 = momentum * self.vW3 - lr * dW3; self.W3 += self.vW3
        self.vb3 = momentum * self.vb3 - lr * db3; self.b3 += self.vb3
        self.vW2 = momentum * self.vW2 - lr * dW2; self.W2 += self.vW2
        self.vb2 = momentum * self.vb2 - lr * db2; self.b2 += self.vb2
        self.vW1 = momentum * self.vW1 - lr * np.asarray(dW1); self.W1 += self.vW1
        self.vb1 = momentum * self.vb1 - lr * db1; self.b1 += self.vb1

        loss = -np.sum(y_onehot * np.log(out + 1e-9)) / n
        return loss

    def save(self, path):
        np.savez(path, W1=self.W1, b1=self.b1, W2=self.W2, b2=self.b2, W3=self.W3, b3=self.b3)

    @classmethod
    def load(cls, path):
        d = np.load(path)
        model = cls(d["W1"].shape[0], d["W1"].shape[1], d["W2"].shape[1], d["W3"].shape[1])
        model.W1, model.b1 = d["W1"], d["b1"]
        model.W2, model.b2 = d["W2"], d["b2"]
        model.W3, model.b3 = d["W3"], d["b3"]
        return model
