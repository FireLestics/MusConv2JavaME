import os
import subprocess
import requests
import shutil
import time
import sys

REPO_URL = "https://github.com/FireLestics/MusConv2JavaME.git"
SCRIPT_NAME = "mus_converter.py"
UPDATE_INTERVAL_SECONDS = 60 * 60
TEMP_DIR = "temp_repo"

def convert_audio_to_low_bitrate_wav(audio_file, output_dir):
    try:
        relative_path = os.path.relpath(os.path.dirname(audio_file), "mus")
        output_subdir = os.path.join(output_dir, relative_path)
        os.makedirs(output_subdir, exist_ok=True)
        
        base_name, ext = os.path.splitext(os.path.basename(audio_file))
        output_wav = os.path.join(output_subdir, f"{base_name}.wav")

        # Команда FFmpeg с параметрами для низкого размера
        command = [
            "ffmpeg",
            "-i", audio_file,
            "-acodec", "pcm_s16le",
            "-ar", "8000",  # Очень низкая частота дискретизации
            "-ac", "1",
            "-ab", "8k",  # Низкий битрейт
            "-f", "wav",
            output_wav
        ]
        
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Конвертирован: {audio_file} -> {output_wav}")
        return True
    except FileNotFoundError:
        print("Ошибка: FFmpeg не найден. Убедитесь, что он установлен и добавлен в PATH.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при конвертации {audio_file}:\n{e.stderr}")
        return False
    except Exception as e:
        print(f"Произошла неизвестная ошибка при конвертации {audio_file}: {e}")
        return False

def process_audio_files(input_dir, output_dir):
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith((".mp3", ".wav", ".ogg", ".flac", ".m4a")):
                audio_file = os.path.join(root, file)
                if not convert_audio_to_low_bitrate_wav(audio_file, output_dir):
                    return

def check_for_updates():
   # ... (Функция check_for_updates остается без изменений из предыдущих примеров)

def update_script():
   # ... (Функция update_script остается без изменений из предыдущих примеров)


if __name__ == "__main__":
    input_directory = "mus"
    output_directory = "out"

    if not os.path.exists(input_directory):
        print(f"Ошибка: Папка '{input_directory}' не существует.")
        sys.exit(1)  # Выход с кодом ошибки

    if check_for_updates():
        print("Найдено обновление. Перезапустите скрипт для применения изменений.")
        sys.exit(0) # Возврат кода 0 означает успех

    process_audio_files(input_directory, output_directory)