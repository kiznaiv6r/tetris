# view.py
import pygame
import pygame_gui
from typing import Optional
from tetromino_factory import Tetromino
from utils import load_logo


class GameView:
    def __init__(self, width: int, height: int, config):
        pygame.init()
        self.width = width
        self.height = height
        self.config = config

        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Тетрис")
        self.screen_width = 800
        self.screen_height = 600
        self.clock = pygame.time.Clock()

        self.ui_manager = pygame_gui.UIManager((800, 600))
        self.font_big = pygame.font.Font(None, 42)
        self.font = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 22)

        # Ключевой фикс: поле всегда помещается
        # Ограничение размера клетки для предотвращения выхода за границы экрана
        max_cell_size = min(500 // width, (self.screen_height - 20) // height)
        self.cell_size = max(18, min(28, max_cell_size))

        self.field_offset_x = 40
        self.field_offset_y = 20

        self.save_notification_time = 0
        
        # Инициализация информации для панели
        self.current_info = {
            'player_name': '',
            'score': 0,
            'level': 1,
            'lines': 0
        }
        
        # Load logo once
        self.logo = load_logo(max_width=250)

    def show_save_notification(self):
        self.save_notification_time = pygame.time.get_ticks()

    def draw_notification(self):
        if pygame.time.get_ticks() - self.save_notification_time < 2000:
            text = self.font_big.render("Игра сохранена!", True, (0, 255, 100))
            bg = pygame.Surface((text.get_width() + 40, 60))
            bg.fill((0, 0, 0))
            bg.blit(text, (20, 10))
            self.screen.blit(bg, (400 - bg.get_width() // 2, 20))

    def draw_cell(self, x: int, y: int, color):
        rect = pygame.Rect(
            self.field_offset_x + x * self.cell_size,
            self.field_offset_y + y * self.cell_size,
            self.cell_size - 1, self.cell_size - 1
        )
        pygame.draw.rect(self.screen, color, rect)

    def draw_field(self, field):
        self.screen.fill((20, 20, 40))
        pygame.draw.rect(self.screen, (100, 100, 100),
                         (self.field_offset_x - 2, self.field_offset_y - 2,
                          self.width * self.cell_size + 4, self.height * self.cell_size + 4), 3)

        for y, row in enumerate(field):
            for x, cell in enumerate(row):
                if cell:
                    self.draw_cell(x, y, cell)
                else:
                    pygame.draw.rect(self.screen, (45, 45, 60),
                                     (self.field_offset_x + x * self.cell_size,
                                      self.field_offset_y + y * self.cell_size,
                                      self.cell_size - 1, self.cell_size - 1), 1)

    def draw_piece(self, piece: Optional[Tetromino], alpha=255):
        if not piece: return
        for i, row in enumerate(piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    color = piece.color if alpha == 255 else (*piece.color, alpha)
                    rect = pygame.Rect(
                        self.field_offset_x + (piece.x + j) * self.cell_size,
                        self.field_offset_y + (piece.y + i) * self.cell_size,
                        self.cell_size - 1, self.cell_size - 1
                    )
                    s = pygame.Surface(rect.size, pygame.SRCALPHA)
                    s.fill(color)
                    self.screen.blit(s, rect.topleft)

    def draw_ghost_piece(self, ghost):
        if ghost:
            self.draw_piece(ghost, alpha=80)

    def draw_right_panel(self, piece: Optional[Tetromino]):
        """Renders the right panel with player info and next piece."""
        x = self.field_offset_x + self.width * self.cell_size + 40
        y = 20
        
        # Larger font for panel
        font_large = pygame.font.Font(None, 32)
        font_medium = pygame.font.Font(None, 28)

        # Player name
        surf = font_large.render(f"Игрок: {self.current_info['player_name']}", True, (200, 200, 200))
        self.screen.blit(surf, (x, y))
        y += 40
        
        # Score - highlighted in yellow
        score_text = f"Счёт: {self.current_info['score']}"
        surf = font_large.render(score_text, True, (255, 255, 100))
        self.screen.blit(surf, (x, y))
        y += 40
        
        # Level - highlighted in cyan
        level_text = f"Уровень: {self.current_info['level']}"
        surf = font_large.render(level_text, True, (100, 255, 255))
        self.screen.blit(surf, (x, y))
        y += 40
        
        # Lines - normal color
        lines_text = f"Линии: {self.current_info['lines']}"
        surf = font_medium.render(lines_text, True, (200, 200, 200))
        self.screen.blit(surf, (x, y))
        y += 35

        # Controls
        y += 10
        self.screen.blit(font_medium.render("УПРАВЛЕНИЕ:", True, (255, 200, 0)), (x, y))
        y += 30
        controls = [
            "влево: сдвиг влево",
            "вправо: сдвиг вправо",
            "вверх: Rotate",
            "вниз: медленное опускание",
            "Space: мгновенное опускание",
            "P: Пауза",
            "S: Соханить игру",
            "N: Новая игра",
            "ESC: Выйти в меню"
        ]
        for c in controls:
            surf = self.font_small.render(c, True, (180, 180, 180))
            self.screen.blit(surf, (x, y))
            y += 22

        # Next piece
        y += 20
        next_title = font_medium.render("СЛЕДУЮЩАЯ:", True, (255, 200, 0))
        self.screen.blit(next_title, (x, y))
        y += 30

        if piece:
            size = piece.get_width()
            cell = 20
            offset_x = x + (120 - size * cell) // 2
            for i in range(size):
                for j in range(size):
                    if piece.shape[i][j]:
                        pygame.draw.rect(
                            self.screen, piece.color,
                            (offset_x + j * cell, y + i * cell, cell - 1, cell - 1)
                        )

    def draw_game_over(self, player_name, score):
        overlay = pygame.Surface((800, 600))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        lines = ["ИГРА ОКОНЧЕНА", f"{player_name}: {score} очков",
                 "N — новая игра", "ESC — в меню"]
        y = 200
        for line in lines:
            color = (255, 50, 50) if "ОКОНЧЕНА" in line else (255, 255, 255)
            surf = self.font_big.render(line, True, color)
            self.screen.blit(surf, (400 - surf.get_width() // 2, y))
            y += 55

    def draw_pause(self):
        overlay = pygame.Surface((800, 600))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        pause = self.font_big.render("ПАУЗА", True, (255, 255, 0))
        cont = self.font.render("Нажмите P для продолжения", True, (255, 255, 255))
        self.screen.blit(pause, (400 - pause.get_width() // 2, 250))
        self.screen.blit(cont, (400 - cont.get_width() // 2, 310))

    def update(self, time_delta):
        self.ui_manager.update(time_delta)

    def update_display(self):
        """
        Обновление экрана - просто отображаем UI
        """
        self.ui_manager.draw_ui(self.screen)
        pygame.display.flip()

    def process_events(self, event):
        self.ui_manager.process_events(event)

    def draw_title(self):
        """Renders the Tetris logo instead of the text title."""
        if self.logo:
            x = (800 - self.logo.get_width()) // 2
            y = 50
            self.screen.blit(self.logo, (x, y))
        else:
            # Fallback to text if logo is not available
            title_font = pygame.font.Font(None, 100)
            text = "ТЕТРИС"
            text_surface = title_font.render(text, True, (255, 255, 0))
            self.screen.blit(text_surface, (400 - text_surface.get_width() // 2, 50))