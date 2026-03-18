import matplotlib.pyplot as plt
import math


class Task:
    def __init__(self, name, arrival_time, execution_time, deadline):
        """
        name : Identifiant (ex: "T1")
        arrival_time : Date d'arrivée en heures (ex: 0.5 pour 0h30)
        execution_time : Durée en heures (ex: 1.5 pour 1h30)
        deadline : Date limite en heures (ex: 10 pour 10h00)
        """
        self.id = name
        
        # Conversion interne en minutes pour la précision de l'algo
        self.r = int(arrival_time * 60)      # Release date
        self.p = int(execution_time * 60)    # Processing time
        self.d = int(deadline * 60)          # Deadline
        
        # Pour l'affichage graphique
        self.original_r = arrival_time
        self.original_d = deadline
        self.duration_lbl = f"{execution_time}h"

    def __repr__(self):
        return f"Task({self.id}, r={self.original_r}h, p={self.duration_lbl}, d={self.original_d}h)"

class TariffProfile:
    def __init__(self):
        self.horizon_min = 1440 # 24h en minutes
        self.prices = [0.0] * self.horizon_min
        
    def add_interval(self, start_hour, end_hour, price_per_hour):
        price_per_min = price_per_hour / 60.0
        start_min = int(start_hour * 60)
        end_min = int(end_hour * 60)
        
        for t in range(start_min, end_min):
            if t < self.horizon_min:
                self.prices[t] = price_per_min

    def get_cost(self, start_min, end_min):
        if start_min >= self.horizon_min: return float('inf')
        real_end = min(end_min, self.horizon_min)
        total = sum(self.prices[t] for t in range(start_min, real_end))
        return total

# --- 2. ALGORITHME WAN & QI (DP PRÉCISE) ---

def solve_wan_qi_precision(tasks, tariff_profile):
    # 1. Tri EDD (Earliest Deadline First)
    sorted_tasks = sorted(tasks, key=lambda t: t.d)
    
    # DP[t_min] = (nb_taches, cout, liste_taches_planifiees)
    dp = {0: (0, 0.0, [])}
    
    print(f"Planification de {len(tasks)} tâches...")
    
    for task in sorted_tasks:
        current_dp = dp.copy()
        
        for t_prev, (count, cost, schedule) in current_dp.items():
            
            # Début = max(fin_tache_precedente, date_arrivee_tache)
            start_time = max(t_prev, task.r)
            end_time = start_time + task.p
            
            # Contraintes
            if end_time > tariff_profile.horizon_min: continue
            if end_time > task.d: continue
            
            # Calcul coût
            segment_cost = tariff_profile.get_cost(start_time, end_time)
            
            new_count = count + 1
            new_cost = cost + segment_cost
            new_sched = schedule + [(task, start_time, end_time)]
            
            # Mise à jour DP (Maximiser Nombre, puis Minimiser Coût)
            if end_time not in dp:
                dp[end_time] = (new_count, new_cost, new_sched)
            else:
                old_count, old_cost, _ = dp[end_time]
                if new_count > old_count or (new_count == old_count and new_cost < old_cost):
                    dp[end_time] = (new_count, new_cost, new_sched)
                    
    # Meilleur résultat final
    best_state = (0, float('inf'), [])
    for state in dp.values():
        cnt, cst, _ = state
        best_cnt, best_cst, _ = best_state
        if cnt > best_cnt:
            best_state = state
        elif cnt == best_cnt and cst < best_cst:
            best_state = state
            
    final_count, final_cost, final_schedule = best_state
    accepted = [x[0] for x in final_schedule]
    rejected = [t for t in tasks if t not in accepted]
    
    return final_schedule, accepted, rejected, final_cost

# --- 3. AFFICHAGE ---

def plot_schedule(schedule_data, profile, accepted, rejected, P_PEAK):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True, gridspec_kw={'height_ratios': [1, 2]})
    plt.subplots_adjust(hspace=0.2)
    
    # Prix
    times_h = [t/60 for t in range(1441)]
    prices_h = [profile.prices[t]*60 for t in range(1440)] + [profile.prices[1439]*60]
    
    ax1.step(times_h, prices_h, where='post', color='black', linewidth=1)
    ax1.fill_between(times_h, prices_h, step="post", alpha=0.2, color='gray')
    ax1.set_ylabel('Prix (€/h)')
    ax1.set_title(f'Planning Optimisé ({len(accepted)}/{len(accepted)+len(rejected)} tâches)')

    # Gantt
    if schedule_data:
        # Trier l'affichage par ID ou par ordre de passage
        job_ids = [t.id for t in accepted]
        y_map = {jid: i for i, jid in enumerate(job_ids)}
        
        for task, start_m, end_m in schedule_data:
            y = y_map[task.id]
            start_h = start_m / 60
            dur_h = (end_m - start_m) / 60
            
            # Barre Tâche
            ax2.broken_barh([(start_h, dur_h)], (y - 0.4, 0.8), facecolors='#3498db', edgecolor='white')
            ax2.text(start_h + dur_h/2, y, task.id, ha='center', va='center', color='white', fontweight='bold')
            
            # Marqueurs contraintes
            ax2.plot([task.original_r, task.original_d], [y, y], 'k--', alpha=0.3, zorder=0) # Fenêtre
            ax2.plot(task.original_d, y, 'r|', ms=12, mew=2) # Deadline
            ax2.plot(task.original_r, y, 'g|', ms=12, mew=2) # Arrival

        ax2.set_yticks(range(len(job_ids)))
        ax2.set_yticklabels(job_ids)
    
    ax2.set_xlabel('Heures')
    ax2.set_xlim(0, 24)
    ax2.set_xticks(range(25))
    ax2.grid(True, axis='x', linestyle=':', alpha=0.5)
    plt.tight_layout()
    plt.show()

# --- 4. EXÉCUTION (VOTRE SYNTAXE) ---

def run_custom_scenario():
    # 1. Définir les prix
    profile = TariffProfile()
    P_OFF, P_MID, P_PEAK = 10, 30, 80
    profile.add_interval(0, 7, P_OFF)
    profile.add_interval(7, 11, P_MID)
    profile.add_interval(11, 17, P_PEAK)
    profile.add_interval(17, 20, P_MID)
    profile.add_interval(20, 24, P_OFF)

    
    tasks_list = [
        Task("T1", arrival_time=0, execution_time=1.5, deadline=10),
        Task("T10", arrival_time=0.5, execution_time=1, deadline=7),
        Task("T2", arrival_time=2, execution_time=2, deadline=12),
        Task("T4", arrival_time=5, execution_time=3, deadline=15),
    ]

    # 3. Lancer l'algo
    schedule, accepted, rejected, cost = solve_wan_qi_precision(tasks_list, profile)

    # 4. Résultats
    print(f"Coût Total : {cost:.2f}")
    print("Détails du planning :")
    for task, s, e in schedule:
        print(f" - {task.id} : {int(s/60)}h{s%60:02d} -> {int(e/60)}h{e%60:02d}")

    plot_schedule(schedule, profile, accepted, rejected, P_PEAK)

if __name__ == "__main__":
    run_custom_scenario()