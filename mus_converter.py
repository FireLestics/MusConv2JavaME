import os
import subprocess
import requests
import shutil
import time
import sys
from pathlib import Path
import configparser

REPO_URL = "https://raw.githubusercontent.com/FireLestics/MusConv2JavaME/main"
VERSION_FILE = "version.ini"
TEMP_DIR = "temp_repo"
SUPPORTED_EXTENSIONS = (".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac")

def get_remote_version():
    url = f"{REPO_URL}/{VERSION_FILE}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка кода ответа (200 OK)
        config = configparser.ConfigParser()
        config.read_string(response.text)
        return config.get("version", "number")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении версии с GitHub: {e}")
        return None
    except (configparser.Error, KeyError) as e:
        print(f"Ошибка при парсинге файла version.ini: {e}")
        return None


def get_local_version():
    config = configparser.ConfigParser()
    version_file_path = Path(VERSION_FILE)
    if not version_file_path.exists():
      print("Файл version.ini не найден локально. Создаю новый файл...")
      config['version'] = {'number': '0.0.0'}
      with open(VERSION_FILE, 'w') as f:
          config.write(f)
      return '0.0.0'
    try:
        config.read(VERSION_FILE)
        return config.get("version", "number")
    except (configparser.Error, KeyError) as e:
        print(f"Ошибка при парсинге файла version.ini: {e}")
        return None



def convert_audio(input_file, output_file):
    try:
        command = [
            "ffmpeg",
            "-i", input_file,
            "-acodec", "pcm_s16le",
            "-ar", "8000",
            "-ac", "1",
            "-ab", "8k",
            "-f", "wav",
            output_file,
        ]
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Конвертирован: {input_file} -> {output_file}")
        return True
    except FileNotFoundError:
        print("Ошибка: FFmpeg не найден. Убедитесь, что он установлен и добавлен в PATH.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Ошибка FFmpeg при конвертации {input_file}:\n{e.stderr}")
        return False
    except Exception as e:
        print(f"Произошла неизвестная ошибка при конвертации {input_file}: {e}")
        return False

def process_audio_files(input_dir, output_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    for file_path in input_dir.rglob("*"):
        if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            relative_path = file_path.relative_to(input_dir)
            output_file = output_dir / relative_path.with_suffix(".wav")
            output_file.parent.mkdir(parents=True, exist_ok=True)
            if not convert_audio(str(file_path), str(output_file)):
                return False
    return True


def update_script():
    try:
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
        subprocess.run(["git", "clone", "https://github.com/FireLestics/MusConv2JavaME.git", TEMP_DIR], check=True, capture_output=True, text=True)
        shutil.copy(TEMP_DIR / SCRIPT_NAME, ".")
        shutil.rmtree(TEMP_DIR)
        print("Скрипт успешно обновлён!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ошибка обновления скрипта: {e.stderr}")
        return False
    except Exception as e:
        print(f"Произошла неизвестная ошибка при обновлении скрипта: {e}")
        return False

if __name__ == "__main__":
    input_dir = "mus"
    output_dir = "out"

    if not Path(input_dir).exists():
        print(f"Ошибка: Папка '{input_dir}' не существует.")
        sys.exit(1)

    remote_version = get_remote_version()
    local_version = get_local_version()

    if remote_version and local_version and remote_version != local_version:
      if update_script():
        print("Обновление успешно установлено. Перезапустите скрипт.")
      else:
        print("Ошибка обновления!")
      sys.exit(0)

    if not process_audio_files(input_dir, output_dir):
        sys.exit(1)
