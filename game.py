# game.py
import pygame
from model import GameModel
from view import GameView
from controller import GameController


class TetrisGame:
    def __init__(self, width, height, piece_size, player_name,
                 save_manager, leaderboard, config, save_data=None):
        # Если загружаем игру, извлекаем session_id из сохранённых данных
        session_id = save_data.get("session_id") if save_data else None
        
        self.model = GameModel(width, height, piece_size, player_name, session_id=session_id)
        self.view = GameView(width, height, config)
        self.controller = GameController(self.model, self.view,
                                          save_manager, leaderboard, config,
                                          is_loaded_game=save_data is not None)
        if save_data:
            self.model.load_from_save(save_data)
            self.model.paused = True  # загруженная игра сразу на паузе

    def run(self):
        try:
            self.controller.run()
        except Exception as e:
            print(f"Ошибка в игре: {e}")
        finally:
            # Очистка и выключение игровой музыки
            self.controller.cleanup()