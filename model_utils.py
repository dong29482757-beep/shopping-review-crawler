import re
import joblib
from dl.neural_net import FeedForwardNN

LABELS = ["negative", "neutral", "positive"]
LABEL_KO = {"negative": "부정", "neutral": "중립", "positive": "긍정"}


def clean_text(t):
    if not isinstance(t, str):
        return ""
    t = re.sub(r"http\S+", " ", t)
    t = re.sub(r"[^\w\s가-힣]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


class SentimentModels:
    def __init__(self, model_dir=r"D:\crolling\models"):
        self.vec = joblib.load(f"{model_dir}/tfidf_vectorizer.joblib")
        self.ml_model = joblib.load(f"{model_dir}/ml_logreg.joblib")
        self.dl_model = FeedForwardNN.load(f"{model_dir}/dl_ffnn.npz")

    def predict(self, text):
        cleaned = clean_text(text)
        X = self.vec.transform([cleaned])

        ml_pred = self.ml_model.predict(X)[0]
        ml_proba = dict(zip(self.ml_model.classes_, self.ml_model.predict_proba(X)[0]))

        dl_proba_arr = self.dl_model.predict_proba(X)[0]
        dl_pred = LABELS[dl_proba_arr.argmax()]
        dl_proba = dict(zip(LABELS, dl_proba_arr))

        return {
            "cleaned_text": cleaned,
            "ml": {"label": ml_pred, "label_ko": LABEL_KO[ml_pred], "proba": ml_proba},
            "dl": {"label": dl_pred, "label_ko": LABEL_KO[dl_pred], "proba": dl_proba},
        }
