"""
KoELECTRA-small 파인튜닝 (CPU 한정 환경이라 학습 데이터를 서브샘플링해서
실제로 동작/성능을 검증하는 용도). GPU 환경이면 train.csv 전체로 늘려서
재현 가능 (SAMPLE_TRAIN/SAMPLE_TEST를 None으로 바꾸면 전체 사용).
"""
import time
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import classification_report, accuracy_score, f1_score

TRAIN = r"D:\crolling\ml\train.csv"
TEST = r"D:\crolling\ml\test.csv"
OUT_DIR = r"D:\crolling\models"
MODEL_NAME = "monologg/koelectra-small-v3-discriminator"

LABELS = ["negative", "neutral", "positive"]
LABEL2IDX = {l: i for i, l in enumerate(LABELS)}

SAMPLE_TRAIN = 20000
SAMPLE_TEST = 4000
MAX_LEN = 64
BATCH_SIZE = 16
EPOCHS = 2
LR = 2e-5

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class ReviewDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=MAX_LEN):
        self.enc = tokenizer(list(texts), padding=True, truncation=True, max_length=max_len, return_tensors="pt")
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return {k: v[idx] for k, v in self.enc.items()}, self.labels[idx]


def main():
    train = pd.read_csv(TRAIN).dropna(subset=["review_content"])
    test = pd.read_csv(TEST).dropna(subset=["review_content"])

    if SAMPLE_TRAIN:
        train = train.sample(n=min(SAMPLE_TRAIN, len(train)), random_state=42).reset_index(drop=True)
    if SAMPLE_TEST:
        test = test.sample(n=min(SAMPLE_TEST, len(test)), random_state=42).reset_index(drop=True)

    print(f"학습 {len(train)}건 / 검증 {len(test)}건 (CPU 환경 한계로 서브샘플 사용)")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=len(LABELS)).to(device)

    ytr = train["sentiment"].map(LABEL2IDX).tolist()
    yte = test["sentiment"].map(LABEL2IDX).tolist()

    train_ds = ReviewDataset(train["review_content"].tolist(), ytr, tokenizer)
    test_ds = ReviewDataset(test["review_content"].tolist(), yte, tokenizer)
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_ds, batch_size=32, shuffle=False)

    optimizer = torch.optim.AdamW(model.parameters(), lr=LR)

    print(f"학습 시작: device={device}")
    t0 = time.time()
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0.0
        for batch, yb in train_loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            yb = yb.to(device)
            optimizer.zero_grad()
            out = model(**batch, labels=yb)
            out.loss.backward()
            optimizer.step()
            total_loss += out.loss.item()
        print(f"epoch {epoch+1}/{EPOCHS}  loss={total_loss/len(train_loader):.4f}  elapsed={time.time()-t0:.1f}s")

    model.eval()
    preds = []
    with torch.no_grad():
        for batch, yb in test_loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            out = model(**batch)
            preds.extend(out.logits.argmax(dim=1).cpu().numpy().tolist())

    pred_labels = [LABELS[i] for i in preds]
    true_labels = [LABELS[i] for i in yte]
    acc = accuracy_score(true_labels, pred_labels)
    f1 = f1_score(true_labels, pred_labels, average="macro")
    report = classification_report(true_labels, pred_labels)
    print(f"\n최종 accuracy={acc:.4f}, macro_f1={f1:.4f}")
    print(report)

    with open(r"D:\crolling\models\transformer_report.txt", "w", encoding="utf-8") as f:
        f.write(f"model={MODEL_NAME}\ntrain_samples={len(train)}\ntest_samples={len(test)}\n")
        f.write(f"accuracy={acc:.4f}\nmacro_f1={f1:.4f}\n\n{report}")
    model.save_pretrained(f"{OUT_DIR}/koelectra_finetuned")
    tokenizer.save_pretrained(f"{OUT_DIR}/koelectra_finetuned")
    print("저장 완료: models/koelectra_finetuned/")


if __name__ == "__main__":
    main()
