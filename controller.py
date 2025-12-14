# controller.py
import pygame
from tetromino_factory import TetrominoFactory
from utils import load_music, load_sound


class GameController:
    def __init__(self, model, view, save_manager, leaderboard, config, is_loaded_game=False):
        self.model = model
        self.view = view
        self.save_manager = save_manager
        self.leaderboard = leaderboard
        self.config = config
        self.is_loaded_game = is_loaded_game  # Флаг для отслеживания, загружена ли игра

        self.running = True
        self.last_drop_time = 0
        self.last_move_time = 0
        self.soft_drop_rows = 0
        self.show_leaderboard = False
        self.added_game_over_score = False
        self.score_added_to_leaderboard = False  # Флаг для отслеживания добавления рекорда
        
        # Используем session_id из модели (который был восстановлен или сгенерирован)
        self.session_id = model.session_id
        
        # Stop menu music and load game music
        pygame.mixer.init()
        pygame.mixer.music.stop()  # Останавливаем музыку меню
        self.game_music_loaded = load_music("game_music.mp3", volume=0.7, config=config)
        
        # Load game over sound
        self.gameover_sound = load_sound("game_over.mp3", config=config)
        
        # Load sound effects
        self.drop_sound = load_sound("drop.mp3", config=config)
        self.soft_drop_sound = load_sound("drop.mp3", config=config)  # Используем тот же звук
        self.line_clear_sound = load_sound("line_clear.mp3", config=config)
        self.level_up_sound = load_sound("level_up.mp3", config=config)
        self.pause_sound = load_sound("pause.wav", config=config)

        # Загружаем контролы из конфига
        self.controls = config.get_controls()

    def handle_events(self):
        current_time = pygame.time.get_ticks()
        move_delay = 200  # 200 мс задержка между ходами

        for event in pygame.event.get():
            self.view.process_events(event)
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                if not self.model.game_over and not self.model.paused:
                    if event.key == self.controls['move_left']:
                        if current_time - self.last_move_time >= move_delay:
                            self.model.move(-1, 0)
                            self.last_move_time = current_time
                    elif event.key == self.controls['move_right']:
                        if current_time - self.last_move_time >= move_delay:
                            self.model.move(1, 0)
                            self.last_move_time = current_time
                    elif event.key == self.controls['rotate']:
                        self.model.rotate_piece()
                    elif event.key == self.controls['hard_drop']:
                        rows = self.model.hard_drop()
                        self.model.score += rows * 2
                        if self.drop_sound:
                            self.drop_sound.play()
                    elif event.key == self.controls['save_game']:
                        save_data = self.model.get_save_data()
                        if self.save_manager.save_game(save_data, self.model.player_name):
                            # Добавляем рекорд при сохранении только если это новая игра
                            if not self.is_loaded_game and not self.score_added_to_leaderboard:
                                self.leaderboard.add_score(
                                    self.model.player_name, self.model.score, self.model.level,
                                    self.model.lines_cleared, self.model.piece_size,
                                    f"{self.model.width}x{self.model.height}",
                                    session_id=self.session_id
                                )
                                self.score_added_to_leaderboard = True
                            self.view.show_save_notification()

                if event.key == self.controls['pause']:
                    self.model.paused = not self.model.paused
                    if self.pause_sound:
                        self.pause_sound.play()
                    # Пауза/включение музыки
                    if self.model.paused:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                elif event.key == self.controls['new_game']:
                    self.model.reset_game()
                    self.soft_drop_rows = 0
                    self.added_game_over_score = False
                elif event.key == self.controls['menu']:
                    # Сохраняем рекорд перед выходом
                    if self.model.score > 0 and not self.score_added_to_leaderboard:
                        self.leaderboard.add_score(
                            self.model.player_name, self.model.score, self.model.level,
                            self.model.lines_cleared, self.model.piece_size,
                            f"{self.model.width}x{self.model.height}",
                            session_id=self.session_id
                        )
                        self.score_added_to_leaderboard = True
                    return False

            elif event.type == pygame.KEYUP:
                if event.key == self.controls['soft_drop'] and self.soft_drop_rows:
                    self.model.score += self.soft_drop_rows
                    if self.soft_drop_sound:
                        self.soft_drop_sound.play()
                    self.soft_drop_rows = 0

        # Удержание клавиш
        if not self.model.game_over and not self.model.paused and not self.show_leaderboard:
            keys = pygame.key.get_pressed()
            if current_time - self.last_move_time >= move_delay:
                if keys[self.controls['move_left']]:
                    self.model.move(-1, 0)
                    self.last_move_time = current_time
                elif keys[self.controls['move_right']]:
                    self.model.move(1, 0)
                    self.last_move_time = current_time
            if keys[self.controls['soft_drop']]:
                if self.model.move(0, 1):
                    self.soft_drop_rows += 1

        return True

    def update(self):
        if self.model.game_over or self.model.paused or self.show_leaderboard:
            self.handle_game_over()
            return

        if pygame.time.get_ticks() - self.last_drop_time > self.model.speed:
            self.model.drop()
            self.last_drop_time = pygame.time.get_ticks()

        # Обновление музыки на основе скорости игры
        if self.model.lines_cleared_this_turn > 0:
            if self.line_clear_sound:
                self.line_clear_sound.play()
            self.model.lines_cleared_this_turn = 0
        
        # Проверяем рост уровня и обновляем флаг
        if self.model.level_up:
            if self.level_up_sound:
                self.level_up_sound.play()
            self.model.level_up = False

    def handle_game_over(self):
        """Обработка Game Over"""
        if self.model.game_over and not self.added_game_over_score:
            # Воспроизведение музыки конца игры
            if self.gameover_sound:
                self.gameover_sound.play()
            
            # Добавляем рекорд при Game Over только если его еще не добавили
            if not self.score_added_to_leaderboard:
                self.leaderboard.add_score(
                    self.model.player_name, self.model.score, self.model.level,
                    self.model.lines_cleared, self.model.piece_size,
                    f"{self.model.width}x{self.model.height}",
                    session_id=self.session_id
                )
                self.score_added_to_leaderboard = True
            self.added_game_over_score = True

    def render(self):
        self.view.screen.fill((30, 30, 40))
        
        # Рисуем цветное название игры
        self.view.draw_title()
        
        self.view.draw_field(self.model.field)

        ghost = self.model.get_ghost_position()
        if ghost:
            self.view.draw_ghost_piece(ghost)
        if self.model.current_piece:
            self.view.draw_piece(self.model.current_piece)

        # Обновляем информацию для панели
        self.view.current_info = {
            'player_name': self.model.player_name,
            'score': self.model.score,
            'level': self.model.level,
            'lines': self.model.lines_cleared
        }
        
        self.view.draw_right_panel(self.model.next_piece)

        if self.show_leaderboard:
            leaders = self.leaderboard.get_leaders(
                self.model.piece_size, f"{self.model.width}x{self.model.height}"
            )
            # Простая отрисовка лидерборда (можно улучшить)
            y = 100
            for i, entry in enumerate(leaders[:10]):
                text = f"{i+1}. {entry['player_name']} — {entry['score']}"
                surf = self.view.font.render(text, True, (255, 255, 255))
                self.view.screen.blit(surf, (200, y))
                y += 30

        if self.model.game_over:
            self.view.draw_game_over(self.model.player_name, self.model.score)
        elif self.model.paused:
            self.view.draw_pause()

        # Показываем уведомление о сохранении
        self.view.draw_notification()

        self.view.update_display()

    def run(self):
        self.last_drop_time = pygame.time.get_ticks()
        while self.running:
            dt = self.view.clock.tick(60) / 1000.0
            if not self.handle_events():
                break
            self.update()
            self.view.update(dt)
            self.render()
        
        # Stop game music when exiting
        pygame.mixer.music.stop()

    def cleanup(self):
        """Clean up when exiting the game"""
        pygame.mixer.music.stop()
        return True