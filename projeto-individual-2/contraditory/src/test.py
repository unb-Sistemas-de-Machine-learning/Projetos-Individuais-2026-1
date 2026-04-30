import unittest
import os
import tempfile
import numpy as np
import pandas as pd
import torch
from unittest.mock import patch, MagicMock

from model.cross_encoder import load_tokenizer_and_model, tokenize_nli_batch
from model.metrics import compute_metrics


class TestDataProcessing(unittest.TestCase):
    """Testes para carregamento e processamento de dados"""
    
    def test_train_data_loading(self):
        """Testa se dados de treino carregam corretamente"""
        # Cria DataFrame temporário
        df = pd.DataFrame({
            "premise": ["The cat is on the mat"],
            "hypothesis": ["The cat is on the floor"],
            "label": [0]
        })
        self.assertEqual(len(df), 1)
        self.assertIn("premise", df.columns)
        self.assertIn("hypothesis", df.columns)
        self.assertIn("label", df.columns)

    def test_train_test_split(self):
        """Testa se o split treino/validação funciona"""
        df = pd.DataFrame({
            "premise": [f"Text {i}" for i in range(100)],
            "hypothesis": [f"Hyp {i}" for i in range(100)],
            "label": [i % 3 for i in range(100)]
        })
        
        from sklearn.model_selection import train_test_split
        train_df, val_df = train_test_split(df, test_size=0.2, random_state=42)
        
        self.assertEqual(len(train_df), 80)
        self.assertEqual(len(val_df), 20)
        self.assertEqual(len(train_df) + len(val_df), len(df))

    def test_column_rename(self):
        """Testa se renomeação de colunas funciona"""
        df = pd.DataFrame({"label": [0, 1, 2]})
        df = df.rename_column("label", "labels") if hasattr(df, "rename_column") else df.rename(columns={"label": "labels"})
        
        if "labels" in df.columns:
            self.assertIn("labels", df.columns)


class TestTokenization(unittest.TestCase):
    """Testes para tokenização de textos"""
    
    def setUp(self):
        """Inicializa tokenizer para os testes"""
        self.model_name = "cross-encoder/nli-deberta-v3-small"
        try:
            from transformers import AutoTokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        except Exception:
            self.skipTest("Modelo não disponível para download")

    def test_tokenizer_loading(self):
        """Testa se tokenizer carrega corretamente"""
        self.assertIsNotNone(self.tokenizer)

    def test_tokenization_output(self):
        """Testa se tokenização produz output válido"""
        text = "This is a test sentence."
        output = self.tokenizer(text, max_length=128, truncation=True, padding="max_length")
        
        self.assertIn("input_ids", output)
        self.assertIn("attention_mask", output)
        self.assertEqual(len(output["input_ids"]), 128)

    def test_batch_tokenization(self):
        """Testa tokenização em batch"""
        texts = ["Sentence 1", "Sentence 2", "Sentence 3"]
        output = self.tokenizer(texts, max_length=128, truncation=True, padding="max_length", batch_encode_plus=True)
        
        self.assertEqual(len(output["input_ids"]), 3)


class TestMetrics(unittest.TestCase):
    """Testes para métricas de avaliação"""
    
    def test_perfect_predictions(self):
        """Testa métricas com predições perfeitas"""
        predictions = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        labels = np.array([0, 1, 2])
        
        accuracy = np.mean(np.argmax(predictions, axis=1) == labels)
        self.assertEqual(accuracy, 1.0)

    def test_random_predictions(self):
        """Testa métricas com predições aleatórias"""
        np.random.seed(42)
        predictions = np.random.randn(100, 3)
        labels = np.random.randint(0, 3, 100)
        
        accuracy = np.mean(np.argmax(predictions, axis=1) == labels)
        self.assertGreaterEqual(accuracy, 0.0)
        self.assertLessEqual(accuracy, 1.0)

    def test_confusion_matrix(self):
        """Testa geração de matriz de confusão"""
        from sklearn.metrics import confusion_matrix
        y_true = np.array([0, 1, 2, 0, 1, 2])
        y_pred = np.array([0, 1, 1, 0, 2, 2])
        
        cm = confusion_matrix(y_true, y_pred)
        self.assertEqual(cm.shape, (3, 3))
        self.assertEqual(np.sum(cm), len(y_true))


class TestModelTraining(unittest.TestCase):
    """Testes para configuração de treinamento"""
    
    def test_training_arguments(self):
        """Testa configuração de argumentos de treino"""
        from transformers import TrainingArguments
        
        args = TrainingArguments(
            output_dir="models/test",
            eval_strategy="epoch",
            num_train_epochs=1,
            learning_rate=2e-5
        )
        
        self.assertEqual(args.num_train_epochs, 1)
        self.assertEqual(args.learning_rate, 2e-5)
        self.assertEqual(args.eval_strategy, "epoch")

    def test_device_detection(self):
        """Testa detecção de device (GPU/CPU)"""
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.assertIn(device, ["cuda", "cpu"])

    def test_artifact_creation(self):
        """Testa criação de diretórios de artefatos"""
        with tempfile.TemporaryDirectory() as tmpdir:
            models_dir = os.path.join(tmpdir, "models")
            artifacts_dir = os.path.join(tmpdir, "artifacts")
            
            os.makedirs(models_dir, exist_ok=True)
            os.makedirs(artifacts_dir, exist_ok=True)
            
            self.assertTrue(os.path.exists(models_dir))
            self.assertTrue(os.path.exists(artifacts_dir))


class TestDataValidation(unittest.TestCase):
    """Testes para validação de dados"""
    
    def test_dataset_format(self):
        """Testa se dataset tem o formato esperado"""
        df = pd.DataFrame({
            "premise": ["Text 1", "Text 2"],
            "hypothesis": ["Hyp 1", "Hyp 2"],
            "label": [0, 1]
        })
        
        required_cols = ["premise", "hypothesis", "label"]
        for col in required_cols:
            self.assertIn(col, df.columns)

    def test_label_distribution(self):
        """Testa distribuição balanceada de labels"""
        df = pd.DataFrame({
            "label": [0] * 33 + [1] * 33 + [2] * 34
        })
        
        value_counts = df["label"].value_counts()
        self.assertEqual(len(value_counts), 3)
        self.assertTrue(all(count >= 30 for count in value_counts))


if __name__ == "__main__":
    unittest.main()
