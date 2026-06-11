import torch

# Konfiguracja sprzętowa
# Proporcje obrazu przedniej kamery (16:9 lub 9:16)
CAMERA_1_MODE = "9:16"
# Rotacja przedniej kamery
CAMERA_1_ROTATION = True

# Proporcje obrazu bocznej kamery
CAMERA_2_MODE = "9:16"
# Rotacja bocznej kamery
CAMERA_2_ROTATION = True

# Ścieżka do modelu sieci neuronowej
MODEL_PATH = 'yolo26m-pose.pt'

# Indeksy kamer
CAMERA_1_INDEX = 1
CAMERA_2_INDEX = 3

# Wybór sprzętu do obliczeń: karta graficzna z obsługą CUDA ('cuda') lub procesor ('cpu')
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
