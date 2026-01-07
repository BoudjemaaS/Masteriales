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
    

   