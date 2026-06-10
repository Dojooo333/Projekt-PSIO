# Indeksy punktów kluczowych YOLO pose
class YoloPoint:
    NOSE = 0
    L_SHO = 5  # Lewy bark
    R_SHO = 6  # Prawy bark
    L_WRI = 9  # Lewy nadgarstek
    R_WRI = 10 # Prawy nadgarstek
    L_HIP = 11 # Lewe biodro
    R_HIP = 12 # Prawe biodro
    L_KNE = 13 # Lewe kolano
    R_KNE = 14 # Prawe kolano
    L_ANK = 15 # Lewa kostka
    R_ANK = 16 # Prawa kostka

# Klasa bazowa przechowująca stan ćwiczenia
class ExerciseState:
    def __init__(self, name):
        self.exercise_name = name
        self.stage = "down"  # Aktualna faza ruchu ('down' lub 'up')

    # Metoda resetująca flagi poprawności po powtórzeniu
    def reset_rep_flags(self):
        pass

# Sprawdzenie widoczności punktów kluczowych z obu kamer
def check_visibility(conf_front, conf_side, required_front, required_side_l, required_side_r=None):
    # Weryfikacja pewności modelu (>0.5).
    visible_front = all(conf_front[idx] > 0.5 for idx in required_front)
    
    if required_side_r is not None:
        # Sprawdzenie widoczności bocznego profilu
        visible_l = all(conf_side[idx] > 0.5 for idx in required_side_l)
        visible_r = all(conf_side[idx] > 0.5 for idx in required_side_r)
        visible_side = visible_l or visible_r
        use_left_profile = visible_l
    else:
        # Wymuszenie lewego profilu przy braku prawego
        visible_side = all(conf_side[idx] > 0.5 for idx in required_side_l)
        use_left_profile = True
        
    return (visible_front and visible_side), use_left_profile
