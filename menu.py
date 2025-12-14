import pygame
import pygame_gui
import sys
from utils import load_logo, load_music, load_sound

class Menu:
    """Основной класс меню на pygame-gui"""
    def __init__(self, screen_width=800, screen_height=600):
        pygame.init()
        pygame.mixer.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Тетрис - Меню")
        self.clock = pygame.time.Clock()
        self.manager = pygame_gui.UIManager((self.screen_width, self.screen_height))
        
        self.current_screen = "main"
        self.selected_piece_size = 4
        self.selected_field_width = 10
        self.selected_field_height = 20
        self.player_name = "Игрок"
        
        # Загрузка утилит
        from utils import SaveManager, Leaderboard, ConfigManager
        self.save_manager = SaveManager()
        self.leaderboard = Leaderboard()
        self.config = ConfigManager()
        
        # Load menu sounds
        self.menu_select_sound = load_sound("menu_select.ogg", config=self.config)
        self.menu_hover_sound = load_sound("menu_hower.wav", config=self.config)
        
        # UI элементы
        self.buttons = {}
        self.text_inputs = {}
        self.labels = {}
        self.panels = {}
        
        # Load logo
        self.logo = load_logo(max_width=250)
        
        # Load menu music
        load_music("menu_music.mp3", volume=0.6, config=self.config)
        
        self.create_main_menu()
    
    def clear_ui(self):
        """Очистка всех UI элементов"""
        self.manager.clear_and_reset()
        self.buttons = {}
        self.text_inputs = {}
        self.labels = {}
        self.panels = {}
        self.save_infos = []  # Очищаем информацию о сохранениях
    
    def create_main_menu(self):
        """Создание главного меню"""
        self.clear_ui()
        self.current_screen = "main"
        
        # Заголовок - сейчас отрисовывается вручную как логотип
        # self.labels['title'] = pygame_gui.elements.UILabel(
        #     relative_rect=pygame.Rect((0, 50), (self.screen_width, 100)),
        #     text='ТЕТРИС',
        #     manager=self.manager
        # )
        # self.labels['title'].text_color = (255, 255, 0)
        
        # Кнопки меню - УВЕЛИЧЕНЫ РАЗМЕРЫ И ЦВЕТА ЯРЧЕ
        button_width = 250
        button_height = 70
        start_x = (self.screen_width - button_width) // 2

        self.buttons['new_game'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((start_x, 250), (button_width, button_height)),
            text='Новая игра',
            manager=self.manager
        )
        
        self.buttons['load_game'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((start_x, 330), (button_width, button_height)),
            text='Загрузить игру',
            manager=self.manager
        )
        
        self.buttons['leaders'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((start_x, 410), (button_width, button_height)),
            text='Таблица рекордов',
            manager=self.manager
        )
        
        self.buttons['quit'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((start_x, 490), (button_width, button_height)),
            text='Выход',
            manager=self.manager
        )
    
    def create_new_game_menu(self):
        """Создание меню новой игры"""
        self.clear_ui()
        self.current_screen = "new_game"
        
        # Заголовок - ЯРКИЙ ЖЕЛТЫЙ ЦВЕТ
        self.labels['title'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, 20), (self.screen_width, 60)),
            text='НОВАЯ ИГРА',
            manager=self.manager
        )
        self.labels['title'].text_color = (255, 255, 0)
        
        # Имя игрока - СВЕТЛЫЙ ЦВЕТ
        self.labels['name'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((50, 100), (200, 30)),
            text='Имя игрока:',
            manager=self.manager
        )
        self.labels['name'].text_color = (200, 200, 200)
        
        self.text_inputs['player_name'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((250, 100), (400, 40)),
            manager=self.manager
        )
        self.text_inputs['player_name'].set_text(self.player_name)
        
        # Размер фигур - УВЕЛИЧЕНЫ КНОПКИ
        self.labels['piece_size'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((50, 160), (200, 30)),
            text='Размер фигур:',
            manager=self.manager
        )
        self.labels['piece_size'].text_color = (200, 200, 200)
        
        piece_sizes = [4, 5, 6, 7]
        button_width = 80
        button_height = 40
        start_x = 250
        for i, size in enumerate(piece_sizes):
            self.buttons[f'piece_{size}'] = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((start_x + i * 90, 160), (button_width, button_height)),
                text=str(size),
                manager=self.manager
            )
            if size == self.selected_piece_size:
                self.buttons[f'piece_{size}'].select()
        
        # Размер поля - УВЕЛИЧЕНЫ КНОПКИ
        self.labels['field_size'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((50, 220), (200, 30)),
            text='Размер поля:',
            manager=self.manager
        )
        self.labels['field_size'].text_color = (200, 200, 200)
        
        field_sizes = [(10, 20), (12, 24), (15, 30)]
        start_x = 250
        for i, (w, h) in enumerate(field_sizes):
            self.buttons[f'field_{w}x{h}'] = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((start_x + i * 150, 220), (140, button_height)),
                text=f'{w}x{h}',
                manager=self.manager
            )
            if w == self.selected_field_width and h == self.selected_field_height:
                self.buttons[f'field_{w}x{h}'].select()
        
        # Кнопки действия - УВЕЛИЧЕНЫ
        self.buttons['start'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((150, 480), (200, 60)),
            text='Начать игру',
            manager=self.manager
        )
        
        self.buttons['back'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((450, 480), (200, 60)),
            text='Назад',
            manager=self.manager
        )

    def create_load_game_menu(self):
        """Создание меню загрузки игры"""
        self.clear_ui()
        self.current_screen = "load_game"
        
        # Заголовок
        self.labels['title'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, 20), (self.screen_width, 60)),
            text='ЗАГРУЗИТЬ ИГРУ',
            manager=self.manager
        )
        self.labels['title'].text_color = (255, 255, 0)
        
        # Получаем список сохранений
        self.saves = self.save_manager.get_save_files()
        
        if not self.saves:
            self.labels['no_saves'] = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((0, 250), (self.screen_width, 50)),
                text='Сохранения не найдены',
                manager=self.manager
            )
            self.labels['no_saves'].text_color = (200, 100, 100)
        else:
            # Создаем прокручиваемый список сохранений
            self.panels['saves_panel'] = pygame_gui.elements.UIScrollingContainer(
                relative_rect=pygame.Rect((30, 100), (740, 350)),
                manager=self.manager
            )
            
            for i, save in enumerate(self.saves):
                # Кнопка для загрузки сохранения
                save_button = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect((0, i * 55), (650, 50)),
                    text=f"{save.get('player_name', 'Игрок')} | {save.get('save_date', '')} | Очки: {save.get('score', 0)} | Уровень: {save.get('level', 1)} | Поле: {save.get('field_size', '10x20')} | Фигуры: {save.get('piece_size', '?')}",
                    manager=self.manager,
                    container=self.panels['saves_panel']
                )
                self.buttons[f'save_{i}'] = save_button
                self.buttons[f'save_{i}'].save_info = save
                self.buttons[f'save_{i}'].save_index = i
                
                # Кнопка удаления сохранения
                delete_button = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect((650, i * 55), (50, 50)),
                    text='X',
                    manager=self.manager,
                    container=self.panels['saves_panel']
                )
                self.buttons[f'delete_save_{i}'] = delete_button
                self.buttons[f'delete_save_{i}'].save_info = save
                self.buttons[f'delete_save_{i}'].is_delete = True
        
        self.buttons['back'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((300, 480), (200, 60)),
            text='Назад',
            manager=self.manager
        )
    
    def create_leaders_menu(self):
        """Создание меню таблицы рекордов с фильтрацией"""
        self.clear_ui()
        self.current_screen = "leaders"
        
        # Заголовок
        self.labels['title'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, 15), (self.screen_width, 50)),
            text=f'ТАБЛИЦА РЕКОРДОВ',
            manager=self.manager
        )
        self.labels['title'].text_color = (255, 255, 0)
        
        # Фильтр - размер фигур
        self.labels['filter_piece'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((50, 75), (140, 25)),
            text='Фигуры:',
            manager=self.manager
        )
        self.labels['filter_piece'].text_color = (200, 200, 200)
        
        for i, size in enumerate([4, 5, 6, 7]):
            self.buttons[f'leaders_piece_{size}'] = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((190 + i * 90, 70), (80, 40)),
                text=str(size),
                manager=self.manager
            )
            if size == self.selected_piece_size:
                self.buttons[f'leaders_piece_{size}'].select()
        
        # Фильтр - размер поля
        self.labels['filter_field'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((50, 120), (140, 25)),
            text='Поле:',
            manager=self.manager
        )
        self.labels['filter_field'].text_color = (200, 200, 200)
        
        for i, (w, h) in enumerate([(10, 20), (12, 24), (15, 30)]):
            self.buttons[f'leaders_field_{w}x{h}'] = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((190 + i * 150, 120), (140, 40)),
                text=f'{w}x{h}',
                manager=self.manager
            )
            if w == self.selected_field_width and h == self.selected_field_height:
                self.buttons[f'leaders_field_{w}x{h}'].select()
        
        # Получаем рекорды с текущими фильтрами
        self.current_leaders = self.leaderboard.get_leaders(
            self.selected_piece_size,
            f"{self.selected_field_width}x{self.selected_field_height}"
        )
        
        # Таблица рекордов
        if not self.current_leaders:
            self.labels['no_leaders'] = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((0, 250), (self.screen_width, 50)),
                text='Нет рекордов для выбранных параметров',
                manager=self.manager
            )
            self.labels['no_leaders'].text_color = (200, 100, 100)
        else:
            # Прокручиваемый контейнер
            self.panels['leaders_panel'] = pygame_gui.elements.UIScrollingContainer(
                relative_rect=pygame.Rect((30, 175), (740, 270)),
                manager=self.manager
            )
            
            # Заголовки (больший шрифт)
            headers = ['№', 'Игрок', 'Счет', 'Уровень', 'Линий']
            header_y = 0
            for i, header in enumerate(headers):
                h_label = pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect((i * 150, header_y), (140, 35)),
                    text=header,
                    manager=self.manager,
                    container=self.panels['leaders_panel']
                )
                h_label.text_color = (255, 200, 0)
                h_label.text_font = pygame.font.Font(None, 24)
            
            # Рекорды (больший размер строк)
            for idx, entry in enumerate(self.current_leaders[:20]):
                y = (idx + 1) * 35
                label1 = pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect((20, y), (130, 30)),
                    text=str(idx + 1),
                    manager=self.manager,
                    container=self.panels['leaders_panel']
                )
                label1.text_font = pygame.font.Font(None, 22)
                
                label2 = pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect((150, y), (130, 30)),
                    text=entry.get('player_name', '?'),
                    manager=self.manager,
                    container=self.panels['leaders_panel']
                )
                label2.text_font = pygame.font.Font(None, 22)
                
                label3 = pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect((280, y), (130, 30)),
                    text=str(entry.get('score', 0)),
                    manager=self.manager,
                    container=self.panels['leaders_panel']
                )
                label3.text_font = pygame.font.Font(None, 22)
                
                label4 = pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect((410, y), (130, 30)),
                    text=str(entry.get('level', 1)),
                    manager=self.manager,
                    container=self.panels['leaders_panel']
                )
                label4.text_font = pygame.font.Font(None, 22)
                pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect((540, y), (130, 25)),
                    text=str(entry.get('lines', 0)),
                    manager=self.manager,
                    container=self.panels['leaders_panel']
                )
        
        self.buttons['back'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((300, 480), (200, 60)),
            text='Назад',
            manager=self.manager
        )
    
    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            self.manager.process_events(event)
            
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                button = event.ui_element
                
                # Воспроизводим звук при нажатии кнопки
                if self.menu_select_sound:
                    self.menu_select_sound.play()
                
                # Главное меню
                if button == self.buttons.get('new_game'):
                    self.create_new_game_menu()
                elif button == self.buttons.get('load_game'):
                    self.create_load_game_menu()
                elif button == self.buttons.get('leaders'):
                    self.create_leaders_menu()
                elif button == self.buttons.get('quit'):
                    return False
                
                # Новая игра
                elif button == self.buttons.get('start'):
                    self.start_new_game()
                elif button == self.buttons.get('back') and self.current_screen in ['new_game', 'load_game', 'leaders']:
                    self.create_main_menu()
                
                # Выбор размера фигур в новой игре
                elif self.current_screen == 'new_game':
                    # Сохраняем введённое имя перед пересозданием меню
                    if 'player_name' in self.text_inputs:
                        self.player_name = self.text_inputs['player_name'].get_text()
                    
                    for size in [4, 5, 6, 7]:
                        if button == self.buttons.get(f'piece_{size}'):
                            self.selected_piece_size = size
                            self.create_new_game_menu()
                    for w, h in [(10, 20), (12, 24), (15, 30)]:
                        if button == self.buttons.get(f'field_{w}x{h}'):
                            self.selected_field_width = w
                            self.selected_field_height = h
                            self.create_new_game_menu()
                
                # Фильтр лидерборда
                elif self.current_screen == 'leaders':
                    for size in [4, 5, 6, 7]:
                        if button == self.buttons.get(f'leaders_piece_{size}'):
                            self.selected_piece_size = size
                            self.create_leaders_menu()
                    for w, h in [(10, 20), (12, 24), (15, 30)]:
                        if button == self.buttons.get(f'leaders_field_{w}x{h}'):
                            self.selected_field_width = w
                            self.selected_field_height = h
                            self.create_leaders_menu()
                
                # Загрузка игры
                elif self.current_screen == 'load_game':
                    for i in range(len(self.saves)):
                        # Кнопка загрузки
                        if button == self.buttons.get(f'save_{i}'):
                            self.load_selected_game(self.saves[i])
                        # Кнопка удаления
                        elif button == self.buttons.get(f'delete_save_{i}'):
                            self.delete_save(self.saves[i])
        
        return True
    
    def start_new_game(self):
        """Запуск новой игры"""
        from game import TetrisGame
        
        if 'player_name' in self.text_inputs:
            self.player_name = self.text_inputs['player_name'].get_text() or "Игрок"
        
        game = TetrisGame(
            self.selected_field_width,
            self.selected_field_height,
            self.selected_piece_size,
            self.player_name,
            self.save_manager,
            self.leaderboard,
            self.config
        )
        game.run()
        # После завершения игры возвращаемся в меню
        self.reload_menu_music()
        self.create_main_menu()
    
    def load_selected_game(self, save_info):
        """Загрузка выбранной игры"""
        from game import TetrisGame
        
        save_data = self.save_manager.load_game(save_info['filename'])
        if save_data:
            game = TetrisGame(
                save_data['width'],
                save_data['height'],
                save_data['piece_size'],
                save_data['player_name'],
                self.save_manager,
                self.leaderboard,
                self.config,
                save_data
            )
            game.run()
            # После завершения игры возвращаемся в меню
            self.reload_menu_music()
            self.create_main_menu()

    def delete_save(self, save_info):
        """Удаление сохраненной игры"""
        save_filename = save_info.get('filename')
        if save_filename and self.save_manager.delete_save(save_filename):
            print(f"Сохранение {save_filename} удалено")
        # Обновляем меню загрузки
        self.create_load_game_menu()

    def update(self, time_delta):
        """Обновление UI"""
        self.manager.update(time_delta)
    
    def draw(self):
        """Отрисовка меню"""
        self.screen.fill((30, 30, 50))
        
        # Отрисовка логотипа в главном меню
        if self.current_screen == "main" and self.logo:
            x = (self.screen_width - self.logo.get_width()) // 2
            y = 20
            self.screen.blit(self.logo, (x, y))
        
        self.manager.draw_ui(self.screen)
        pygame.display.flip()
    
    def reload_menu_music(self):
        """Перезагрузить музыку меню после возврата из игры"""
        load_music("menu_music.mp3", volume=0.6, config=self.config)
    
    def run(self):
        """Запуск главного цикла меню"""
        running = True
        
        while running:
            time_delta = self.clock.tick(60) / 1000.0
            
            running = self.handle_events()
            self.update(time_delta)
            self.draw()
        
        pygame.quit()
        sys.exit()