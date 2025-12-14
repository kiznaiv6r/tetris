import pickle
import os
import datetime
from typing import List, Dict, Any, Optional
import configparser
import pygame

class SoundCache:
    """Кэш для звуков и музыки"""
    _sounds: Dict[str, Any] = {}
    _music_loaded = False
    _current_music = None  # Имя текущей загруженной музыки

class SaveManager:
    """Менеджер сохранений игр"""
    
    def __init__(self, save_dir: str = "data/saves"):
        self.save_dir = save_dir
        self.ensure_directories()
    
    def ensure_directories(self):
        """Создание необходимых директорий"""
        os.makedirs(self.save_dir, exist_ok=True)
    
    def get_save_files(self) -> List[Dict[str, Any]]:
        """Получение списка всех сохранений"""
        saves = []
        if os.path.exists(self.save_dir):
            for filename in os.listdir(self.save_dir):
                if filename.endswith('.save'):
                    filepath = os.path.join(self.save_dir, filename)
                    try:
                        with open(filepath, 'rb') as f:
                            save_data = pickle.load(f)
                            save_info = {
                                'filename': filename,
                                'player_name': save_data.get('player_name', 'Неизвестный'),
                                'score': save_data.get('score', 0),
                                'level': save_data.get('level', 1),
                                'lines': save_data.get('lines_cleared', 0),
                                'save_time': save_data.get('save_time', ''),
                                'save_date': save_data.get('save_date', ''),
                                'field_size': f"{save_data.get('width', 10)}x{save_data.get('height', 20)}",
                                'piece_size': save_data.get('piece_size', 4),
                                'field': save_data.get('field', []),  # ДОБАВЛЯЕМ ПОЛЕ ДЛЯ МИНИАТЮРЫ
                                'current_piece_type': save_data.get('current_piece_type', ''),
                                'current_piece_pos': save_data.get('current_piece_pos', (0, 0))
                            }
                            saves.append(save_info)
                    except Exception as e:
                        print(f"Ошибка загрузки сохранения {filename}: {e}")
        
        saves.sort(key=lambda x: x.get('save_time', ''), reverse=True)
        return saves
    
    def save_game(self, game_data: Dict[str, Any], player_name: str = "Игрок"):
        """Сохранение игры — удаляет старые сохранения того же игрока"""
        # Удаляем старые сохранения для этого игрока
        if os.path.exists(self.save_dir):
            for filename in os.listdir(self.save_dir):
                if filename.startswith(player_name) and filename.endswith('.save'):
                    old_filepath = os.path.join(self.save_dir, filename)
                    try:
                        os.remove(old_filepath)
                    except Exception as e:
                        print(f"Ошибка удаления старого сохранения {filename}: {e}")
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{player_name}_{timestamp}.save"
        filepath = os.path.join(self.save_dir, filename)
        
        game_data['player_name'] = player_name
        game_data['save_time'] = timestamp
        game_data['save_date'] = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(game_data, f)
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False
    
    def load_game(self, filename: str) -> Optional[Dict[str, Any]]:
        """Загрузка игры из файла"""
        filepath = os.path.join(self.save_dir, filename)
        try:
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Ошибка загрузки {filename}: {e}")
            return None
    
    def delete_save(self, filename: str) -> bool:
        """Удаление сохранения"""
        filepath = os.path.join(self.save_dir, filename)
        try:
            os.remove(filepath)
            return True
        except Exception as e:
            print(f"Ошибка удаления {filename}: {e}")
            return False
