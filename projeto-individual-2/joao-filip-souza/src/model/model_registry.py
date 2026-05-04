import mlflow
from datetime import datetime
from typing import Optional, Dict, Tuple


def register_model_to_registry(model_name: str, model_uri: str, metrics: Dict):
    """
    Registra o modelo no MLflow Model Registry.
    
    Args:
        model_name: Nome do modelo no registry (ex: "CIFAR10-AnimalClassifier")
        model_uri: URI do modelo salvo (retornado por mlflow.pytorch.log_model)
        metrics: Dicionário com métricas do modelo {'accuracy', 'precision', 'mean_confidence'}
        
    Returns:
        Versão registrada do modelo
    """
    print(f"\n[Model Registry] Registrando modelo '{model_name}'...")
    
    try:
        model_version = mlflow.register_model(model_uri, model_name)
        print(f"[OK] Modelo registrado com sucesso! Versão: {model_version.version}")
        
        return model_version
    except Exception as e:
        print(f"[ERRO] Erro ao registrar modelo: {e}")
        raise


def get_best_model_version(model_name: str) -> Optional[Dict]:
    """
    Busca a melhor versão anterior do modelo baseado em accuracy.
    
    Args:
        model_name: Nome do modelo no registry
        
    Returns:
        Dicionário com dados da melhor versão ou None se não existir
    """
    try:
        client = mlflow.tracking.MlflowClient()
        versions = client.get_latest_versions(model_name)
        
        if not versions:
            print(f"[Model Registry] Nenhuma versão anterior encontrada para '{model_name}'")
            return None
        
        best_version = None
        best_accuracy = -1
        
        for version in versions:
            # Buscar a run associada à versão para pegar as métricas
            run_id = version.run_id
            run = client.get_run(run_id)
            
            accuracy = run.data.metrics.get('accuracy', -1)
            
            print(f"  Versão {version.version}: Acurácia = {accuracy:.4f}")
            
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_version = {
                    'version': version.version,
                    'accuracy': accuracy,
                    'run_id': run_id,
                    'stage': version.current_stage
                }
        
        return best_version
    except Exception as e:
        print(f"[Model Registry] Erro ao buscar versões anteriores: {e}")
        return None


def compare_and_promote_model(
    model_name: str, 
    new_version,
    new_metrics: Dict,
    promotion_metric: str = 'accuracy'
) -> Tuple[bool, str]:
    """
    Compara o novo modelo com a melhor versão anterior e promove se for melhor.
    
    Args:
        model_name: Nome do modelo no registry
        new_version: Versão do novo modelo
        new_metrics: Métricas do novo modelo
        promotion_metric: Métrica para comparação (padrão: 'accuracy')
        
    Returns:
        Tupla (foi_promovido, mensagem)
    """
    print(f"\n[Model Registry] Comparando novo modelo com versão anterior...")
    
    new_accuracy = new_metrics.get(promotion_metric, 0)
    print(f"  Novo modelo - {promotion_metric}: {new_accuracy:.4f}")
    
    best_version = get_best_model_version(model_name)
    
    # Se não existe versão anterior, promover a nova
    if not best_version:
        print(f"\n[OK] Primeira versão registrada! Promovendo para 'Production'...")
        _transition_model_version(model_name, new_version.version, "Production")
        return True, "Primeira versão registrada e promovida para Production"
    
    # Comparar com versão anterior
    old_accuracy = best_version['accuracy']
    improvement = ((new_accuracy - old_accuracy) / old_accuracy * 100) if old_accuracy > 0 else 0
    
    print(f"  Melhor versão anterior (v{best_version['version']}) - {promotion_metric}: {old_accuracy:.4f}")
    print(f"  Melhoria: {improvement:+.2f}%")
    
    if new_accuracy > old_accuracy:
        print(f"\n[OK] Novo modelo é MELHOR! Promovendo para 'Production'...")
        _transition_model_version(model_name, new_version.version, "Production")
        
        # Mover versão anterior para 'Staging'
        print(f"  Movendo versão anterior (v{best_version['version']}) para 'Staging'...")
        _transition_model_version(model_name, best_version['version'], "Staging")
        
        return True, f"Novo modelo promovido (melhoria de {improvement:+.2f}%)"
    else:
        print(f"\n[Warning] Novo modelo NÃO é melhor. Mantendo versão anterior em 'Production'...")
        _transition_model_version(model_name, new_version.version, "Archived")
        
        return False, f"Versão anterior mantida (degradação de {improvement:.2f}%)"


def _transition_model_version(model_name: str, version: str, stage: str) -> None:
    """
    Move uma versão do modelo para um estágio diferente.
    
    Args:
        model_name: Nome do modelo
        version: Número da versão
        stage: Estágio destino ('Production', 'Staging', 'Archived')
    """
    try:
        client = mlflow.tracking.MlflowClient()
        client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage=stage,
            archive_existing_versions=(stage == "Production")
        )
        print(f"[Ok] Versão {version} movida para '{stage}'")
    except Exception as e:
        print(f"[Error] Erro ao mover versão {version}: {e}")


def print_registry_summary(model_name: str) -> None:
    """
    Imprime um resumo de todas as versões do modelo no registry.
    
    Args:
        model_name: Nome do modelo
    """
    try:
        client = mlflow.tracking.MlflowClient()
        versions = client.search_model_versions(f"name = '{model_name}'")
        
        print(f"RESUMO DO MODEL REGISTRY: {model_name}")
        
        if not versions:
            print("Nenhuma versão registrada.")
        else:
            for version in sorted(versions, key=lambda v: int(v.version), reverse=True):
                run = client.get_run(version.run_id)
                accuracy = run.data.metrics.get('accuracy', 'N/A')
                
            
                
                print(f"\n Versão {version.version} [{version.current_stage}]")
                print(f"   Acurácia: {accuracy:.4f}" if isinstance(accuracy, float) else f"   Acurácia: {accuracy}")
                print(f"   Criação: {version.creation_timestamp}")
        
        
    except Exception as e:
        print(f"Erro ao buscar versões: {e}")


if __name__ == "__main__":
    print("Módulo de Model Registry carregado com sucesso!")
