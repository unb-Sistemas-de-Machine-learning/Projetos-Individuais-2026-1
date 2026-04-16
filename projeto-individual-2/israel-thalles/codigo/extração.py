from datasets import load_dataset
import os
from PIL import Image
import io

def baixar_amostras_isic():
    print("Conectando ao dataset mrbrobot/isic-2024...")
    try:
        conjuntos_de_dados = load_dataset("mrbrobot/isic-2024", split='train', streaming=True)
        
        amostras_desejadas_por_classe = {'maligno': 25, 'benigno': 25}
        contadores = {'maligno': 0, 'benigno': 0}
        
        os.makedirs("./dados/maligno", exist_ok=True)
        os.makedirs("./dados/benigno", exist_ok=True)

        for dado in conjuntos_de_dados:
            # No ISIC 2024, 'target' 1 é maligno, 0 é benigno
            rótulo = "maligno" if dado['target'] == 1 else "benigno"
            
            if contadores[rótulo] < amostras_desejadas_por_classe[rótulo]:
                # O dado['image'] geralmente já vem como um objeto PIL ou bytes
                imagem = dado['image']
                
                # Se vier em bytes, convertemos:
                if isinstance(imagem, dict) and 'bytes' in imagem:
                    imagem = Image.open(io.BytesIO(imagem['bytes']))
                
                if imagem.mode != 'RGB':
                    imagem = imagem.convert('RGB')
                
                caminho = f"./dados/{rótulo}/{rótulo}_{contadores[rótulo]}.png"
                imagem.save(caminho)
                
                contadores[rótulo] += 1
                print(f"Salvo: {rótulo} ({contadores[rótulo]}/25)")
                
            if all(contador >= 25 for contador in contadores.values()):
                break

        print("\n✅ Imagens prontas para o pipeline!")
        
    except Exception as erro:
        print(f"\n❌ Erro: {erro}")

if __name__ == "__main__":
    baixar_amostras_isic()