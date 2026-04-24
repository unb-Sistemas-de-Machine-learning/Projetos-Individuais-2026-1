from transformers import BertForSequenceClassification, BertTokenizer

MODEL_NAME = "ElSlay/BERT-Phishing-Email-Model"

def load_model_and_tokenizer():
    model = BertForSequenceClassification.from_pretrained(MODEL_NAME)
    tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
    model.eval()
    return model, tokenizer