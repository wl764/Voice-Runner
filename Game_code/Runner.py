import pygame
from sys import exit
from random import randint, choice
from PIL import Image  # Import Pillow to handle GIFs
from Sql import init_db, save_score
import sqlite3
from Volume import Get_max_amp
import threading
import frc
import os

global current_dir 
current_dir = os.path.dirname(os.path.abspath(__file__))
class Fireball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("graphics/Player/fireball.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (12, 12))  # Resize fireball
        self.rect = self.image.get_rect(midbottom=(x, y))  # Fireball position
        self.x_speed = 2.4  # Adjusted fireball speed

    def update(self):
        self.rect.x += self.x_speed  # Move fireball rightward
        if self.rect.x > 320:  # Remove fireball if off-screen
            self.kill()

        for obstacle in obstacle_group:
            if self.rect.colliderect(obstacle.rect):
                obstacle.kill()  # Remove obstacle
                self.kill()  # Remove fireball
                break


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Load GIF and scale each frame
        self.player_walk = self.load_gif_frames("graphics/Player/player_walk_1.gif", (25, 33))
        self.player_index = 0
        self.player_jump = pygame.image.load("graphics/Player/player_jump.png").convert_alpha()
        self.player_squat = pygame.image.load("graphics/Player/player_squat.png").convert_alpha()
        self.player_jump = pygame.transform.scale(self.player_jump, (25, 33))
        self.player_squat = pygame.transform.scale(self.player_squat, (35, 26))

        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom=(32, 120))
        self.image1 = self.player_squat
        self.rect1 = self.image1.get_rect(midbottom=(32, 120))
        self.gravity = 0

        # Define collision rectangles
        self.collision_rect = pygame.Rect(self.rect.topleft[0], self.rect.topleft[1], 21, 30)
        self.collision_rect_sq = pygame.Rect(self.rect1.topleft[0], self.rect1.topleft[1], 35, 26)

        self.is_squatting = False

        # self.jump_sound = pygame.mixer.Sound(os.path.join(current_dir, "audio/jump.mp3"))
        # self.jump_sound.set_volume(0.5)
        self.squat_timer = 0
        self.last_shot_time = 0

    def load_gif_frames(self, gif_path, size):
        """Load and scale GIF frames."""
        gif = Image.open(gif_path)
        frames = []
        try:
            while True:
                frame = gif.copy()
                frame = frame.convert("RGBA")
                frame = frame.resize(size)
                pygame_image = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
                frames.append(pygame_image)
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass
        return frames

    def player_input(self):
        max_amplitude_freq_1 = frc.max_amplitude_freq_1
        max_amplitude_freq_2 = frc.max_amplitude_freq_2
        if max_amplitude_freq_1 > 450 and self.rect.bottom == 120:
            self.gravity = -8.8

        if (50 < max_amplitude_freq_1 < 150 and 50 < max_amplitude_freq_2 < 150)and(125< max_amplitude_freq_1 < 130 and 125 < max_amplitude_freq_2 < 130) and self.rect.bottom == 120:
            self.squat_timer += 1  # 增加下蹲计时
            if self.squat_timer < 100:  # 控制下蹲状态持续的时间，例如持续30帧
                self.image = self.player_squat
                self.rect = self.image1.get_rect(midbottom=(32, 120))
                self.is_squatting = True
            else:
                self.squat_timer = 0  # 重置计时器
                self.is_squatting = False  # 恢复站立

        else:
            if self.rect == self.rect1:
                self.rect = self.image.get_rect(midbottom=(32, 120))
            self.is_squatting = False

        current_time = pygame.time.get_ticks()
        if (
            150 < max_amplitude_freq_1 < 450
            and 150 < max_amplitude_freq_2 < 450
            and current_time - self.last_shot_time >= 2000
        ):
            fireball = Fireball(self.rect.right, self.rect.centery)
            fireball_group.add(fireball)
            self.last_shot_time = current_time

    def player_gravity(self):
        self.gravity += 0.32
        self.rect.y += self.gravity
        if self.rect.bottom >= 120:
            self.rect.bottom = 120

    def animation_state(self):
        if self.rect.bottom < 120:
            self.image = self.player_jump
        elif not self.is_squatting:
            self.player_index += 0.1
            if self.player_index >= len(self.player_walk):
                self.player_index = 0
            self.image = self.player_walk[int(self.player_index)]

    def update_collision_rect(self):
        """Update collision rectangle."""
        if self.is_squatting:
            self.collision_rect_sq.topleft = self.rect.topleft
        else:
            self.collision_rect.topleft = self.rect.topleft

    def update(self):
        self.player_input()
        self.player_gravity()
        self.animation_state()
        self.update_collision_rect()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()
        self.type = type
        if type == "fly":
            fly_1 = pygame.image.load("graphics/Fly/Evil1.png").convert_alpha()
            fly_2 = pygame.image.load("graphics/Fly/Evil2.png").convert_alpha()
            fly_1 = pygame.transform.scale(fly_1, (24, 16))
            fly_2 = pygame.transform.scale(fly_2, (24, 16))
            self.frames = [fly_1, fly_2]
            y_pos = 92
        elif type == "snail":
            snail_1 = pygame.image.load("graphics/snail/mouse1.png").convert_alpha()
            snail_2 = pygame.image.load("graphics/snail/mouse2.png").convert_alpha()
            snail_1 = pygame.transform.scale(snail_1, (24, 22))
            snail_2 = pygame.transform.scale(snail_2, (24, 22))
            self.frames = [snail_1, snail_2]
            y_pos = 128
        elif type == "paper":
            paper_1 = pygame.image.load("graphics/Player/paper.png").convert_alpha()
            paper_1 = pygame.transform.scale(paper_1, (40, 40))
            self.frames = [paper_1, paper_1]
            y_pos = 120
        elif type == "Coin":
            Coin1 = pygame.image.load("graphics/Coin.png").convert_alpha()
            Coin1 = pygame.transform.scale(Coin1, (16, 16))
            self.frames = [Coin1, Coin1]
            y_pos = choice([84, 120])

        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(midbottom=(randint(360, 440), y_pos))

    def animation_state(self):
        self.animation_index += 0.1
        if self.animation_index >= len(self.frames):
            self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def destroy(self):
        if self.rect.x <= -40 and self.type != "Coin":
            self.kill()

    def update(self):
        self.animation_state()
        self.rect.x -= 2
        self.destroy()

