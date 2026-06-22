import sys
import time
import pandas as pd

sys.path.append(r"D:\crolling")
from preprocessing_ko import clean_for_vectorizer

FILES = [
    (r"D:\crolling\ml\train.csv", r"D:\crolling\ml\train_tok.csv"),
    (r"D:\crolling\ml\test.csv", r"D:\crolling\ml\test_tok.csv"),
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
