"""
통합 리뷰 데이터를 감성분류 학습용으로 정제한다.

문제: positive가 86.7%라서 그대로 학습하면 모델이 그냥 다 positive로 찍어도
     정확도가 86%가 나옴 (== 쓸모없는 모델). 그래서 클래스별로 다운샘플링해서
     학습셋 비율을 맞춘다 (negative/neutral 전량 + positive는 같은 규모로 샘플).
"""
import re
import pandas as pd
import numpy as np

np.random.seed(42)

SRC = r"D:\crolling\merged_reviews_all.csv"
OUT_TRAIN = r"D:\crolling\ml\train.csv"
OUT_TEST = r"D:\crolling\ml\test.csv"


def clean_text(t):
    if not isinstance(t, str):
        return ""
    t = re.sub(r"http\S+", " ", t)
    t = re.sub(r"[^\w\s가-힣]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def main():
    print("로딩...")
    df = pd.read_csv(SRC, low_memory=False)
    df["review_content"] = df["review_content"].apply(clean_text)
    df = df[df["review_content"].str.len() >= 5]
    df = df.dropna(subset=["sentiment"])
    print("클리닝 후:", len(df))

    neg = df[df["sentiment"] == "negative"]
    neu = df[df["sentiment"] == "neutral"]
    pos = df[df["sentiment"] == "positive"]
    print("원본 분포 - neg:", len(neg), "neu:", len(neu), "pos:", len(pos))

    # positive는 negative*2 규모로만 샘플 (완전 1:1:1은 텍스트 다양성 손해라서 2:1:1로 절충)
    target_pos = min(len(pos), len(neg) * 2)
    pos_sampled = pos.sample(n=target_pos, random_state=42)
    balanced = pd.concat([neg, neu, pos_sampled], ignore_index=True)
    balanced = balanced.sample(frac=1, random_state=42).reset_index(drop=True)
    print("밸런싱 후 전체:", len(balanced))
    print(balanced["sentiment"].value_counts())

    n = len(balanced)
    n_test = int(n * 0.15)
    test = balanced.iloc[:n_test]
    train = balanced.iloc[n_test:]

    train[["review_content", "sentiment", "platform"]].to_csv(OUT_TRAIN, index=False, encoding="utf-8-sig")
    test[["review_content", "sentiment", "platform"]].to_csv(OUT_TEST, index=False, encoding="utf-8-sig")
    print(f"train={len(train)}, test={len(test)} 저장 완료")


if __name__ == "__main__":
    main()
