from .base import ExerciseState, YoloPoint, check_visibility

# Przechowuje stan dla ćwiczenia Skip A
class SkipAState(ExerciseState):
    def __init__(self):
        super().__init__("high_knees")
        self.knee_high_ok = False
        self.back_ok = True
        self.knee_flare = False

    # Zeruje flagi po skończonym powtórzeniu
    def reset_rep_flags(self):
        self.knee_high_ok = False
        self.back_ok = True
        self.knee_flare = False

# Analizuje powtórzenie w Skipie A (uniesienie kolana)
def analyze_skip_a(kp_front, conf_front, kp_side, conf_side, state: SkipAState):
    p_front = [YoloPoint.L_HIP, YoloPoint.R_HIP, YoloPoint.L_KNE, YoloPoint.R_KNE, YoloPoint.L_SHO, YoloPoint.R_SHO]
    p_side_l = [YoloPoint.L_SHO, YoloPoint.L_HIP]
    p_side_r = [YoloPoint.R_SHO, YoloPoint.R_HIP]

    is_visible, use_left_profile = check_visibility(conf_front, conf_side, p_front, p_side_l, p_side_r)
    if not is_visible:
        return state, False, False, False, "BŁĄD: Sylwetka niewidoczna w obu kamerach"

    h_l_y = kp_front[YoloPoint.L_HIP][1]
    h_r_y = kp_front[YoloPoint.R_HIP][1]
    k_l_y = kp_front[YoloPoint.L_KNE][1]
    k_r_y = kp_front[YoloPoint.R_KNE][1]

    shoulder_width = abs(kp_front[YoloPoint.L_SHO][0] - kp_front[YoloPoint.R_SHO][0])
    # Obliczenie proporcji i referencji z profilu
    if use_left_profile:
        s_x, s_y = kp_side[YoloPoint.L_SHO][0], kp_side[YoloPoint.L_SHO][1]
        h_x_side, h_y_side = kp_side[YoloPoint.L_HIP][0], kp_side[YoloPoint.L_HIP][1]
    else:
        s_x, s_y = kp_side[YoloPoint.R_SHO][0], kp_side[YoloPoint.R_SHO][1]
        h_x_side, h_y_side = kp_side[YoloPoint.R_HIP][0], kp_side[YoloPoint.R_HIP][1]

    torso_height = abs(s_y - h_y_side) if abs(s_y - h_y_side) > 0 else 1

    # Zaczynamy liczyć powtórzenie, gdy noga przekroczy ten próg
    lift_threshold = torso_height * 0.4
    
    # Używamy kamery BOCZNEJ do pomiaru wysokości, bo nie ulega skrótom perspektywicznym (foreshortening)
    k_side_y = min(kp_side[YoloPoint.L_KNE][1], kp_side[YoloPoint.R_KNE][1])
    is_lifted = k_side_y < h_y_side + lift_threshold
    
    # Powtórzenie kończy się, gdy kolano z profilu opadnie poniżej tego progu
    drop_threshold = torso_height * 0.6
    is_dropped = k_side_y > h_y_side + drop_threshold

    # Właściwa wysokość kolana (złagodzony próg do 0.25, by nie omijać szybkich klatek biegu)
    high_threshold = torso_height * 0.25
    is_high = k_side_y < h_y_side + high_threshold

    # Pochylenie pleców (złagodzony próg do 0.35)
    slouch_ratio = abs(s_x - h_x_side) / torso_height
    frame_back_correct = slouch_ratio < 0.35

    rep_completed = False
    rep_correct = False
    message = ""

    # Maszyna stanów wertykalnych dla nogi
    if state.stage == "down":
        if is_lifted:
            state.stage = "up"
            # Identyfikacja nogi za pomocą przedniej kamery (która kostka jest wyżej/bardziej oderwana od ziemi)
            a_l_y = kp_front[YoloPoint.L_ANK][1]
            a_r_y = kp_front[YoloPoint.R_ANK][1]
            
            # RATUNEK NA BLUR/MOTION: Jeśli model YOLO z przodu zgubi jedną stopę w szybkim ruchu i "zleje" obie na nodze stojącej, 
            # ich różnica Y będzie bardzo mała. Wtedy ufamy w naprzemienność, by nie spamować "zmieniaj nogi".
            if abs(a_l_y - a_r_y) < torso_height * 0.15:
                current_leg = "right" if getattr(state, 'last_leg', 'left') == "left" else "left"
            else:
                current_leg = "left" if a_l_y < a_r_y else "right"
            
            if hasattr(state, 'last_leg') and state.last_leg == current_leg:
                state.wrong_leg = True
            else:
                state.wrong_leg = False
                
            state.last_leg = current_leg
            state.knee_high_ok = False
            state.back_ok = frame_back_correct
            state.knee_flare = False
    elif state.stage == "up":
        if not frame_back_correct:
            state.back_ok = False
            
        # Analiza uciekających kolan z kamery frontowej
        if hasattr(state, 'last_leg'):
            if state.last_leg == "left":
                k_x = kp_front[YoloPoint.L_KNE][0]
                h_x = kp_front[YoloPoint.L_HIP][0]
            else:
                k_x = kp_front[YoloPoint.R_KNE][0]
                h_x = kp_front[YoloPoint.R_HIP][0]
                
            if abs(k_x - h_x) > shoulder_width * 0.5:
                state.knee_flare = True

        if is_high:
            state.knee_high_ok = True
            
        # Zakończenie powtórzenia, gdy wyższe kolano na kamerze bocznej opadnie
        # WERYFIKACJA: Jeśli boczna kamera zgubi kolano przez okluzję w kącie 90 stopni, sprawdzamy kostki z przodu.
        # Jeśli różnica w wysokości kostek jest nadal duża, noga wciąż jest w górze (fałszywy drop).
        a_l_y = kp_front[YoloPoint.L_ANK][1]
        a_r_y = kp_front[YoloPoint.R_ANK][1]
        ankle_diff = abs(a_l_y - a_r_y)
        
        # W momencie pełnego biegu/zmiany nóg, kostki mijają się w połowie wysokości, więc ankle_diff jest małe.
        is_actually_dropped = is_dropped and (ankle_diff < torso_height * 0.4)

        if is_actually_dropped:
            state.stage = "down"
            rep_completed = True
            
            wrong_leg = getattr(state, 'wrong_leg', False)
            rep_correct = state.knee_high_ok and state.back_ok and not wrong_leg and not state.knee_flare
            
            if rep_correct:
                message = "OK (Dobre tempo i wysokość)"
            else:
                errors = []
                if wrong_leg: errors.append("Zmieniaj nogi")
                if not state.knee_high_ok: errors.append("Kolana za nisko")
                if not state.back_ok: errors.append("Zgarbione plecy")
                if state.knee_flare: errors.append("Kolana uciekają na zewnątrz")
                message = "BŁĄD: " + ", ".join(errors)
            state.reset_rep_flags()

    return state, rep_completed, rep_correct, True, message