def collision_sprite():
    global score  # 确保修改全局score
    for obstacle in obstacle_group:
        if player.sprite.is_squatting:
            if player.sprite.collision_rect_sq.colliderect(obstacle.rect):
                if obstacle.type == 'Coin':  # 如果碰撞的是金币
                    obstacle.kill()  # 移除金币
                    score += 10  # 分数加10
                else:
                    obstacle_group.empty()  # 碰到障碍物就结束游戏
                    return False
        else:
            if player.sprite.collision_rect.colliderect(obstacle.rect):
                if obstacle.type == 'Coin':  # 如果碰撞的是金币
                    obstacle.kill()  # 移除金币
                    score += 10  # 分数加10
                else:
                    obstacle_group.empty()  # 碰到障碍物就结束游戏
                    return False
    return True
def display_score():
    global score
    current_time = int((pygame.time.get_ticks() - start_time) / 1000)
    score_total = score + current_time
    score_surf = text_font.render(f"Score : {score_total}", False, (64, 64, 64))
    score_rect = score_surf.get_rect(center=(160, 20))  # 缩放坐标
    pygame.draw.rect(screen, (192, 232, 207), score_rect)
    pygame.draw.rect(screen, (192, 232, 207), score_rect, 4)  # 缩放边框厚度
    screen.blit(score_surf, score_rect)
    return score_total


