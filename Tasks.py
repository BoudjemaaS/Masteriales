
import copy
import time


class Task:
    def __init__(self, name, arrival_time, execution_time, deadline):
        self.name = name # Nom de la tâche
        self.arrival_time = round(arrival_time * 60,2) # Date d'arrivée de la tâche
        self.execution_time = round(execution_time * 60,2)  # Temps d'exécution total de la tâche
        self.remaining_time = round(execution_time * 60,2) # Temps d'exécution restant
        self.deadline = round(deadline * 60,2) # Échéance de la tâche

    def get_laxity(self, current_time):
        # Laxité = (Échéance - Temps actuel) - Temps d'exécution restant
        # Correspond au temps disponible avant l'échéance après avoir pris en compte le temps d'exécution restant
        return round(((self.deadline - current_time) - self.remaining_time),2)   
    

def get_cost_at_hour(hour, tariff_model):

    hour = round(hour/60, 2)  # Convertir en heures
    price = 0

    if tariff_model == 2:
        #7h-11h & 17h-21h: Peak, autres: OffPeak
        #hour = t % 24
        if 7 <= hour < 11 or 17 <= hour < 21:
            price = 3 # Peak

        else:
            price = 1 # OffPeak

    else:
        # 0h-7h: OffPeak, 7h-11h: MidPeak, 11h-17h: Peak, 17h-20h: MidPeak, 20h-24h: OffPeak
        #hour = t % 24
        if 11 <= hour < 17: 
            price = 3 # Peak
        elif 7 <= hour < 11 or 17 <= hour < 20: 
            price = 2 # MidPeak
        else:
            price = 1 # OffPeak

    return price/60  # Convertir en coût par minute


def greedy(tasks_list, strategy="EDF",tariff_model=3,cost_opt=False):
    #Algorithme d'ordonnancement glouton avec optimisation de coût optionnelle

    current_time = 0 #Début de la simulation
    completed_tasks = [] #Liste des tâches complétées
    active_tasks = [] #Liste des tâches actives
    failed_tasks = [] #Liste des tâches échouées
    total_cost = 0 #Coût total de l'ordonnancement 
    total_inital_tasks = len(tasks_list) #Nombre total de tâches initiales
    history = [] #Historique des taches pour le diagramme de Gantt
    start_loop_time = time.time()
    
    # Simulation pas à pas
    while tasks_list or active_tasks:
        
        #Ajout des tâches qui viennent d'arriver
        new_arrivals = [t for t in tasks_list if t.arrival_time == current_time] #Tâches arrivant à l'instant t
        active_tasks.extend(new_arrivals)
        for t in new_arrivals: tasks_list.remove(t)


        # Si (Temps actuel + Temps restant > Deadline), la tâche est condamnée et supprimée
        missed = [t for t in active_tasks if (current_time + t.remaining_time) > t.deadline]
        for t in missed:
            failed_tasks.append(t)
            active_tasks.remove(t)

        if active_tasks:
            #Trier et choisir la tâche selon la stratégie
            if strategy == "EDF":
                active_tasks.sort(key=lambda x: x.deadline)
            elif strategy == "LLF":
                active_tasks.sort(key=lambda x: x.get_laxity(current_time))

            current_task = active_tasks[0]
            

            current_price = get_cost_at_hour(current_time, tariff_model)
            laxity = current_task.get_laxity(current_time)

            #Econoime de coût si on peut retarder l'exécution
            if not cost_opt or current_price < 2/60 or laxity == 0:
                
                history.append((current_time, current_task.name, current_price))
                #Ajout du coût (par minute)
                cost_multiplier = get_cost_at_hour(current_time, tariff_model)
                total_cost += cost_multiplier
                
                #Exécution de la tâche pendant une unité de temps
                current_task.remaining_time -= 1
                if current_task.remaining_time == 0:
                    active_tasks.remove(current_task)
                    completed_tasks.append(current_task)

        current_time += 1

    print("Simulation completed in", time.time() - start_loop_time, "seconds.")
    print("End time:", round(current_time/60,2), "hours")
    print("Total cost:", round (total_cost,2))
    print("Completed tasks:" , len(completed_tasks)/total_inital_tasks * 100, "%")

    return history
    
    
