import copy
import time


from task2 import greedy, rolling_horizon, tariff_model as tm2
from Tasks import online_full_tasks, tariff_model as tm_tasks
from mv2_4 import solve_wan_qi_precision, TariffProfile

# --- 1. CLASSE UNIFIÉE ---
class UnifiedTask:
    def __init__(self, name, arrival_time, execution_time, deadline):
        # Attributs requis par task2.py et Tasks.py (Glouton, Rolling Horizon, Online)
        self.name = name
        self.arrival_time = round(arrival_time * 60)
        self.execution_time = round(execution_time * 60)
        self.remaining_time = round(execution_time * 60)
        self.deadline = round(deadline * 60)
        
        # Attributs requis par mv2_4.py (DP WAN & QI)
        self.id = name
        self.r = int(arrival_time * 60)
        self.p = int(execution_time * 60)
        self.d = int(deadline * 60)
        self.original_r = arrival_time
        self.original_d = deadline
        self.duration_lbl = f"{execution_time}h"

    def get_laxity(self, current_time):
        # Méthode requise par task2.py et Tasks.py
        return round(((self.deadline - current_time) - self.remaining_time), 2)
        
    def __repr__(self):
        return f"Task({self.name}, arr={self.original_r}h, exec={self.duration_lbl}, dead={self.original_d}h)"


# --- 2. CRÉATION DES PROFILS TARIFAIRES ---
# Pour task2.py et Tasks.py, on utilise le tariff_model = 2 (Peak 7h-11h et 17h-21h)
MODEL_TARIFAIRE_INT = 2 

# Pour mv2_4.py, on recrée exactement le même modèle avec la classe TariffProfile
profile_dp = TariffProfile()
profile_dp.add_interval(0, 7, 1)    # OffPeak
profile_dp.add_interval(7, 11, 3)   # Peak
profile_dp.add_interval(11, 17, 1)  # OffPeak
profile_dp.add_interval(17, 21, 3)  # Peak
profile_dp.add_interval(21, 24, 1)  # OffPeak


# --- 3. LES 3 DATASETS DE TEST ---
datasets = {
    "DATASET A : Standard (Mixte)": [
        UnifiedTask("T1", 0, 2.5, 10),
        UnifiedTask("T2", 2, 3, 8),
        UnifiedTask("T3", 4, 2, 12),
        UnifiedTask("T4", 6, 1, 9),
        UnifiedTask("T5", 8, 2.3, 12)
    ],
    "DATASET B : Haute Congestion (Arrivées simultanées en heure de pointe)": [
        UnifiedTask("C1", 7.0, 2.0, 9.5),
        UnifiedTask("C2", 7.5, 1.5, 9.5),
        UnifiedTask("C3", 8.0, 2.0, 11.0),
        UnifiedTask("C4", 8.5, 1.0, 10.0),
    ],
    "DATASET C : Haute Laxité (Beaucoup de marge pour optimiser)": [
        UnifiedTask("F1", 0.0, 4.0, 20.0),
        UnifiedTask("F2", 2.0, 3.0, 22.0),
        UnifiedTask("F3", 6.0, 5.0, 23.0),
    ]
}


# --- 4. EXÉCUTION DU BENCHMARK ---
def run_benchmark():
    for dataset_name, tasks in datasets.items():
        print(f"\n{'='*60}")
        print(f"🚀 LANCEMENT DU TEST : {dataset_name}")
        print(f"{'='*60}")

        # 1. Test Programmation Dynamique (mv2_4.py)
        print("\n--- 1. DP (WAN & QI - Optimal Offline) ---")
        tasks_dp = copy.deepcopy(tasks)
        schedule, accepted, rejected, cost = solve_wan_qi_precision(tasks_dp, profile_dp)
        print(f"Coût Total : {cost:.2f}")
        print(f"Tâches acceptées : {len(accepted)}/{len(tasks)}")

        # 2. Test Greedy EDF (task2.py)
        print("\n--- 2. GREEDY EDF (Sans opti coût) ---")
        tasks_greedy = copy.deepcopy(tasks)
        # On capture la sortie console standard de ta fonction greedy
        history_greedy = greedy(tasks_greedy, strategy="EDF", tariff_model=MODEL_TARIFAIRE_INT, cost_opt=False)

        # 3. Test Rolling Horizon (task2.py)
        print("\n--- 3. ROLLING HORIZON ---")
        tasks_rh = copy.deepcopy(tasks)
        history_rh = rolling_horizon(tasks_rh, strategy="EDF", tariff_model=MODEL_TARIFAIRE_INT)

        # Note: Si tu veux aussi tester online_full_tasks() de Tasks.py, il faudra légèrement
        # adapter la fonction dans ton fichier Tasks.py car elle utilise une variable globale `tasks_list`
        # au lieu de la prendre en paramètre. 

if __name__ == "__main__":
    run_benchmark()