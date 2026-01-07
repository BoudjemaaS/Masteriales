
import copy


class Task:
    def __init__(self, name, arrival_time, execution_time, deadline):
        self.name = name # Nom de la tâche
        self.arrival_time = arrival_time # Date d'arrivée de la tâche
        self.execution_time = execution_time # Temps d'exécution total de la tâche
        self.remaining_time = execution_time # Temps d'exécution restant
        self.deadline = deadline # Échéance de la tâche

    def get_laxity(self, current_time):
        # Laxité = (Échéance - Temps actuel) - Temps d'exécution restant
        # Correspond au temps disponible avant l'échéance après avoir pris en compte le temps d'exécution restant
        return (self.deadline - current_time) - self.remaining_time
    

def get_cost_at_hour(hour, tariff_model):


    if tariff_model == 2:
        #7h-11h & 17h-21h: Peak, autres: OffPeak
        #hour = t % 24
        if 7 <= hour < 11 or 17 <= hour < 21: return 3 # Peak
        return 1 # OffPeak

    else:
        # 0h-7h: OffPeak, 7h-11h: MidPeak, 11h-17h: Peak, 17h-20h: MidPeak, 20h-24h: OffPeak
        #hour = t % 24
        if 11 <= hour < 17: return 3 # Peak
        if 7 <= hour < 11 or 17 <= hour < 20: return 2 # MidPeak
        return 1 # OffPeak





def simulate(tasks_list, strategy="EDF",tariff_model=3):
    current_time = 0
    completed_tasks = []
    active_tasks = []
    failed_tasks = []
    total_cost = 0
    total_inital_tasks = len(tasks_list)
    
    # Simulation pas à pas
    while tasks_list or active_tasks:
        
        # 1. Ajouter les tâches qui viennent d'arriver
        new_arrivals = [t for t in tasks_list if t.arrival_time == current_time]
        active_tasks.extend(new_arrivals)
        for t in new_arrivals: tasks_list.remove(t)


        # Si (Temps actuel + Temps restant > Deadline), la tâche est condamnée et supprimée
        missed = [t for t in active_tasks if (current_time + t.remaining_time) > t.deadline]
        for t in missed:
            failed_tasks.append(t)
            active_tasks.remove(t)

        if active_tasks:
            # 2. Choisir la tâche selon la stratégie
            if strategy == "EDF":
                active_tasks.sort(key=lambda x: x.deadline)
            elif strategy == "LLF":
                active_tasks.sort(key=lambda x: x.get_laxity(current_time))

            current_task = active_tasks[0]
            
            # 3. Calcul du coût (basé sur la Figure 1 de votre document)
            cost_multiplier = get_cost_at_hour(current_time, tariff_model)
            total_cost += cost_multiplier
            
            # 4. Exécuter
            current_task.remaining_time -= 1
            if current_task.remaining_time == 0:
                active_tasks.remove(current_task)
                completed_tasks.append(current_task)

        current_time += 1
    print("End time:", current_time)
    print("Completed tasks:" , len(completed_tasks)/total_inital_tasks * 100, "%")
    return total_cost
    
    
tasks_list = [
    Task("T1", arrival_time=0, execution_time=4, deadline=10),
    Task("T2", arrival_time=2, execution_time=3, deadline=8),
    Task("T3", arrival_time=4, execution_time=2, deadline=12),
    Task("T4", arrival_time=6, execution_time=1, deadline=9),
    Task("T5", arrival_time=8, execution_time=2, deadline=15),
    Task("T6", arrival_time=1, execution_time=5, deadline=14),
    Task("T7", arrival_time=3, execution_time=2, deadline=11),
    Task("T8", arrival_time=5, execution_time=3, deadline=13),
    Task("T9", arrival_time=7, execution_time=4, deadline=16)
]

print("Total cost with EDF:", simulate(copy.deepcopy(tasks_list),strategy="EDF", tariff_model=3))

print("Total cost with LLF:", simulate(copy.deepcopy(tasks_list),strategy="LLF", tariff_model=3))