def simulate_rolling_horizon(tasks_list, strategy="EDF", tariff_model=3, horizon_minutes=120):
    current_time = 0
    completed_tasks = []
    active_tasks = []
    failed_tasks = []
    total_cost = 0
    total_initial = len(tasks_list)
    history = []
    
    while tasks_list or active_tasks:
        #Arrivée des tâches
        new_arrivals = [t for t in tasks_list if t.arrival_time == current_time]
        active_tasks.extend(new_arrivals)
        for t in new_arrivals: tasks_list.remove(t)

        # Nettoyage des échecs
        missed = [t for t in active_tasks if (current_time + t.remaining_time) > t.deadline]
        for t in missed:
            failed_tasks.append(t)
            active_tasks.remove(t)

        if active_tasks:
            # Tri selon la stratégie
            if strategy == "EDF":
                active_tasks.sort(key=lambda x: x.deadline)
            elif strategy == "LLF":
                active_tasks.sort(key=lambda x: x.get_laxity(current_time))

            current_task = active_tasks[0]
            
            
            # On regarde le prix futur dans l'horizon choisi
            current_price = get_cost_at_hour(current_time, tariff_model)
            
            # On cherche s'il y a un prix plus bas dans l'horizon
            future_prices = [get_cost_at_hour(current_time + offset, tariff_model) 
                             for offset in range(1, horizon_minutes + 1)]
            min_future_price = min(future_prices)
            
            laxity = current_task.get_laxity(current_time)

            # DÉCISION : On exécute si :
            # - On est déjà au prix minimum de l'horizon
            # - OU la laxité est nulle (Urgence absolue)
            # - OU le prix actuel est acceptable (OffPeak)
            if current_price <= min_future_price or laxity == 0 or current_price <= (1/60):
                # Exécution
                total_cost += current_price
                current_task.remaining_time -= 1
                history.append((current_time, current_task.name, current_price * 60))
                
                if current_task.remaining_time == 0:
                    active_tasks.remove(current_task)
                    completed_tasks.append(current_task)
            

        current_time += 1
        

    print("End time:", round(current_time/60,2), "hours")
    print("Total cost:", round (total_cost,2))
    print("Completed tasks:" , len(completed_tasks)/total_initial * 100, "%")

    return history

def plot_gantt(history):
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    fig, ax = plt.subplots(figsize=(10, 6))

    task_colors = {}
    color_index = 0
    colors = plt.cm.get_cmap('tab20', len(set([h[1] for h in history])))

    for time, task_name, price in history:
        if task_name not in task_colors:
            task_colors[task_name] = colors(color_index)
            color_index += 1
        ax.broken_barh([(time, 1)], (0, 5), facecolors=task_colors[task_name])

    ax.set_ylim(0, 5)
    ax.set_xlim(0, max([h[0] for h in history]) + 1)
    ax.set_xlabel('Time')
    ax.set_yticks([])
    

    # Create legend
    patches = [mpatches.Patch(color=color, label=task) for task, color in task_colors.items()]
    plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.show()



tasks_list = [
    Task("T1", arrival_time=0, execution_time=4.5, deadline=10),
    Task("T2", arrival_time=2, execution_time=3, deadline=8),
    Task("T3", arrival_time=4, execution_time=2, deadline=12),
    Task("T4", arrival_time=6, execution_time=1, deadline=9),
    Task("T5", arrival_time=8, execution_time=2.3, deadline=15),
    Task("T6", arrival_time=1, execution_time=5, deadline=14),
    Task("T7", arrival_time=3, execution_time=2.2, deadline=11),
    Task("T8", arrival_time=5, execution_time=3, deadline=13),
    Task("T9", arrival_time=7, execution_time=4.6, deadline=16)
]


l1=copy.deepcopy(tasks_list)
l2=copy.deepcopy(tasks_list)

plot_gantt(greedy(l1, strategy="EDF", tariff_model=3, cost_opt=True))
plot_gantt(simulate_rolling_horizon(l2, strategy="EDF", tariff_model=3, horizon_minutes=120))


