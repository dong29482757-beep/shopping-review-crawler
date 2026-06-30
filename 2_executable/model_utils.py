import joblib
import numpy as np
from dl.neural_net import FeedForwardNN
from preprocessing_ko import clean_for_vectorizer

LABELS = ["negative", "neutral", "positive"]
LABEL_KO = {"negative": "부정", "neutral": "중립", "positive": "긍정"}

# 학습 시 클래스 밸런싱을 위해 다운샘플링했기 때문에, 학습 데이터의 클래스 비율과
# 실제 서비스에서 들어오는 리뷰의 실제 클래스 비율이 다르다 (positive가 학습셋엔 55%,
# 실제론 87%). 이대로 배포하면 모델이 neutral/negative를 과도하게 예측해서
# 실제 분포에서는 neutral precision이 0.20까지 떨어지는 문제가 있었다.
# (자세한 진단/재현: DEVLOG.md "모델 문제점과 개선" 참고)
# -> label shift correction: p_real(y|x) ∝ p_train(y|x) * (p_real(y) / p_train(y))
TRAIN_PRIOR = np.array([0.277048, 0.170827, 0.552126])  # negative, neutral, positive
REAL_PRIOR = np.array([0.082203, 0.050704, 0.867093])
PRIOR_CORRECTION = REAL_PRIOR / TRAIN_PRIOR


def correct_proba(proba):
    corrected = proba * PRIOR_CORRECTION
    return corrected / corrected.sum()


class SentimentModels:
    def __init__(self, model_dir=r"D:\crolling\models"):
        self.vec = joblib.load(f"{model_dir}/tfidf_vectorizer.joblib")
        self.ml_model = joblib.load(f"{model_dir}/ml_logreg.joblib")
        self.dl_model = FeedForwardNN.load(f"{model_dir}/dl_ffnn.npz")
        assert list(self.ml_model.classes_) == LABELS, "ml_model.classes_ 순서가 LABELS와 달라 보정이 깨짐"

    def predict(self, text):
        tokens = clean_for_vectorizer(text)
        X = self.vec.transform([tokens])

        ml_proba_raw = self.ml_model.predict_proba(X)[0]
        ml_proba_arr = correct_proba(ml_proba_raw)
        ml_pred = LABELS[ml_proba_arr.argmax()]

        dl_proba_raw = self.dl_model.predict_proba(X)[0]
        dl_proba_arr = correct_proba(dl_proba_raw)
        dl_pred = LABELS[dl_proba_arr.argmax()]

        return {
            "cleaned_text": tokens,
            "ml": {"label": ml_pred, "label_ko": LABEL_KO[ml_pred], "proba": dict(zip(LABELS, ml_proba_arr))},
            "dl": {"label": dl_pred, "label_ko": LABEL_KO[dl_pred], "proba": dict(zip(LABELS, dl_proba_arr))},
        }