class Leaderboard:
    """Управление лидербордом"""
    
    def __init__(self, leaders_file: str = "data/leaders.dat"):
        self.leaders_file = leaders_file
        self.ensure_directories()
        # Проверяем, что файл лидерборда не повреждён
        self._validate_leaders_file()
    
    def _validate_leaders_file(self):
        """Проверка целостности файла лидерборда"""
        if os.path.exists(self.leaders_file):
            if os.path.getsize(self.leaders_file) == 0:
                # Если файл пустой, удаляем его
                try:
                    os.remove(self.leaders_file)
                except:
                    pass
            else:
                # Проверяем, можно ли загрузить файл
                try:
                    with open(self.leaders_file, 'rb') as f:
                        pickle.load(f)
                except:
                    # Если файл повреждён, удаляем его
                    try:
                        os.remove(self.leaders_file)
                    except:
                        pass
    
    def ensure_directories(self):
        """Создание необходимых директорий"""
        os.makedirs(os.path.dirname(self.leaders_file), exist_ok=True)
    
    def get_leaders(self, piece_size: int = 4, field_size: str = "10x20") -> List[Dict[str, Any]]:
        """Получение лидерборда для конкретных настроек (исключая записи со score=0 и дубли по session_id)"""
        all_leaders = self._load_all_leaders()
        key = f"{field_size}_{piece_size}"
        leaders = all_leaders.get(key, [])
        
        # Фильтруем записи со score=0 и оставляем только последнюю запись для каждого session_id
        seen_sessions = {}
        filtered = []
        
        for entry in leaders:
            score = entry.get('score', 0)
            session_id = entry.get('session_id')
            
            # Пропускаем записи со score=0
            if score <= 0:
                continue
            
            # Если есть session_id, оставляем только последнюю запись для этой сессии
            if session_id:
                if session_id not in seen_sessions:
                    seen_sessions[session_id] = entry
                    filtered.append(entry)
                else:
                    # Заменяем старую запись на новую (более свежую)
                    if score > seen_sessions[session_id].get('score', 0):
                        filtered.remove(seen_sessions[session_id])
                        seen_sessions[session_id] = entry
                        filtered.append(entry)
            else:
                # Для записей без session_id просто добавляем
                filtered.append(entry)
        
        return filtered
    
    def add_score(self, player_name: str, score: int, level: int, lines: int, 
              piece_size: int = 4, field_size: str = "10x20", session_id: str = None):
        """Добавление или обновление результата в лидерборд"""
        if not player_name.strip():
            player_name = "Игрок"
        
        all_leaders = self._load_all_leaders()
        key = f"{field_size}_{piece_size}"
        
        if key not in all_leaders:
            all_leaders[key] = []
        
        new_entry = {
            'player_name': player_name,
            'score': score,
            'level': level,
            'lines': lines,
            'date': datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
            'session_id': session_id
        }
        
        # Если есть session_id, ищем существующий рекорд для этой сессии
        if session_id:
            for i, entry in enumerate(all_leaders[key]):
                if entry.get('session_id') == session_id:
                    # Обновляем только если новый рекорд выше старого
                    if score > entry.get('score', 0):
                        all_leaders[key][i] = new_entry
                    # Сортируем и сохраняем
                    all_leaders[key].sort(key=lambda x: x['score'], reverse=True)
                    all_leaders[key] = all_leaders[key][:10]  # Только топ-10
                    self._save_all_leaders(all_leaders)
                    return
        
        # Если рекорда для этой сессии нет, добавляем новый
        all_leaders[key].append(new_entry)
        all_leaders[key].sort(key=lambda x: x['score'], reverse=True)
        all_leaders[key] = all_leaders[key][:10]  # Только топ-10
        
        self._save_all_leaders(all_leaders)  # Не забываем сохранить!
    
    def _load_all_leaders(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Восстановление старой версии загрузки лидерборда с поддержкой pickle.
        """
        if not os.path.exists(self.leaders_file):
            return {}
        
        # Проверяем, что файл не пустой
        if os.path.getsize(self.leaders_file) == 0:
            return {}

        try:
            with open(self.leaders_file, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Ошибка загрузки лидерборда: {e}")
            return {}

    def _save_all_leaders(self, leaders: Dict[str, List[Dict[str, Any]]]):
        """
        Восстановление старой версии сохранения лидерборда с использованием pickle.
        """
        try:
            with open(self.leaders_file, 'wb') as f:
                pickle.dump(leaders, f)
        except Exception as e:
            print(f"Ошибка сохранения лидерборда: {e}")

class ConfigManager:
    """Управление конфигурацией"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self):
        """Загрузка конфигурации"""
        config = configparser.ConfigParser()
        
        if os.path.exists(self.config_file):
            config.read(self.config_file)
        else:
            self._create_default_config(config)
        
        return config
    
    def _create_default_config(self, config):
        """Создание конфигурации по умолчанию"""
        config['Game'] = {
            'field_width': '10',
            'field_height': '20',
            'piece_size': '4',
            'initial_speed': '500',
            'speed_increase': '50'
        }
        config['Controls'] = {
            'move_left': 'left',
            'move_right': 'right',
            'rotate': 'up',
            'soft_drop': 'down',
            'hard_drop': 'space',
            'pause': 'p',
            'new_game': 'n',
            'save_game': 's',
            'menu': 'escape'
        }
        config['Graphics'] = {
            'cell_size': '30',
            'show_grid': 'true',
            'show_ghost': 'true'
        }
        config['Sound'] = {
            'music_volume': '0.7',
            'sound_volume': '1.0',
            'enable_music': 'true',
            'enable_sound': 'true'
        }
        self.save_config(config)
    
    def save_config(self, config=None):
        """Сохранение конфигурации"""
        if config is None:
            config = self.config
        with open(self.config_file, 'w') as f:
            config.write(f)
    
    def get(self, section, key, default=None, type_func=str):
        """Получение значения конфигурации"""
        try:
            value = self.config[section][key]
            return type_func(value)
        except (KeyError, ValueError):
            return default
    
    def get_key_code(self, key_name: str) -> int:
        """Преобразование названия клавиши в pygame код"""
        key_map = {
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT,
            'up': pygame.K_UP,
            'down': pygame.K_DOWN,
            'space': pygame.K_SPACE,
            'a': pygame.K_a,
            'b': pygame.K_b,
            'c': pygame.K_c,
            'd': pygame.K_d,
            'e': pygame.K_e,
            'f': pygame.K_f,
            'g': pygame.K_g,
            'h': pygame.K_h,
            'i': pygame.K_i,
            'j': pygame.K_j,
            'k': pygame.K_k,
            'l': pygame.K_l,
            'm': pygame.K_m,
            'n': pygame.K_n,
            'o': pygame.K_o,
            'p': pygame.K_p,
            'q': pygame.K_q,
            'r': pygame.K_r,
            's': pygame.K_s,
            't': pygame.K_t,
            'u': pygame.K_u,
            'v': pygame.K_v,
            'w': pygame.K_w,
            'x': pygame.K_x,
            'y': pygame.K_y,
            'z': pygame.K_z,
            'escape': pygame.K_ESCAPE,
            'enter': pygame.K_RETURN,
            'tab': pygame.K_TAB,
            'shift': pygame.K_LSHIFT,
            'ctrl': pygame.K_LCTRL,
            'alt': pygame.K_LALT
        }
        return key_map.get(key_name.lower(), pygame.K_LEFT)
    
    def get_controls(self) -> dict:
        """Получение всех контролов из конфига"""
        controls = {}
        try:
            for key in self.config['Controls']:
                key_name = self.config['Controls'][key]
                controls[key] = self.get_key_code(key_name)
        except KeyError:
            # Если раздел Controls не найден, используем стандартные
            controls = {
                'move_left': pygame.K_LEFT,
                'move_right': pygame.K_RIGHT,
                'rotate': pygame.K_UP,
                'soft_drop': pygame.K_DOWN,
                'hard_drop': pygame.K_SPACE,
                'pause': pygame.K_p,
                'new_game': pygame.K_n,
                'save_game': pygame.K_s,
                'menu': pygame.K_ESCAPE
            }
        return controls


def load_logo(max_width: int = 250) -> Optional[Any]:
    """
    Загружает логотип тетриса из ресурсов.
    
    Args:
        max_width: Максимальная ширина логотипа после масштабирования
    
    Returns:
        pygame.Surface объект логотипа или None если не найден
    """
    import pygame
    
    logo = None
    try:
        logo_path = os.path.join(os.path.dirname(__file__), "resources", "tetris_logo.png")
        if os.path.exists(logo_path):
            logo = pygame.image.load(logo_path)
            # Масштабирование с сохранением пропорций (оригинал: 320x222)
            original_width = logo.get_width()
            original_height = logo.get_height()
            aspect_ratio = original_height / original_width
            new_height = int(max_width * aspect_ratio)
            logo = pygame.transform.scale(logo, (max_width, new_height))
            print(f"Logo loaded from: {logo_path}")
        else:
            print(f"Logo not found at: {logo_path}")
    except Exception as e:
        print(f"Could not load logo: {e}")
    
    return logo


def load_music(music_filename: str, volume: float = 0.6, config: 'ConfigManager' = None) -> bool:
    """
    Загружает и воспроизводит музыку из ресурсов.
    
    Args:
        music_filename: Имя файла музыки (например, "menu_music.mp3")
        volume: Громкость (0.0 - 1.0)
        config: ConfigManager для проверки enable_music
    
    Returns:
        True если музыка загружена успешно
    """
    import pygame
    
    # Проверяем, включена ли музыка в конфиге
    if config:
        enable_music = config.get('Sound', 'enable_music', 'true', lambda x: x.lower() == 'true')
        if not enable_music:
            return False
    
    # Если эта же музыка уже загружена, просто воспроизводим
    if SoundCache._current_music == music_filename and SoundCache._music_loaded:
        try:
            pygame.mixer.music.play(-1)
        except:
            pass
        return True
    
    try:
        music_path = os.path.join(os.path.dirname(__file__), "resources", music_filename)
        if os.path.exists(music_path):
            pygame.mixer.music.load(music_path)
            music_volume = config.get('Sound', 'music_volume', volume, float) if config else volume
            pygame.mixer.music.set_volume(music_volume)
            pygame.mixer.music.play(-1)  # -1 = infinite loop
            SoundCache._music_loaded = True
            SoundCache._current_music = music_filename  # Запоминаем, какая музыка загружена
            print(f"Music '{music_filename}' loaded from: {music_path}")
            return True
        else:
            print(f"Music not found at: {music_path}")
            return False
    except Exception as e:
        print(f"Could not load music '{music_filename}': {e}")
        return False


def load_sound(sound_filename: str, config: 'ConfigManager' = None) -> Optional[Any]:
    """
    Загружает звуковой эффект из ресурсов с кэшированием.
    
    Args:
        sound_filename: Имя файла звука (например, "gameover.wav")
        config: ConfigManager для проверки enable_sound
    
    Returns:
        pygame.mixer.Sound объект или None если не найден
    """
    import pygame
    
    # Проверяем, включены ли звуки в конфиге
    if config:
        enable_sound = config.get('Sound', 'enable_sound', 'true', lambda x: x.lower() == 'true')
        if not enable_sound:
            return None
    
    # Проверяем, есть ли звук в кэше
    if sound_filename in SoundCache._sounds:
        return SoundCache._sounds[sound_filename]
    
    sound = None
    try:
        sound_path = os.path.join(os.path.dirname(__file__), "resources", sound_filename)
        if os.path.exists(sound_path):
            sound = pygame.mixer.Sound(sound_path)
            sound_volume = config.get('Sound', 'sound_volume', 1.0, float) if config else 1.0
            sound.set_volume(sound_volume)
            SoundCache._sounds[sound_filename] = sound  # Кэшируем звук
            # Выводим сообщение только при первой загрузке
            print(f"Sound '{sound_filename}' loaded from: {sound_path}")
        else:
            print(f"Sound not found at: {sound_path}")
    except Exception as e:
        print(f"Could not load sound '{sound_filename}': {e}")
    
    return sound