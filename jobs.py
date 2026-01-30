import matplotlib.pyplot as plt
import matplotlib.patches as mpatches



# --- 1. MODÉLISATION ---

class Job:
    def __init__(self, id, processing_time, deadline):
        self.id = id
        self.p = processing_time
        self.d = deadline 

    def __repr__(self):
        return f"Job({self.id}, p={self.p}, d={self.d})"

class TariffProfile:
    def __init__(self, unit_duration_minutes=60):
        self.unit_duration = unit_duration_minutes
        self.slots = [] 
        
    def add_interval(self, start_hour, end_hour, price):
        start_idx = int(start_hour * 60 / self.unit_duration)
        end_idx = int(end_hour * 60 / self.unit_duration)
        for t in range(start_idx, end_idx):
            self.slots.append(price)

    def get_price(self, t):
        if 0 <= t < len(self.slots):
            return self.slots[t]
        return float('inf')

    def get_horizon(self):
        return len(self.slots)

# --- 2. ALGORITHME WAN & QI (2010) - APPROCHE PROGRAMMATION DYNAMIQUE ---

def solve_wan_qi_max_on_time(jobs, tariff_profile):
    """
    Algorithme exact (Pseudo-Polynomial) pour :
    1. Maximiser le nombre de tâches finies avant deadline.
    2. Minimiser le coût total.
    
    Inspiré de Wan & Qi (2010) pour les cas discrets.
    """
    
    # 1. Tri EDD (Earliest Deadline First) : condition nécessaire pour l'optimalité
    sorted_jobs = sorted(jobs, key=lambda j: j.d)
    
    horizon = tariff_profile.get_horizon()
    
    # DP[t] stocke le meilleur état possible se terminant exactement au temps t
    # État = (nombre_taches, cout_total, liste_jobs_planifies)
    # On initialise avec 0 tâche, coût 0 au temps 0.
    dp = {0: (0, 0, [])} 
    
    print(f"Traitement de {len(jobs)} tâches avec l'algo Wan & Qi...")

    for job in sorted_jobs:
        # On crée une copie pour cette itération pour ne pas utiliser le même job 2 fois
        current_dp_snapshot = dp.copy()
        
        # Pour chaque temps de fin 't' existant dans nos états précédents
        for t_end_prev, (count, cost, schedule_list) in current_dp_snapshot.items():
            
            # Calcul du nouveau temps de fin si on ajoute ce job
            t_start_new = t_end_prev
            t_end_new = t_start_new + job.p
            
            # VÉRIFICATIONS (Contraintes)
            # 1. Ne pas dépasser l'horizon
            if t_end_new > horizon: continue
            
            # 2. Ne pas dépasser la DEADLINE du job
            if t_end_new > job.d: continue
            
            # Calcul du coût d'ajout
            job_cost = 0
            valid_slots = True
            current_slots = []
            
            for k in range(t_start_new, t_end_new):
                p = tariff_profile.get_price(k)
                if p == float('inf'): 
                    valid_slots = False
                    break
                job_cost += p
                current_slots.append(k)
            
            if not valid_slots: continue
            
            # NOUVEL ÉTAT CANDIDAT
            new_count = count + 1
            new_total_cost = cost + job_cost
            new_schedule = schedule_list + [(job, current_slots)]
            
            # MISE À JOUR DP
            # Si on atteint le temps t_end_new mieux qu'avant (plus de tâches ou moins cher)
            if t_end_new not in dp:
                dp[t_end_new] = (new_count, new_total_cost, new_schedule)
            else:
                existing_count, existing_cost, _ = dp[t_end_new]
                # On préfère plus de tâches, ou à nombre égal, moins cher
                if new_count > existing_count or (new_count == existing_count and new_total_cost < existing_cost):
                    dp[t_end_new] = (new_count, new_total_cost, new_schedule)

    # --- SÉLECTION DE LA MEILLEURE SOLUTION ---
    # On cherche dans DP l'état avec le max de tâches et le coût min
    best_state = (0, 0, [])
    
    for t, state in dp.items():
        count, cost, sched = state
        best_count, best_cost, _ = best_state
        
        if count > best_count:
            best_state = state
        elif count == best_count and cost < best_cost:
            best_state = state
            
    # Reconstruction pour l'affichage
    final_count, final_cost, final_sched_list = best_state
    
    schedule_map = {}
    accepted_ids = []
    for job, slots in final_sched_list:
        accepted_ids.append(job.id)
        for s in slots:
            schedule_map[s] = job.id
            
    # Identifier les rejetés
    all_ids = set(j.id for j in jobs)
    rejected_ids = list(all_ids - set(accepted_ids))
    rejected_jobs = [j for j in jobs if j.id in rejected_ids]
    accepted_jobs = [j for j in jobs if j.id in accepted_ids] # Pour avoir les objets
            
    return schedule_map, accepted_jobs, rejected_jobs, final_cost

