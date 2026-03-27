# backend/scapy_module/auto_trainer.py
# Auto-treino com comparação de modelos e persistência de estado
# AGORA USA OPÇÃO 4 (COMBINAR TUDO) DO train_new_model.py

import time
import threading
import json
import pickle
from pathlib import Path
from datetime import datetime
import sys

PROJECT_PATH = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_PATH))

from backend.scapy_module.predictor import ModelPredictor
from backend.scapy_module.train_new_model import NovoModeloTrainer
import numpy as np
from sklearn.metrics import accuracy_score


class AutoTrainer:
    """
    Orquestrador do auto-treino com persistência de estado
    """
    
    def __init__(self):
        self.project_root = PROJECT_PATH
        self.models_folder = self.project_root / "models"
        self.logs_dir = self.project_root / "data" / "logs"
        self.historico_file = self.logs_dir / "auto_treino_historico.json"
        self.estado_file = self.logs_dir / "auto_treino_estado.json"
        
        # Configurações
        self.ativo = False
        self.intervalo_horas = 24
        self.thread = None
        
        # Criar pastas
        self.models_folder.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Carregar estado salvo
        self._carregar_estado()
        
        # Carregar histórico
        self.historico = self._carregar_historico()
        
        print("🤖 AutoTrainer inicializado (usa opção COMBINAR TUDO)")
    
    def _carregar_estado(self):
        """Carrega estado salvo"""
        if self.estado_file.exists():
            try:
                with open(self.estado_file, 'r') as f:
                    estado = json.load(f)
                    self.ativo = estado.get('ativo', False)
                    self.intervalo_horas = estado.get('intervalo_horas', 24)
                    print(f"📂 Estado carregado: ativo={self.ativo}, intervalo={self.intervalo_horas}h")
            except:
                pass
    
    def _guardar_estado(self):
        """Guarda estado atual"""
        estado = {
            'ativo': self.ativo,
            'intervalo_horas': self.intervalo_horas,
            'ultima_atualizacao': datetime.now().isoformat()
        }
        with open(self.estado_file, 'w') as f:
            json.dump(estado, f, indent=2)
    
    def _carregar_historico(self):
        """Carrega histórico de auto-treinos"""
        if self.historico_file.exists():
            try:
                with open(self.historico_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _guardar_historico(self):
        """Guarda histórico de auto-treinos"""
        with open(self.historico_file, 'w') as f:
            json.dump(self.historico[-50:], f, indent=2)
    
    def _obter_modelo_atual(self):
        """Retorna o caminho do modelo atual em uso"""
        modelo_principal = self.models_folder / "modelo_principal.pkl"
        
        if not modelo_principal.exists():
            modelos = list(self.models_folder.glob("modelo_fluxo_*.pkl"))
            if modelos:
                return max(modelos, key=lambda x: x.stat().st_mtime)
            return None
        
        return modelo_principal
    
    def _obter_ultimo_modelo_candidato(self):
        """Retorna o último modelo treinado"""
        modelos = list(self.models_folder.glob("modelo_fluxo_*.pkl"))
        if not modelos:
            return None
        return max(modelos, key=lambda x: x.stat().st_mtime)
    
    def _treinar_novo_modelo(self):
        """Treina um novo modelo usando a opção COMBINAR TUDO"""
        print("\n📊 Iniciando treino automático...")
        print("   🔥 Usando opção COMBINAR TUDO (PCAPs + Logs + CSVs)")

        try:
            trainer = NovoModeloTrainer()
            
            # Usar COMBINAR TUDO (opção 4)
            X, y, scaler = trainer.combinar_tudo()
            
            if X is None or y is None:
                print("   ❌ Não foi possível carregar dados")
                return None
            
            model, acuracia = trainer.treinar_novo_modelo(X, y)
            
            if model:
                print(f"   ✅ Novo modelo treinado! Acurácia: {acuracia*100:.2f}%")
                return self._obter_ultimo_modelo_candidato()
            else:
                print("   ❌ Falha no treino")
                return None
                
        except Exception as e:
            print(f"   ❌ Erro no treino: {e}")
            return None
    
    def _comparar_modelos(self, modelo_atual_path, modelo_candidato_path):
        """Compara dois modelos usando dados de validação"""
        print("\n📊 Comparando modelos...")
        
        try:
            predictor_atual = ModelPredictor(modelo_atual_path)
            predictor_candidato = ModelPredictor(modelo_candidato_path)
            
            # Usar dados de validação
            trainer = NovoModeloTrainer()
            X, y, _ = trainer.combinar_tudo()
            
            if X is None or y is None:
                print("   ⚠️ Não foi possível carregar dados para comparação")
                return {'melhor': 'atual', 'acuracia_atual': 0, 'acuracia_candidato': 0, 'melhoria': 0}
            
            # Avaliar modelo atual
            y_pred_atual = predictor_atual.model.predict(X)
            y_pred_binary_atual = np.where(y_pred_atual == 1, 0, 1)
            acuracia_atual = accuracy_score(y, y_pred_binary_atual)
            
            # Avaliar modelo candidato
            y_pred_candidato = predictor_candidato.model.predict(X)
            y_pred_binary_candidato = np.where(y_pred_candidato == 1, 0, 1)
            acuracia_candidato = accuracy_score(y, y_pred_binary_candidato)
            
            melhoria = acuracia_candidato - acuracia_atual
            
            print(f"   Modelo atual: {acuracia_atual*100:.2f}%")
            print(f"   Modelo candidato: {acuracia_candidato*100:.2f}%")
            print(f"   Melhoria: {melhoria*100:+.2f}%")
            
            if acuracia_candidato > acuracia_atual:
                print("   ✅ Candidato é MELHOR! Será promovido.")
                return {
                    'melhor': 'candidato',
                    'acuracia_atual': acuracia_atual,
                    'acuracia_candidato': acuracia_candidato,
                    'melhoria': melhoria
                }
            else:
                print("   ⚠️ Candidato NÃO é melhor. Mantendo modelo atual.")
                return {
                    'melhor': 'atual',
                    'acuracia_atual': acuracia_atual,
                    'acuracia_candidato': acuracia_candidato,
                    'melhoria': melhoria
                }
                
        except Exception as e:
            print(f"   ❌ Erro na comparação: {e}")
            return {'melhor': 'atual', 'acuracia_atual': 0, 'acuracia_candidato': 0, 'melhoria': 0}
    
    def _promover_modelo(self, modelo_candidato_path):
        """Promove o modelo candidato a modelo principal"""
        print("\n🚀 Promovendo modelo...")
        
        modelo_principal = self.models_folder / "modelo_principal.pkl"
        
        try:
            import shutil
            shutil.copy(modelo_candidato_path, modelo_principal)
            print(f"   ✅ Modelo promovido: {modelo_candidato_path.name} → modelo_principal.pkl")
            return True
        except Exception as e:
            print(f"   ❌ Erro ao promover modelo: {e}")
            return False
    
    def executar_ciclo(self):
        """Executa um ciclo completo de auto-treino"""
        print("\n" + "="*70)
        print(f"🔄 CICLO DE AUTO-TREINO - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        print("   🔥 Usando opção COMBINAR TUDO (PCAPs + Logs + CSVs)")
        
        # 1. Obter modelo atual
        modelo_atual = self._obter_modelo_atual()
        if modelo_atual is None:
            print("⚠️ Nenhum modelo atual encontrado!")
            print("🔄 A criar modelo base com COMBINAR TUDO...")
            modelo_candidato = self._treinar_novo_modelo()
            if modelo_candidato:
                self._promover_modelo(modelo_candidato)
            return
        
        print(f"📂 Modelo atual: {modelo_atual.name}")
        
        # 2. Treinar novo modelo
        modelo_candidato = self._treinar_novo_modelo()
        if modelo_candidato is None:
            print("❌ Falha no treino. Ciclo abortado.")
            return
        
        print(f"📂 Modelo candidato: {modelo_candidato.name}")
        
        # 3. Comparar modelos
        resultado = self._comparar_modelos(modelo_atual, modelo_candidato)
        
        # 4. Promover se melhor
        promovido = False
        if resultado['melhor'] == 'candidato':
            promovido = self._promover_modelo(modelo_candidato)
        
        # 5. Guardar histórico
        entrada_historico = {
            'data': datetime.now().isoformat(),
            'modelo_atual': modelo_atual.name,
            'modelo_candidato': modelo_candidato.name,
            'acuracia_atual': resultado['acuracia_atual'],
            'acuracia_candidato': resultado['acuracia_candidato'],
            'melhoria': resultado['melhoria'],
            'promovido': promovido
        }
        
        self.historico.append(entrada_historico)
        self._guardar_historico()
        
        # 6. Mostrar resultado
        print("\n" + "="*70)
        if promovido:
            print(f"✅ AUTO-TREINO CONCLUÍDO - MODELO PROMOVIDO!")
            print(f"   Melhoria: {resultado['melhoria']*100:+.2f}%")
        else:
            print(f"ℹ️ AUTO-TREINO CONCLUÍDO - MODELO MANTIDO")
            print(f"   Melhoria: {resultado['melhoria']*100:+.2f}%")
        print("="*70)
    
    def _loop(self):
        """Loop principal do auto-treino"""
        while self.ativo:
            self.executar_ciclo()
            
            intervalo_segundos = self.intervalo_horas * 3600
            print(f"\n⏰ Próximo treino em {self.intervalo_horas} horas")
            
            for _ in range(intervalo_segundos):
                if not self.ativo:
                    break
                time.sleep(1)
    
    def iniciar(self, intervalo_horas=24):
        """Inicia o auto-treino"""
        if self.ativo:
            print("⚠️ Auto-treino já está ativo")
            return
        
        self.intervalo_horas = intervalo_horas
        self.ativo = True
        self._guardar_estado()
        
        self.thread = threading.Thread(target=self._loop)
        self.thread.daemon = True
        self.thread.start()
        
        print(f"✅ Auto-treino ATIVADO (intervalo: {intervalo_horas} horas)")
        print("   🔥 Usando opção COMBINAR TUDO (PCAPs + Logs + CSVs)")
    
    def parar(self):
        """Para o auto-treino"""
        if not self.ativo:
            print("⚠️ Auto-treino já está inativo")
            return
        
        self.ativo = False
        self._guardar_estado()
        
        if self.thread:
            self.thread.join(timeout=5)
        
        print("✅ Auto-treino DESATIVADO")
    
    def get_status(self):
        """Retorna status atual"""
        modelo_atual = self._obter_modelo_atual()
        ultimo_treino = self.historico[-1] if self.historico else None
        
        return {
            'ativo': self.ativo,
            'intervalo_horas': self.intervalo_horas,
            'modelo_atual': modelo_atual.name if modelo_atual else None,
            'ultimo_treino': ultimo_treino,
            'historico': self.historico[-10:]
        }


# Instância global
auto_trainer = AutoTrainer()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-treino com comparação de modelos')
    parser.add_argument('--iniciar', action='store_true', help='Inicia auto-treino')
    parser.add_argument('--parar', action='store_true', help='Para auto-treino')
    parser.add_argument('--status', action='store_true', help='Mostra status')
    parser.add_argument('--intervalo', type=int, help='Define intervalo em horas')
    parser.add_argument('--ciclo', action='store_true', help='Executa um ciclo manualmente')
    
    args = parser.parse_args()
    
    if args.status:
        status = auto_trainer.get_status()
        print("\n" + "="*50)
        print("📊 STATUS DO AUTO-TREINO")
        print("="*50)
        print(f"Ativo: {'✅ SIM' if status['ativo'] else '❌ NÃO'}")
        print(f"Intervalo: {status['intervalo_horas']} horas")
        print(f"Modelo atual: {status['modelo_atual']}")
        print(f"🔥 Usando opção COMBINAR TUDO (PCAPs + Logs + CSVs)")
        if status['ultimo_treino']:
            print(f"Último treino: {status['ultimo_treino']['data'][:19]}")
            print(f"Melhoria: {status['ultimo_treino']['melhoria']*100:+.2f}%")
        else:
            print("Nenhum treino realizado ainda")
        print("="*50)
    
    elif args.iniciar:
        intervalo = args.intervalo if args.intervalo else 24
        auto_trainer.iniciar(intervalo)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️ A parar auto-treino...")
            auto_trainer.parar()
    
    elif args.parar:
        auto_trainer.parar()
    
    elif args.ciclo:
        auto_trainer.executar_ciclo()
    
    else:
        print("Uso: python auto_trainer.py --status")
        print("     python auto_trainer.py --iniciar [--intervalo 24]")
        print("     python auto_trainer.py --parar")
        print("     python auto_trainer.py --ciclo")

if __name__ == "__main__":
    main()