from .base import ExerciseState, YoloPoint, check_visibility

# Przechowuje stan i flagi błędów dla powtórzenia Pajacyków
class JumpingJacksState(ExerciseState):
    def __init__(self):
        super().__init__("jumping_jacks")
        self.arms_ok = False
        self.legs_ok = False
        self.back_ok = True

    # Zeruje flagi błędów przed rozpoczęciem powtórzenia
    def reset_rep_flags(self):
        self.arms_ok = False
        self.legs_ok = False
        self.back_ok = True

# Analizuje jakość wykonania Pajacyków przy użyciu obu kamer
def analyze_jumping_jacks(kp_front, conf_front, kp_side, conf_side, state: JumpingJacksState):
    p_front = [YoloPoint.NOSE, YoloPoint.L_SHO, YoloPoint.R_SHO, YoloPoint.L_WRI, YoloPoint.R_WRI, YoloPoint.L_ANK, YoloPoint.R_ANK]
    p_side_l = [YoloPoint.L_SHO, YoloPoint.L_HIP]
    p_side_r = [YoloPoint.R_SHO, YoloPoint.R_HIP]

    # Sprawdzenie widoczności punktów
    is_visible, use_left_profile = check_visibility(conf_front, conf_side, p_front, p_side_l, p_side_r)
    if not is_visible:
        return state, False, False, False, "BŁĄD: Sylwetka niewidoczna w obu kamerach"

    # Dynamiczne miary dystansu
    shoulder_width = abs(kp_front[YoloPoint.L_SHO][0] - kp_front[YoloPoint.R_SHO][0])
    ankle_spread = abs(kp_front[YoloPoint.L_ANK][0] - kp_front[YoloPoint.R_ANK][0])

    # Ocena faz i ułożenia ciała
    frame_arms_up = (kp_front[YoloPoint.L_WRI][1] < kp_front[YoloPoint.L_SHO][1]) and (kp_front[YoloPoint.R_WRI][1] < kp_front[YoloPoint.R_SHO][1])
    frame_arms_down = (kp_front[YoloPoint.L_WRI][1] > kp_front[YoloPoint.L_SHO][1]) and (kp_front[YoloPoint.R_WRI][1] > kp_front[YoloPoint.R_SHO][1])
    frame_arms_correct = (kp_front[YoloPoint.L_WRI][1] < kp_front[YoloPoint.NOSE][1]) and (kp_front[YoloPoint.R_WRI][1] < kp_front[YoloPoint.NOSE][1])
    frame_legs_correct = ankle_spread > (shoulder_width * 1.5)

    # Analiza pochylenia pleców (profil)
    if use_left_profile:
        s_x, s_y = kp_side[YoloPoint.L_SHO][0], kp_side[YoloPoint.L_SHO][1]
        h_x, h_y = kp_side[YoloPoint.L_HIP][0], kp_side[YoloPoint.L_HIP][1]
    else:
        s_x, s_y = kp_side[YoloPoint.R_SHO][0], kp_side[YoloPoint.R_SHO][1]
        h_x, h_y = kp_side[YoloPoint.R_HIP][0], kp_side[YoloPoint.R_HIP][1]

    torso_height = abs(s_y - h_y) if abs(s_y - h_y) > 0 else 1
    slouch_ratio = abs(s_x - h_x) / torso_height
    frame_back_correct = slouch_ratio < 0.35

    rep_completed = False
    rep_correct = False
    message = ""

    # Maszyna stanów
    if state.stage == "down":
        if frame_arms_up:
            state.stage = "up"
            state.arms_ok = frame_arms_correct
            state.legs_ok = frame_legs_correct
            state.back_ok = frame_back_correct
    elif state.stage == "up":
        # Weryfikacja momentów poprawności
        if frame_arms_correct: state.arms_ok = True
        if frame_legs_correct: state.legs_ok = True
        if not frame_back_correct: state.back_ok = False

        if not frame_arms_up:
            state.stage = "wait_for_down"
            rep_completed = True
            rep_correct = state.arms_ok and state.legs_ok and state.back_ok
            if rep_correct:
                message = "OK (Idealne powtórzenie)"
            else:
                errors = []
                if not state.arms_ok: errors.append("Ręce za nisko")
                if not state.legs_ok: errors.append("Nogi za wąsko")
                if not state.back_ok: errors.append("Zgarbione plecy")
                message = "BŁĄD: " + ", ".join(errors)
            state.reset_rep_flags()
    elif state.stage == "wait_for_down":
        if frame_arms_down:
            state.stage = "down"

    return state, rep_completed, rep_correct, True, message
