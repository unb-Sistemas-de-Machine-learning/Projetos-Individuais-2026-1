# src/phishing/feature_extraction.py

import re
from urllib.parse import urlparse
import pandas as pd

def extract_url_features(url: str) -> dict:
    """
    Extrai features heurísticas de uma URL para auxiliar na detecção de phishing.
    Estas features podem complementar modelos de NLP ou serem usadas em modelos tradicionais.
    """
    features = {}

    # Comprimento da URL
    features['url_length'] = len(url)

    # Contagem de caracteres especiais comuns em URLs de phishing
    features['num_dots'] = url.count('.')
    features['num_hyphens'] = url.count('-')
    features['num_at'] = url.count('@') # Indicador de credenciais na URL
    features['num_question_mark'] = url.count('?')
    features['num_and'] = url.count('&')
    features['num_equals'] = url.count('=')
    features['num_slash'] = url.count('/')
    features['num_double_slash'] = url.count('//') # Pode indicar redirecionamento ou ofuscação

    # Presença de HTTPS
    features['has_https'] = 1 if url.startswith('https') else 0

    # Uso de IP no domínio (muitas vezes visto em phishing)
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        if hostname and re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", hostname):
            features['uses_ip_address'] = 1
        else:
            features['uses_ip_address'] = 0
    except Exception:
        features['uses_ip_address'] = 0 # Em caso de URL malformada

    # Comprimento do hostname
    features['hostname_length'] = len(parsed_url.hostname) if parsed_url.hostname else 0

    # Comprimento do path
    features['path_length'] = len(parsed_url.path) if parsed_url.path else 0

    return features

if __name__ == "__main__":
    # Exemplo de uso
    test_urls = [
        "https://www.google.com",
        "http://192.168.1.1/login.php?user=admin",
        "https://bank.com.phishing.ru/login?id=123",
        "ftp://malicious.software/download.zip"
    ]

    print("--- Testando extração de features de URLs ---")
    for url in test_urls:
        print(f"
URL: {url}")
        feats = extract_url_features(url)
        for feature, value in feats.items():
            print(f"  {feature}: {value}")

    # Exemplo com DataFrame
    df_test = pd.DataFrame({'url': test_urls})
    features_df = df_test['url'].apply(lambda x: pd.Series(extract_url_features(x)))
    df_with_features = pd.concat([df_test, features_df], axis=1)
    print("
--- DataFrame com Features ---")
    print(df_with_features.to_string())
