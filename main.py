"""
Главный файл игры Тетрис
"""
import pygame
from menu import Menu

def main():
    """Основная функция запуска"""
    try:
        menu = Menu()
        menu.run()
    except Exception as e:
        print(f"Ошибка запуска: {e}")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()