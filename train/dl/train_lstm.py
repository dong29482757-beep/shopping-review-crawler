"""
PyTorch LSTM 감성 분류 모델.
numpy FFNN과 다르게 단어 "순서"를 학습한다 (TF-IDF는 순서를 버림).
별도 venv(torch_env, Python 3.11)에서 실행해야 함 — 메인 환경은 Python 3.14라
PyTorch 휠이 없어서 설치가 안 됨.
"""
import re
import time
import collections
import pickle

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import classification_report, accuracy_score, f1_score

TRAIN = r"D:\crolling\ml\train.csv"
TEST = r"D:\crolling\ml\test.csv"
OUT_DIR = r"D:\crolling\models"

LABELS = ["negative", "neutral", "positive"]
LABEL2IDX = {l: i for i, l in enumerate(LABELS)}

MAX_LEN = 40
VOCAB_SIZE = 20000
EMBED_DIM = 100
HIDDEN_DIM = 128
BATCH_SIZE = 128
EPOCHS = 6

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def tokenize(text):
    return re.findall(r"[가-힣]+|[a-zA-Z]+|\d+", text)


def build_vocab(texts, max_size=VOCAB_SIZE):
    counter = collections.Counter()
    for t in texts:
        counter.update(tokenize(t))
    most_common = counter.most_common(max_size - 2)
    vocab = {"<pad>": 0, "<unk>": 1}
    for word, _ in most_common:
        vocab[word] = len(vocab)
    return vocab


def encode(text, vocab, max_len=MAX_LEN):
    tokens = tokenize(text)[:max_len]
    ids = [vocab.get(t, 1) for t in tokens]
    ids = ids + [0] * (max_len - len(ids))
    return ids


class ReviewDataset(Dataset):
    def __init__(self, texts, labels, vocab):
        self.X = np.array([encode(t, vocab) for t in texts], dtype=np.int64)
        self.y = np.array(labels, dtype=np.int64)

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


class LSTMClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, n_classes):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.dropout = nn.Dropout(0.3)
        self.fc = nn.Linear(hidden_dim * 2, n_classes)

    def forward(self, x):
        emb = self.embedding(x)
        out, (h_n, _) = self.lstm(emb)
        h = torch.cat([h_n[0], h_n[1]], dim=1)
        h = self.dropout(h)
        return self.fc(h)


def main():
    train = pd.read_csv(TRAIN).dropna(subset=["review_content"])
    test = pd.read_csv(TEST).dropna(subset=["review_content"])

    print("vocab 생성...")
    vocab = build_vocab(train["review_content"])
    print(f"vocab size: {len(vocab)}")

    ytr = train["sentiment"].map(LABEL2IDX).tolist()
    yte = test["sentiment"].map(LABEL2IDX).tolist()

    train_ds = ReviewDataset(train["review_content"].tolist(), ytr, vocab)
    test_ds = ReviewDataset(test["review_content"].tolist(), yte, vocab)
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_ds, batch_size=512, shuffle=False)

    model = LSTMClassifier(len(vocab), EMBED_DIM, HIDDEN_DIM, len(LABELS)).to(device)

    class_counts = np.bincount(ytr, minlength=len(LABELS))
    class_weights = torch.tensor(class_counts.sum() / (len(LABELS) * class_counts), dtype=torch.float32).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    print(f"학습 시작: device={device}, train={len(train_ds)}, test={len(test_ds)}")
    t0 = time.time()
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0.0
        for xb, yb in train_loader:
            xb, yb = xb.to(device), yb.to(device)
            optimizer.zero_grad()
            logits = model(xb)
            loss = criterion(logits, yb)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        model.eval()
        preds = []
        with torch.no_grad():
            for xb, yb in test_loader:
                xb = xb.to(device)
                logits = model(xb)
                preds.extend(logits.argmax(dim=1).cpu().numpy().tolist())
        acc = accuracy_score(yte, preds)
        print(f"epoch {epoch+1}/{EPOCHS}  loss={total_loss/len(train_loader):.4f}  test_acc={acc:.4f}  elapsed={time.time()-t0:.1f}s")

    model.eval()
    preds = []
    with torch.no_grad():
        for xb, yb in test_loader:
            xb = xb.to(device)
            logits = model(xb)
            preds.extend(logits.argmax(dim=1).cpu().numpy().tolist())
    pred_labels = [LABELS[i] for i in preds]
    true_labels = [LABELS[i] for i in yte]
    acc = accuracy_score(true_labels, pred_labels)
    f1 = f1_score(true_labels, pred_labels, average="macro")
    report = classification_report(true_labels, pred_labels)
    print(f"\n최종 accuracy={acc:.4f}, macro_f1={f1:.4f}")
    print(report)

    torch.save(model.state_dict(), f"{OUT_DIR}/lstm_model.pt")
    with open(f"{OUT_DIR}/lstm_vocab.pkl", "wb") as f:
        pickle.dump(vocab, f)
    with open(r"D:\crolling\models\lstm_report.txt", "w", encoding="utf-8") as f:
        f.write(f"accuracy={acc:.4f}\nmacro_f1={f1:.4f}\n\n{report}")
    print("저장 완료: models/lstm_model.pt, models/lstm_vocab.pkl")


if __name__ == "__main__":
    main()
