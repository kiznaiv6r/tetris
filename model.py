# model.py
import copy
from typing import List, Optional
from tetromino_factory import TetrominoFactory, Tetromino
from resources.game_resources import COLORS


class GameModel:
    def __init__(self, width: int, height: int, piece_size: int, player_name: str = "Игрок", session_id: str = None):
        self.width = width
        self.height = height
        self.piece_size = piece_size
        self.player_name = player_name or "Игрок"
        
        # Генерируем или используем переданный session_id
        if session_id:
            self.session_id = session_id
        else:
            import uuid
            self.session_id = str(uuid.uuid4())

        self.field: List[List[Optional[tuple]]] = [[0] * width for _ in range(height)]
        self.factory = TetrominoFactory(piece_size)

        self.current_piece: Optional[Tetromino] = None
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.speed = 500

        self.paused = False
        self.game_over = False
        self.level_up = False  # Флаг для отслеживания повышения уровня
        self.lines_cleared_this_turn = 0  # Количество линий, очищенных в этом ходу

        self._spawn_piece()

    def _check_game_over(self):
        """
        Check if the game is over: if a new piece cannot spawn in the visible field
        or if any cell reaches the top boundary.
        """
        if not self.current_piece:
            return

        for i, row in enumerate(self.current_piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    x = self.current_piece.x + j
                    y = self.current_piece.y + i
                    # Check if the piece overlaps with existing blocks in the visible field
                    if y >= 0 and (x < 0 or x >= self.width or (y < self.height and self.field[y][x] != 0)):
                        self.game_over = True
                        return

        # Additional check: if any block in the top row is occupied
        if any(self.field[0][x] != 0 for x in range(self.width)):
            self.game_over = True

    def _spawn_piece(self):
        self.current_piece = self.factory.create_random()
        self.current_piece.x = (self.width - self.current_piece.get_width()) // 2
        self.current_piece.y = -self.current_piece.get_width()  # Фигура появляется за пределом сверху
        self._check_game_over()

    @property
    def next_piece(self) -> Tetromino:
        return self.factory.get_next_preview()

    def _check_collision(self, piece=None, dx=0, dy=0):
        piece = piece or self.current_piece
        if not piece:
            return True
        for i in range(len(piece.shape)):
            for j in range(len(piece.shape[i])):
                if piece.shape[i][j]:
                    x = piece.x + j + dx
                    y = piece.y + i + dy
                    if x < 0 or x >= self.width or y >= self.height:
                        return True
                    if y >= 0 and self.field[y][x] != 0:
                        return True
        return False

    def move(self, dx: int, dy: int) -> bool:
        if self.game_over or self.paused or not self.current_piece:
            return False
        if not self._check_collision(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False

    def rotate_piece(self):
        if self.game_over or self.paused or not self.current_piece:
            return
        old_shape = copy.deepcopy(self.current_piece.shape)
        old_x = self.current_piece.x
        
        # Try to rotate
        self.current_piece.shape = self.current_piece.get_rotated()
        
        # If collision, try wall kick (shift left/right)
        if self._check_collision():
            # Try shifting right
            self.current_piece.x = old_x + 1
            if not self._check_collision():
                return  # Success with right shift
            
            # Try shifting left
            self.current_piece.x = old_x - 1
            if not self._check_collision():
                return  # Success with left shift
            
            # Try shifting right 2 cells
            self.current_piece.x = old_x + 2
            if not self._check_collision():
                return  # Success with right shift 2
            
            # Try shifting left 2 cells
            self.current_piece.x = old_x - 2
            if not self._check_collision():
                return  # Success with left shift 2
            
            # Rotation failed, revert
            self.current_piece.shape = old_shape
            self.current_piece.x = old_x

    def drop(self) -> bool:
        if self.move(0, 1):
            return True
        self._lock_piece()
        return False

    def hard_drop(self) -> int:
        rows = 0
        while self.move(0, 1):
            rows += 1
        self._lock_piece()
        return rows

    def _lock_piece(self):
        if not self.current_piece:
            return
        for i in range(len(self.current_piece.shape)):
            for j in range(len(self.current_piece.shape[i])):
                if self.current_piece.shape[i][j]:
                    x = self.current_piece.x + j
                    y = self.current_piece.y + i
                    if y >= 0:
                        self.field[y][x] = self.current_piece.color
        self._clear_lines()
        self._spawn_piece()
        # Проверяем game_over после спауна новой фигуры
        self._check_game_over()

    def _clear_lines(self):
        lines = 0
        new_field = [row for row in self.field if not all(c != 0 for c in row)]
        lines = self.height - len(new_field)
        while len(new_field) < self.height:
            new_field.insert(0, [0] * self.width)
        self.field = new_field

        self.lines_cleared_this_turn = lines  # Сохраняем количество очищенных линий

        if lines:
            points = [0, 40, 100, 300, 1200][min(lines, 4)]
            self.score += points * self.level
            self.lines_cleared += lines
            
            # Система повышения уровня: каждые 5 линий
            old_level = self.level
            self.level = self.lines_cleared // 5 + 1
            
            # Бонус за повышение уровня
            if self.level > old_level:
                bonus = (self.level - old_level) * 500
                self.score += bonus
                self.level_up = True  # Установить флаг повышения уровня
            
            # Увеличение скорости с каждым уровнем
            self.speed = max(50, 500 - (self.level - 1) * 50)

    def get_ghost_position(self):
        if not self.current_piece:
            return None
        ghost = copy.deepcopy(self.current_piece)
        while not self._check_collision(ghost, 0, 1):
            ghost.y += 1
        return ghost

    def reset_game(self):
        self.field = [[0] * self.width for _ in range(self.height)]
        self.score = self.level = self.lines_cleared = 0
        self.speed = 500
        self.game_over = self.paused = False
        self.factory.reset_generation()
        self._spawn_piece()

    def get_save_data(self):
        shape = copy.deepcopy(self.current_piece.shape) if self.current_piece else None
        return {
            "width": self.width, "height": self.height, "piece_size": self.piece_size,
            "player_name": self.player_name, "field": copy.deepcopy(self.field),
            "score": self.score, "level": self.level, "lines_cleared": self.lines_cleared,
            "current_piece_type": self.current_piece.shape_type if self.current_piece else "",
            "current_piece_pos": (self.current_piece.x, self.current_piece.y) if self.current_piece else (0, 0),
            "current_shape": shape,
            "session_id": self.session_id,  # Сохраняем session_id
        }

    def load_from_save(self, data):
        self.width = data["width"]
        self.height = data["height"]
        self.piece_size = data["piece_size"]
        self.player_name = data["player_name"]
        self.field = copy.deepcopy(data["field"])
        self.score = data["score"]
        self.level = data["level"]
        self.lines_cleared = data["lines_cleared"]
        self.session_id = data.get("session_id", self.session_id)  # Восстанавливаем session_id

        self.factory = TetrominoFactory(self.piece_size)
        self.factory.reset_generation()

        ctype = data.get("current_piece_type")
        cpos = data.get("current_piece_pos", (0, 0))
        cshape = data.get("current_shape")

        if ctype and cshape:
            color = COLORS.get(ctype, (255, 255, 255))
            self.current_piece = Tetromino(ctype, self.piece_size, cshape, color)
            self.current_piece.x, self.current_piece.y = cpos
        else:
            self.current_piece = None

        self.speed = max(50, 500 - (self.level - 1) * 50)
        self.game_over = False
        self.paused = True  # ← ВАЖНО: загруженная игра на паузе