# --- 3. AFFICHAGE (Visualisation Identique) ---

def plot_schedule_wan_qi(schedule, profile, accepted_jobs, rejected_jobs, P_OFF, P_MID, P_PEAK):
    horizon = 24
    times = list(range(horizon + 1))
    prices = [profile.get_price(t) for t in range(horizon)]
    prices_plot = prices + [prices[-1]]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True, gridspec_kw={'height_ratios': [1, 2]})
    plt.subplots_adjust(hspace=0.15)

    # Profil Tarifaire
    ax1.step(times, prices_plot, where='post', color='black', linewidth=1.5)
    for t in range(horizon):
        p = profile.get_price(t)
        color = '#ffcccc' if p == P_PEAK else ('#ffffcc' if p == P_MID else '#ccffcc')
        ax1.axvspan(t, t+1, color=color, alpha=0.6)
    
    # Deadlines (toutes les tâches)
    all_jobs = accepted_jobs + rejected_jobs
    all_jobs.sort(key=lambda j: j.d) # Pour affichage propre
    
    for i, job in enumerate(all_jobs):
        # Petit décalage hauteur pour lisibilité des deadlines
        h_pos = P_PEAK - (i % 3) * 1.5 
        ax1.axvline(x=job.d, color='blue', linestyle=':', alpha=0.4)
        ax1.text(job.d, h_pos, f"D_{job.id}", rotation=90, fontsize=8, color='blue', ha='right')

    ax1.set_ylabel('Prix (€)')
    ax1.set_title(f'Wan & Qi (2010): {len(accepted_jobs)} Acceptées / {len(rejected_jobs)} Rejetées')
    ax1.set_yticks([P_OFF, P_MID, P_PEAK])

    # Gantt
    if accepted_jobs:
        job_ids = [j.id for j in accepted_jobs]
        # On garde l'ordre de traitement pour l'axe Y
        y_map = {jid: i for i, jid in enumerate(job_ids)}
        
        for t, job_id in schedule.items():
            if 0 <= t < horizon:
                y_idx = y_map[job_id]
                ax2.broken_barh([(t, 1)], (y_idx - 0.4, 0.8), facecolors='#8e44ad', edgecolor='white')
                ax2.text(t + 0.5, y_idx, job_id, ha='center', va='center', color='white', fontweight='bold')
                
        # Marquer la deadline sur la ligne de la tâche
        for job in accepted_jobs:
            y = y_map[job.id]
            ax2.plot(job.d, y, 'r|', markeredgewidth=3, markersize=15)
        
        ax2.set_yticks(range(len(job_ids)))
        ax2.set_yticklabels(job_ids)
    else:
        ax2.text(12, 0.5, "Aucune tâche planifiée", ha='center')

    ax2.set_ylabel('Tâches Planifiées')
    ax2.set_xlabel('Heure')
    ax2.set_xlim(0, horizon)
    ax2.set_xticks(range(horizon + 1))
    ax2.grid(True, axis='x', linestyle=':', alpha=0.7)
    
    plt.tight_layout()
    plt.show()

# --- 4. SCÉNARIO DE TEST ---

def run_wan_qi_scenario():
    profile = TariffProfile()
    P_OFF, P_MID, P_PEAK = 1, 3, 8
    
    profile.add_interval(0, 7, P_OFF)
    profile.add_interval(7, 11, P_MID)
    profile.add_interval(11, 17, P_PEAK)
    profile.add_interval(17, 20, P_MID)
    profile.add_interval(20, 24, P_OFF)
    
    # SCÉNARIO COMPLEXE :
    # J1, J2, J3 ont la même deadline (10h).
    # J1 (2h) coûte cher si mal placée.
    # J4 est longue (6h) avec deadline large.
    # J5 est courte mais deadline très serrée (2h).
    


    jobs = [
        Job("T1", 2, 10),
        Job("T10" , 1, 7),
        Job("T11" , 1, 9),
        Job("T7", 2, 11),
        Job("T2", 3, 8),
        Job("T9", 4, 25),
        Job("T4", 1, 9),
        Job("T14", 2, 11),
        Job("T3", 2, 12),
        Job("T5", 2, 12),
        Job("T6", 5, 14),
        Job("T8", 2, 13)
    ]



    
    print(f"--- Scénario Wan & Qi ---")
    
    schedule, accepted, rejected, cost = solve_wan_qi_max_on_time(jobs, profile)
    
    print(f"\nRésultats Optimaux :")
    print(f"✅ Tâches acceptées ({len(accepted)}) : {[j.id for j in accepted]}")
    print(f"❌ Tâches rejetées ({len(rejected)}) : {[j.id for j in rejected]}")
    print(f"💰 Coût total : {cost}")
    
    plot_schedule_wan_qi(schedule, profile, accepted, rejected, P_OFF, P_MID, P_PEAK)

if __name__ == "__main__":
    run_wan_qi_scenario()