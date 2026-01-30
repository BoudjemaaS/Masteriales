
import copy
import time

from matplotlib import ticker
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

tariff_model = 3  # Modèle tarifaire par défaut

class Task:
    def __init__(self, name, arrival_time, execution_time, deadline):
        self.name = name # Nom de la tâche
        self.arrival_time = round(arrival_time * 60) # Date d'arrivée de la tâche
        self.execution_time = round(execution_time * 60)  # Temps d'exécution total de la tâche
        self.remaining_time = round(execution_time * 60) # Temps d'exécution restant
        self.deadline = round(deadline * 60) # Échéance de la tâche

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


def plot_gantt(history, ax=None):
    

    if ax is None:
        fig, ax = plt.subplots(figsize=(24, 6))
        show_plot = True
    else:
        show_plot = False

    task_colors = {}
    color_index = 0
    colors = plt.get_cmap('tab20', len(set([h[1] for h in history])))

    for time, task_name, price in history:
        if task_name not in task_colors:
            task_colors[task_name] = colors(color_index)
            color_index += 1
        ax.broken_barh([(time, 1)], (0, price), facecolors=task_colors[task_name])

    ax.set_ylim(0, max([h[2] for h in history]) + 1)
    ax.set_xlim(0, max([h[0] for h in history]) + 1)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(60))
    formatter = ticker.FuncFormatter(lambda x, pos: f'{int(x/60)}')
    ax.xaxis.set_major_formatter(formatter)
    ax.set_xlabel('Time')
    ax.set_yticks([])
    

    # Create legend
    patches = [mpatches.Patch(color=color, label=task) for task, color in task_colors.items()]
    plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc='upper left')

    if show_plot:
        plt.tight_layout()
        plt.show()

def plot_cost_profile(tariff_model, max_hours=24, ax=None):
    """
    Affiche la courbe des coûts.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(24, 4))
        show_plot = True
    else:
        show_plot = False

    # Génération des données minute par minute
    minutes = list(range(0, max_hours * 60))
    costs = [get_cost_at_hour(m, tariff_model) * 60 for m in minutes]
    
    ax.plot(minutes, costs, drawstyle='steps-post', color='tab:red', linewidth=2, label=f'Tariff Model {tariff_model}')
    
    ax.set_ylim(0, 4)
    ax.set_yticks([1, 2, 3])
    ax.set_yticklabels(["Off (1)", "Mid (2)", "Peak (3)"])
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc='upper right') # Utiliser ax.legend
    

    if show_plot:
        # Si on affiche seul, on formate l'axe X ici
        ax.xaxis.set_major_locator(ticker.MultipleLocator(60))
        formatter = ticker.FuncFormatter(lambda x, pos: f'{int(x/60)}h')
        ax.xaxis.set_major_formatter(formatter)
        plt.show()


def online_full_tasks():
    
    current_time = 0 #Début de la simulation
    completed_tasks = [] #Liste des tâches complétées
    active_tasks = [] #Liste des tâches actives
    failed_tasks = [] #Liste des tâches échouées
    total_cost = 0 #Coût total de l'ordonnancement 
    total_inital_tasks = len(tasks_list) #Nombre total de tâches initiales
    history = [] #Historique des taches pour le diagramme de Gantt
    start_loop_time = time.time()
    new_arrivals = [t for t in tasks_list if t.arrival_time <= current_time] #Tâches arrivant à l'instant t

    while tasks_list or active_tasks:
        #Ajout des tâches qui viennent d'arriver
        active_tasks.extend(new_arrivals)
        for t in new_arrivals: tasks_list.remove(t)

        # Si (Temps actuel + Temps restant > Deadline), la tâche est condamnée et supprimée
        missed = [t for t in active_tasks[:] if (current_time + t.remaining_time) > t.deadline]
        for t in missed:
            failed_tasks.append(t)
            active_tasks.remove(t)

        

        if active_tasks:
            active_tasks.sort(key=lambda x: x.deadline)
            current_task = active_tasks[0]
           
            

            while current_task.remaining_time > 0:
                
                delay = False


                new_arrivals = [t for t in tasks_list if t.arrival_time <= current_time] #Tâches arrivant à l'instant t
                active_tasks.extend(new_arrivals)
                active_tasks.sort(key=lambda x: x.deadline)
                for t in new_arrivals:
                    tasks_list.remove(t)

                if len(new_arrivals) > 1:
                   
                    new_arrivals.sort(key=lambda x: x.deadline)
                    if active_tasks[0].execution_time+active_tasks[1].execution_time <= current_task.remaining_time:
                        current_task.execution_time= current_task.remaining_time
                        #print(current_task.remaining_time,current_task.execution_time)
                        new_arrivals.append(current_task)
                        current_task = active_tasks[0]


                window = [get_cost_at_hour(h, tariff_model) for h in range(current_time, current_task.deadline)]
                #print("window",window)

                min_cost = min ([get_cost_at_hour(h, tariff_model) for h in range(current_time, current_task.deadline)])
                #print("cost",get_cost_at_hour(current_time, tariff_model), min_cost)
                if get_cost_at_hour(current_time, tariff_model) > min_cost and current_task.get_laxity(current_time) > 0:
                    #si on peut retarder la tâche actuelle pour une tâche moins coûteuse
                    #print("delay")
                    delay = True
                    active_tasks.sort(key=lambda x: x.deadline)
                    current_task=active_tasks[0]
                    #print("current task", current_task.name)
                    
                if not delay:
                    total_cost += get_cost_at_hour(current_time, tariff_model)
                    history.append((current_time, current_task.name, get_cost_at_hour(current_time, tariff_model)*60))
                    current_task.remaining_time -= 1
                    current_time += 1

                else:
                    current_time += 1

            if current_task.remaining_time == 0:
                active_tasks.remove(current_task)
                completed_tasks.append(current_task)

        else:
            current_time +=1 
               
    print("Simulation completed in", time.time() - start_loop_time, "seconds.")
    print("End time:", round(current_time/60,2), "hours")
    print("Total cost:", round (total_cost,2))
    print("Completed tasks:" , len(completed_tasks)/total_inital_tasks * 100, "%")
    print("completed tasks:", [t.name for t in completed_tasks])
    print("Failed tasks:", [t.name for t in failed_tasks])

    return history




tasks_list = [
    Task("T1", arrival_time=0, execution_time=2, deadline=10),
    Task("T10"  , arrival_time=0.5, execution_time=1, deadline=7),
    Task("T11"  , arrival_time=0.5, execution_time=1, deadline=9),
    Task("T7", arrival_time=3.5, execution_time=2, deadline=11),
    Task("T2", arrival_time=2, execution_time=3, deadline=8),
    Task("T9", arrival_time=7, execution_time=4, deadline=25),
    Task("T4", arrival_time=6, execution_time=1, deadline=9),
    Task("T14", arrival_time=3.5, execution_time=2, deadline=11),
    Task("T3", arrival_time=4, execution_time=2, deadline=12),
    Task("T5", arrival_time=8, execution_time=2, deadline=12),
    Task("T6", arrival_time=1, execution_time=5, deadline=14),
    Task("T8", arrival_time=5, execution_time=2, deadline=13)
]


l1=copy.deepcopy(tasks_list)
l2=copy.deepcopy(tasks_list)

history = online_full_tasks()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 8), sharex=True, gridspec_kw={'height_ratios': [1, 3]})
plt.subplots_adjust(hspace=0.1)

plot_cost_profile(tariff_model=tariff_model, max_hours=24, ax=ax1) # Dessine en haut
plot_gantt(history, ax=ax2)
plt.show()
