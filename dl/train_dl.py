import sys
import time
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, accuracy_score, f1_score

sys.path.append(r"D:\crolling")
from dl.neural_net import FeedForwardNN

TRAIN = r"D:\crolling\ml\train.csv"
TEST = r"D:\crolling\ml\test.csv"
VEC_PATH = r"D:\crolling\models\tfidf_vectorizer.joblib"
OUT_DIR = r"D:\crolling\models"

LABELS = ["negative", "neutral", "positive"]
LABEL2IDX = {l: i for i, l in enumerate(LABELS)}


def main():
    train = pd.read_csv(TRAIN).dropna(subset=["review_content"])
    test = pd.read_csv(TEST).dropna(subset=["review_content"])

    vec = joblib.load(VEC_PATH)
    Xtr = vec.transform(train["review_content"]).astype(np.float32)
    Xte = vec.transform(test["review_content"]).astype(np.float32)
    ytr = train["sentiment"].map(LABEL2IDX).values
    yte = test["sentiment"].map(LABEL2IDX).values

    n_classes = len(LABELS)
    ytr_onehot = np.eye(n_classes, dtype=np.float32)[ytr]

    model = FeedForwardNN(input_dim=Xtr.shape[1], hidden1=128, hidden2=64, n_classes=n_classes)

    epochs = 15
    batch_size = 256
    n = Xtr.shape[0]
    idx_all = np.arange(n)

    print(f"학습 시작: {n}개 샘플, {epochs} epoch, batch={batch_size}")
    t0 = time.time()
    for epoch in range(epochs):
        rng = np.random.default_rng(epoch)
        rng.shuffle(idx_all)
        lr = 0.08 * (0.92 ** epoch)
        total_loss = 0.0
        n_batches = 0
        for start in range(0, n, batch_size):
            bidx = idx_all[start:start + batch_size]
            Xb = Xtr[bidx]
            yb = ytr_onehot[bidx]
            loss = model.train_step(Xb, yb, lr=lr)
            total_loss += loss
            n_batches += 1
        avg_loss = total_loss / n_batches
        pred = model.predict(Xte)
        acc = accuracy_score(yte, pred)
        print(f"epoch {epoch+1}/{epochs}  loss={avg_loss:.4f}  test_acc={acc:.4f}  lr={lr:.4f}  elapsed={time.time()-t0:.1f}s")

    pred = model.predict(Xte)
    acc = accuracy_score(yte, pred)
    f1 = f1_score(yte, pred, average="macro")
    report = classification_report(yte, pred, target_names=LABELS)
    print(f"\n최종 accuracy={acc:.4f}, macro_f1={f1:.4f}")
    print(report)

    model.save(f"{OUT_DIR}/dl_ffnn.npz")
    with open(r"D:\crolling\models\dl_report.txt", "w", encoding="utf-8") as f:
        f.write(f"accuracy={acc:.4f}\nmacro_f1={f1:.4f}\n\n{report}")
    print("저장 완료: models/dl_ffnn.npz")


if __name__ == "__main__":
    main()
