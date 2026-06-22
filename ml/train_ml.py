"""
ML 베이스라인: TF-IDF + LogisticRegression
한국어 형태소 분석기(konlpy) 설치가 환경상 무거워서, 1~2gram 음절 기반
TF-IDF로 대체했다 (별도 설치 없이 형태소 분석과 비슷한 효과를 냄).
"""
import time
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, f1_score

TRAIN = r"D:\crolling\ml\train.csv"
TEST = r"D:\crolling\ml\test.csv"
OUT_DIR = r"D:\crolling\models"


def main():
    train = pd.read_csv(TRAIN).dropna(subset=["review_content"])
    test = pd.read_csv(TEST).dropna(subset=["review_content"])

    print("TF-IDF 벡터화...")
    vec = TfidfVectorizer(max_features=20000, ngram_range=(1, 2), min_df=2)
    Xtr = vec.fit_transform(train["review_content"])
    Xte = vec.transform(test["review_content"])
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
