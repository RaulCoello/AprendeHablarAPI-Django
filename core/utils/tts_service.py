import os
import wave
import shutil
import uuid
from pathlib import Path
from django.conf import settings
from piper import PiperVoice, SynthesisConfig


# pip install piper-tts
# =============================
# RUTAS
# =============================

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "piper_models/claude/es_MX-claude-high.onnx"


# =============================
# CARGAR MODELO UNA SOLA VEZ 🚀
# (MUY importante para rendimiento)
# =============================

voice = PiperVoice.load(str(MODEL_PATH))


syn_config = SynthesisConfig(
    volume=1.0,
    length_scale=1.0,
    noise_scale=0.3,
    noise_w_scale=0.5,
    normalize_audio=False,
)


# =============================
# FUNCIÓN BASE
# =============================

def text_to_wav_file(text: str, output_path: str):
    """
    Genera un wav usando Piper
    """
    with wave.open(output_path, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file, syn_config=syn_config)


# =============================
# HELPERS PARA MODELOS DJANGO
# =============================

def generate_game_tts(title,tss_dir, type ): 

    text = f"{title}"

    os.makedirs(tss_dir, exist_ok=True)# Crear la carpeta temp

    id_uuid = uuid.uuid4().hex # generar un uuid para que no se repita skere

    tmp_rel = f"{tss_dir}/{id_uuid}.wav"
    

    tmp_abs = os.path.join(settings.MEDIA_ROOT, tmp_rel)
    

    text_to_wav_file(text, tmp_abs)

    return f"tmp/tss/{type}/{id_uuid}.wav"


