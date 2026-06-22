"""
ML 모델: 형태소 분석(Okt) 기반 토큰 + TF-IDF + LogisticRegression.

이전 버전은 형태소 분석 없이 1~2gram 음절 TF-IDF를 썼는데, 조사가 그대로
토큰에 섞여서("좋아요"/"좋아서"/"좋은데"가 전부 다른 단어로 취급됨) 품질이
떨어졌다. ml/tokenize_data.py에서 Okt로 미리 토큰화한 train_tok.csv/test_tok.csv를
사용한다 (이미 공백 구분된 형태소 토큰이므로 tokenizer=str.split만 적용).
"""
import time
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, f1_score

TRAIN = r"D:\crolling\ml\train_tok.csv"
TEST = r"D:\crolling\ml\test_tok.csv"
OUT_DIR = r"D:\crolling\models"


def main():
    train = pd.read_csv(TRAIN).dropna(subset=["tokens"])
    test = pd.read_csv(TEST).dropna(subset=["tokens"])

    print("TF-IDF 벡터화 (형태소 토큰 기반)...")
    vec = TfidfVectorizer(
        tokenizer=str.split, token_pattern=None, preprocessor=None, lowercase=False,
        max_features=15000, ngram_range=(1, 2), min_df=2,
    )
    Xtr = vec.fit_transform(train["tokens"])
    Xte = vec.transform(test["tokens"])
    ytr, yte = train["sentiment"], test["sentiment"]

    print("로지스틱 회귀 학습...")
    t0 = time.time()
    clf = LogisticRegression(max_iter=300, class_weight="balanced", C=2.0)
    clf.fit(Xtr, ytr)
    print(f"학습 시간: {time.time()-t0:.1f}s")

    pred = clf.predict(Xte)
    acc = accuracy_score(yte, pred)
    f1 = f1_score(yte, pred, average="macro")
    print(f"accuracy={acc:.4f}, macro_f1={f1:.4f}")
    print(classification_report(yte, pred))

    joblib.dump(vec, f"{OUT_DIR}/tfidf_vectorizer.joblib")
    joblib.dump(clf, f"{OUT_DIR}/ml_logreg.joblib")
    print("저장 완료: models/tfidf_vectorizer.joblib, models/ml_logreg.joblib")

    with open(r"D:\crolling\models\ml_report.txt", "w", encoding="utf-8") as f:
        f.write(f"accuracy={acc:.4f}\nmacro_f1={f1:.4f}\n\n")
        f.write(classification_report(yte, pred))


if __name__ == "__main__":
    main()
