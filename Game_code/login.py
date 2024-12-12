import pygame, pigame
import sys
import os
from Runner import play_game
import sqlite3

# 初始化 pygame
os.putenv('SDL_VIDEODRV', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'dummy')
os.putenv('SDL_MOUSEDEV', '/dev/null')
os.putenv('DISPLAY', '')

pygame.init()
# pygame.mouse.set_visible(False)
global pitft
pitft = pigame.PiTft()

# 屏幕设置
screen = pygame.display.set_mode((320, 240))

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# 字体定义
font = pygame.font.Font(None, 15)  # 缩小字体大小
small_font = pygame.font.Font(None, 10)

# 比例缩放函数
def scale(x, y):
    return int(x * 0.4), int(y * 0.6)

# 输入框类
class InputBox:
    def __init__(self, x, y, w, h, text=''):
        x, y = scale(x, y)  # 缩放位置
        w, h = scale(w, h)  # 缩放尺寸
        self.rect = pygame.Rect(x, y, w, h)
        self.color = GRAY
        self.text = text
        self.txt_surface = font.render(text, True, BLACK)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 检测鼠标点击
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = GREEN if self.active else GRAY
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = font.render(self.text, True, BLACK)

    def draw(self, screen):
        # 绘制输入框
        pygame.draw.rect(screen, self.color, self.rect, 2)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

# 按钮类
class Button:
    def __init__(self, x, y, w, h, text):
        x, y = scale(x, y)  # 缩放位置
        w, h = scale(w, h)  # 缩放尺寸
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = GRAY
        self.txt_surface = font.render(text, True, BLACK)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.txt_surface, (self.rect.x + (self.rect.width - self.txt_surface.get_width()) // 2,
                                       self.rect.y + (self.rect.height - self.txt_surface.get_height()) // 2))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# 登录检查
def check_login(username, password):
    if not os.path.exists("player.txt"):
        return False
    with open("player.txt", "r") as file:
        for line in file:
            user, pw = line.strip().split()
            if username == user and password == pw:
                return True
    return False

# 注册用户
def register_user(username, password):
    # 检查用户名是否已存在
    if os.path.exists("player.txt"):
        with open("player.txt", "r") as file:
            for line in file:
                user, _ = line.strip().split()
                if username == user:
                    return False  # 用户名已存在
    # 如果用户名不存在，则写入文件
    with open("player.txt", "a") as file:
        file.write(f"{username} {password}\n")
    return True

# 主函数
def login():
    clock = pygame.time.Clock()

    # 输入框和按钮
    username_box = InputBox(300, 100, 200, 40)
    password_box = InputBox(300, 160, 200, 40)
    login_button = Button(300, 220, 100, 40, "Login")
    register_button = Button(420, 220, 100, 40, "Register")

    # 错误提示
    error_message = ""

    running = True
    while running:
        pitft.update()
        screen.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            username_box.handle_event(event)
            password_box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                # 检查 Login 按钮
                if login_button.is_clicked(event.pos):
                    username = username_box.text
                    password = password_box.text
                    if check_login(username, password):
                        play_game(username)
                    else:
                        error_message = "Invalid username or password."
                # 检查 Register 按钮
                if register_button.is_clicked(event.pos):
                    username = username_box.text
                    password = password_box.text
                    if username and password:
                        if register_user(username, password):
                            error_message = "User registered successfully!"
                        else:
                            error_message = "Username already exists."
                    else:
                        error_message = "Username and password cannot be empty."

        # 绘制 UI 元素
        username_box.draw(screen)
        password_box.draw(screen)
        login_button.draw(screen)
        register_button.draw(screen)

        # 显示提示文字
        screen.blit(font.render("Username:", True, BLACK), scale(150, 110))
        screen.blit(font.render("Password:", True, BLACK), scale(150, 170))
        if error_message:
            screen.blit(small_font.render(error_message, True, RED), scale(300, 280))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

login()