from .base import ExerciseState, YoloPoint, check_visibility
from vision_utils import calculate_angle

# Przechowuje stan dla pojedynczego powtórzenia Wykroków
class LungesState(ExerciseState):
    def __init__(self):
        super().__init__("lunges")
        self.knee_angle_ok = False
        self.back_ok = True
        self.knee_front_ok = True

    # Zeruje flagi po skończonym powtórzeniu
    def reset_rep_flags(self):
        self.knee_angle_ok = False
        self.back_ok = True
        self.knee_front_ok = True

# Analizuje Wykroki z użyciem dwóch kamer symultanicznie
def analyze_lunges(kp_front, conf_front, kp_side, conf_side, state: LungesState):
    p_front = [
        YoloPoint.NOSE, YoloPoint.L_SHO, YoloPoint.R_SHO,
        YoloPoint.L_HIP, YoloPoint.R_HIP,
        YoloPoint.L_KNE, YoloPoint.R_KNE,
        YoloPoint.L_ANK, YoloPoint.R_ANK
    ]
    p_side_l = [YoloPoint.L_SHO, YoloPoint.L_HIP, YoloPoint.L_KNE, YoloPoint.L_ANK]
    p_side_r = [YoloPoint.R_SHO, YoloPoint.R_HIP, YoloPoint.R_KNE, YoloPoint.R_ANK]

    is_visible, use_left_profile = check_visibility(conf_front, conf_side, p_front, p_side_l, p_side_r)
    if not is_visible:
        return state, False, False, False, "BŁĄD: Sylwetka niewidoczna w obu kamerach"

    # Analiza z kamery bocznej (profil)
    if use_left_profile:
        s_y = kp_side[YoloPoint.L_SHO][1]
        h_x, h_y = kp_side[YoloPoint.L_HIP][0], kp_side[YoloPoint.L_HIP][1]
        k_x, k_y = kp_side[YoloPoint.L_KNE][0], kp_side[YoloPoint.L_KNE][1]
        a_x, a_y = kp_side[YoloPoint.L_ANK][0], kp_side[YoloPoint.L_ANK][1]
    else:
        s_y = kp_side[YoloPoint.R_SHO][1]
        h_x, h_y = kp_side[YoloPoint.R_HIP][0], kp_side[YoloPoint.R_HIP][1]
        k_x, k_y = kp_side[YoloPoint.R_KNE][0], kp_side[YoloPoint.R_KNE][1]
        a_x, a_y = kp_side[YoloPoint.R_ANK][0], kp_side[YoloPoint.R_ANK][1]

    # Zgięcie kolana wykrocznego (Biodro-Kolano-Kostka)
    knee_angle = calculate_angle((h_x, h_y), (k_x, k_y), (a_x, a_y))

    # Pochylenie pleców na podstawie profilu
    torso_height = abs(s_y - h_y) if abs(s_y - h_y) > 0 else 1
    s_x = kp_side[YoloPoint.L_SHO][0] if use_left_profile else kp_side[YoloPoint.R_SHO][0]
    slouch_ratio = abs(s_x - h_x) / torso_height
    frame_back_correct = slouch_ratio < 0.35

    # Faza przysiadu, gdy kąt poniżej 110 stopni
    is_down = knee_angle < 110

    # Analiza z kamery przedniej (front)
    shoulder_width = abs(kp_front[YoloPoint.L_SHO][0] - kp_front[YoloPoint.R_SHO][0])
    
    # Określenie nogi wykrocznej
    l_ank_y = kp_front[YoloPoint.L_ANK][1]
    r_ank_y = kp_front[YoloPoint.R_ANK][1]
    
    if l_ank_y > r_ank_y:
        front_kne_x = kp_front[YoloPoint.L_KNE][0]
        front_ank_x = kp_front[YoloPoint.L_ANK][0]
    else:
        front_kne_x = kp_front[YoloPoint.R_KNE][0]
        front_ank_x = kp_front[YoloPoint.R_ANK][0]
        
    center_x = (kp_front[YoloPoint.L_HIP][0] + kp_front[YoloPoint.R_HIP][0]) / 2.0
    
    dist_kne_to_center = abs(front_kne_x - center_x)
    dist_ank_to_center = abs(front_ank_x - center_x)
    
    # Detekcja koślawienia kolana
    valgus_margin = shoulder_width * 0.15
    knee_caving = dist_kne_to_center < (dist_ank_to_center - valgus_margin)
    frame_knee_straight = not knee_caving

    rep_completed = False
    rep_correct = False
    message = ""

    # Maszyna stanów
    if state.stage == "down":
        if is_down:
            state.stage = "up"
            # Akceptacja zgięcia od 70 do 120 stopni
            state.knee_angle_ok = (knee_angle > 70 and knee_angle < 120)
            state.back_ok = frame_back_correct
            state.knee_front_ok = frame_knee_straight
    elif state.stage == "up":
        # Weryfikacja błędów w trakcie powrotu
        if not frame_back_correct:
            state.back_ok = False
        if not frame_knee_straight:
            state.knee_front_ok = False

        # Zakończenie powtórzenia powyżej 160 stopni
        if not is_down and knee_angle > 160:
            state.stage = "down"
            rep_completed = True
            rep_correct = state.knee_angle_ok and state.back_ok and state.knee_front_ok
            
            if rep_correct:
                message = "OK (Idealny wykrok)"
            else:
                errors = []
                if not state.knee_angle_ok: errors.append("Zły kąt zgięcia")
                if not state.back_ok: errors.append("Zgarbione plecy")
                if not state.knee_front_ok: errors.append("Kolano schodzi do środka")
                message = "BŁĄD: " + ", ".join(errors)
            state.reset_rep_flags()

    return state, rep_completed, rep_correct, True, message