def play_game(username):
    global score, game_active, start_time, score_final, player, obstacle_group, fireball_group, text_font, screen

    init_db()
    pygame.init()
    screen = pygame.display.set_mode((320, 160))  # 缩放窗口大小
    pygame.display.set_caption("5725 project")
    clock = pygame.time.Clock()
    text_font = pygame.font.Font("font/Pixeltype.ttf", 20)  # 缩小字体大小
    game_active = False
    start_time = 0
    score = 0
    score_final = 0

    # Groups
    player = pygame.sprite.GroupSingle()
    player.add(Player())

    obstacle_group = pygame.sprite.Group()
    fireball_group = pygame.sprite.Group()

    # Background and ground
    sky_surf = pygame.image.load("graphics/Sky.png").convert()
    sky_surf = pygame.transform.scale(sky_surf, (320, 160))  # 缩放背景
    ground_surf = pygame.image.load("graphics/ground.png").convert()
    ground_surf = pygame.transform.scale(ground_surf, (320, 60))  # 缩放地面

    # Intro screen
    game_name = text_font.render("Cornell Bear", False, (111, 196, 169))
    game_name_rect = game_name.get_rect(center=(160, 32))  # 缩放坐标

    player_stand = pygame.image.load("graphics/Player/player_jump.png").convert_alpha()
    player_stand = pygame.transform.scale(player_stand, (20, 20))  # 缩放图片
    player_stand = pygame.transform.rotozoom(player_stand, 0, 1.6)  # 调整比例缩放
    player_stand_rect = player_stand.get_rect(center=(160, 80))  # 缩放坐标

    game_message = text_font.render("Press space to run", False, (111, 196, 169))
    game_message_rect = game_message.get_rect(center=(160, 132))  # 缩放坐标

    # Timer for spawning obstacles
    obstacle_timer = pygame.USEREVENT + 1
    pygame.time.set_timer(obstacle_timer, 2000)

    thread1 = threading.Thread(target=Get_max_amp)
    thread1.start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if game_active:
                # Spawn obstacles
                if event.type == obstacle_timer:
                    obstacle_group.add(Obstacle(choice(['fly', 'paper', 'snail', 'Coin'])))
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_active = True
                    score_final = 0
                    score = 0
                    start_time = pygame.time.get_ticks()

        if game_active:
            # Game screen
            screen.blit(sky_surf, (0, 0))
            screen.blit(ground_surf, (0, 120))  # 调整地面位置
            score_final = display_score()

            player.draw(screen)
            player.update()

            obstacle_group.draw(screen)
            obstacle_group.update()

            fireball_group.draw(screen)  # Draw all fireballs
            fireball_group.update()  # Update fireballs

            # Collision detection
            if not collision_sprite():
                game_active = False
                # Save score to database
                save_score(username, score_final)
        else:
            # Intro screen
            screen.fill((94, 129, 162))
            screen.blit(game_name, game_name_rect)
            screen.blit(player_stand, player_stand_rect)

            # 显示当前游戏分数
            game_score = text_font.render(f"Your score : {score_final}", False, (111, 196, 169))
            game_score_rect = game_score.get_rect(center=(160, 132))

            if score:
                screen.blit(game_score, game_score_rect)
            else:
                screen.blit(game_message, game_message_rect)

            # 获取用户的最高 5 次分数
            conn = sqlite3.connect("scores.db")
            cursor = conn.cursor()
            cursor.execute("SELECT score FROM scores WHERE username = ? ORDER BY score DESC LIMIT 5", (username,))
            top_scores = cursor.fetchall()

            # 获取全局最高 5 次分数及对应用户
            cursor.execute("SELECT username, score FROM scores ORDER BY score DESC LIMIT 5")
            global_top_scores = cursor.fetchall()
            conn.close()

            # 显示最高 5 次成绩
            top_scores_text = text_font.render("Top Scores:", False, (255, 255, 255))
            top_scores_text_rect = top_scores_text.get_rect(topleft=(20, 20))
            screen.blit(top_scores_text, top_scores_text_rect)

            for i, (score,) in enumerate(top_scores):
                score_text = text_font.render(f"{i + 1}. {score}", False, (255, 255, 255))
                score_text_rect = score_text.get_rect(topleft=(20, 50 + i * 20))  # 缩放行距
                screen.blit(score_text, score_text_rect)

            global_scores_text = text_font.render("Global Top Scores:", False, (255, 255, 255))
            global_scores_text_rect = global_scores_text.get_rect(topleft=(200, 20))  # 缩放坐标
            screen.blit(global_scores_text, global_scores_text_rect)

            for i, (user, score) in enumerate(global_top_scores):
                global_score_text = text_font.render(f"{i + 1}. {user}: {score}", False, (255, 255, 255))
                global_score_text_rect = global_score_text.get_rect(topleft=(200, 50 + i * 20))  # 缩放行距
                screen.blit(global_score_text, global_score_text_rect)

        pygame.display.update()
        clock.tick(60)