import os
import sys
import time
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT)
from preprocessing_ko import clean_for_vectorizer

_ML = os.path.join(ROOT, "train", "ml")
FILES = [
    (os.path.join(_ML, "train.csv"), os.path.join(_ML, "train_tok.csv")),
    (os.path.join(_ML, "test.csv"), os.path.join(_ML, "test_tok.csv")),
]


def main():
    for src, dst in FILES:
        df = pd.read_csv(src).dropna(subset=["review_content"])
        print(f"{src}: {len(df)}건 토큰화 시작")
        t0 = time.time()
        df["tokens"] = df["review_content"].apply(clean_for_vectorizer)
        df = df[df["tokens"].str.len() > 0]
        print(f"  완료: {time.time()-t0:.1f}s, 결과 {len(df)}건")
        df.to_csv(dst, index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main()
