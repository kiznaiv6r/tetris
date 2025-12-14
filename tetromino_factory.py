"""
Фабрика для создания тетромино (паттерн Factory Method)
Включает интеллектуальную генерацию для избежания повторяющихся фигур.
"""
import random
from resources.game_resources import SHAPES, COLORS

class Tetromino:
    """Класс фигуры тетрамино"""
    def __init__(self, shape_type: str, piece_size: int, shape: list, color: tuple):
        self.shape_type = shape_type
        self.piece_size = piece_size
        self.shape = shape 
        self.color = color
        self.x = 0
        self.y = 0
        
    def get_rotated(self):
        """Получение повернутой фигуры (без изменения оригинала)"""
        n = len(self.shape)
        rotated = [[0 for _ in range(n)] for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                rotated[j][n-1-i] = self.shape[i][j]
        
        return rotated
    
    def get_width(self):
        """Ширина фигуры"""
        return len(self.shape[0]) if self.shape else 0
    
    def get_height(self):
        """Высота фигуры"""
        return len(self.shape) if self.shape else 0


class TetrominoFactory:
    """
    Фабрика для создания фигур тетромино.
    
    Использует паттерн Factory Method для централизованного создания фигур.
    Включает интеллектуальную систему генерации, которая:
    - Избегает создания одинаковых фигур подряд
    - Использует циклическую очередь для равномерного распределения
    - Поддерживает разные размеры фигур (4, 5, 6, 7)
    """
    
    def __init__(self, piece_size: int = 4):
        """
        Инициализация фабрики.
        
        Args:
            piece_size: Размер фигур (4 = тетрамино, 5 = пентамино, 6 = гексамино, 7 = гептамино)
        """
        self.piece_size = piece_size
        self._update_available_shapes()
        self._generation_queue = []  # Очередь для генерации
        self._last_piece = None  # Последняя сгенерированная фигура
        self._shuffle_queue()
    
    def _update_available_shapes(self):
        """Обновляет список доступных фигур для текущего размера и ниже"""
        # Используем фигуры для выбранного размера и все размеры ниже
        self.shapes_dict = {}
        for size in range(4, self.piece_size + 1):
            if size in SHAPES:
                self.shapes_dict.update(SHAPES[size])
        
        # Если размер меньше 4, используем только размер 4
        if not self.shapes_dict:
            self.shapes_dict = SHAPES.get(4, {})
        
        self.available_shapes = list(self.shapes_dict.keys())
    
    def set_piece_size(self, piece_size: int):
        """Изменить размер фигур и сбросить очередь генерации"""
        self.piece_size = piece_size
        self._update_available_shapes()
        self._generation_queue = []
        self._last_piece = None
        self._shuffle_queue()
    
    def _shuffle_queue(self):
        """Перемешать и создать новую очередь всех фигур"""
        self._generation_queue = self.available_shapes.copy()
        random.shuffle(self._generation_queue)
    
    def create_tetromino(self, shape_type: str):
        """
        Создание тетромино заданного типа.
        
        Args:
            shape_type: Тип фигуры ('I', 'O', 'T', 'S', 'Z', 'J', 'L', и т.д.)
            
        Returns:
            Объект Tetromino
        """
        shape = self.shapes_dict.get(shape_type, self.shapes_dict['I'])
        color = COLORS.get(shape_type, (255, 255, 255))
        return Tetromino(shape_type, self.piece_size, shape, color)
    
    def create_random(self) -> Tetromino:
        """
        Создание случайного тетромино с интеллектуальной генерацией.
        
        Использует циклическую очередь для:
        - Избежания повторяющихся фигур подряд
        - Равномерного распределения всех типов фигур
        
        Returns:
            Объект Tetromino
        """
        # Если очередь пуста, перемешиваем снова
        if not self._generation_queue:
            self._shuffle_queue()
        
        # Берём следующую фигуру из очереди
        shape_type = self._generation_queue.pop(0)
        
        # Если это была последняя фигура, перемешиваем очередь для следующей
        if not self._generation_queue:
            self._shuffle_queue()
        
        self._last_piece = shape_type
        return self.create_tetromino(shape_type)
    
    def get_next_preview(self) -> Tetromino:
        if not self._generation_queue:
            self._shuffle_queue()
        return self.create_tetromino(self._generation_queue[0])
        
    
    def get_available_shapes(self) -> list:
        """Получить список доступных типов фигур"""
        return self.available_shapes.copy()
    
    def get_piece_size(self) -> int:
        """Получить текущий размер фигур"""
        return self.piece_size
    
    def reset_generation(self):
        """Сбросить историю генерации и перемешать очередь"""
        self._generation_queue = []
        self._last_piece = None
        self._shuffle_queue()