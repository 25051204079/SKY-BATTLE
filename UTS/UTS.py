import pygame
import random
import os

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sky Battle Final")

clock = pygame.time.Clock()

WHITE = (255,255,255)
BLUE = (0,150,255)
GREEN = (0,200,0)
RED = (255,0,0)

# ======================
# LOAD IMAGE
# ======================
def load_image(name, size):
    if os.path.exists(name):
        img = pygame.image.load(name)
        return pygame.transform.scale(img, size)
    return None

bg = load_image("background.png", (WIDTH, HEIGHT))
player_img = load_image("player.png", (80, 60))
car_img = load_image("car.png", (60, 40))
enemy_plane_img = load_image("enemy_plane.png", (60, 40))

# ======================
# SOUND
# ======================

# BACKSOUND
try:
    pygame.mixer.music.load("bgm.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)  # loop terus
except:
    print("BGM tidak ditemukan!")

# SOUND TEMBAKAN
try:
    shoot_sound = pygame.mixer.Sound("shoot.mp3")
    shoot_sound.set_volume(0.3)
except:
    shoot_sound = None
    print("Sound tembakan tidak ditemukan!")

# ======================
# PARENT CLASS
# ======================
class GameObject:
    def __init__(self, x, y, w, h, speed, image=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.speed = speed
        self.image = image

    def draw(self, surface, color):
        if self.image:
            surface.blit(self.image, self.rect)
        else:
            pygame.draw.rect(surface, color, self.rect)

# ======================
# PLAYER
# ======================
class Player(GameObject):
    def move(self, keys):
        if keys[pygame.K_UP] and self.rect.y > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.y < HEIGHT - self.rect.height:
            self.rect.y += self.speed
        if keys[pygame.K_LEFT] and self.rect.x > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.x < WIDTH - self.rect.width:
            self.rect.x += self.speed

    def shoot(self):
        return Bullet(self.rect.right, self.rect.centery, 10, 5, 8)

# ======================
# BULLET
# ======================
class Bullet(GameObject):
    def update(self):
        self.rect.x += self.speed

# ======================
# ENEMY (PARENT)
# ======================
class Enemy(GameObject):
    def update(self):
        self.rect.x -= self.speed

# ======================
# MOBIL
# ======================
class CarEnemy(Enemy):
    def __init__(self):
        super().__init__(WIDTH, HEIGHT-40, 50, 30, 4, car_img)

# ======================
# PESAWAT MUSUH
# ======================
class AirEnemy(Enemy):
    def __init__(self):
        y = random.randint(50, HEIGHT-100)
        super().__init__(WIDTH, y, 50, 30, 6, enemy_plane_img)

# ======================
# HIGHSCORE SYSTEM
# ======================
def load_highscore():
    try:
        with open("highscore.txt", "r") as f:
            return int(f.read())
    except:
        return 0

def save_highscore(score):
    with open("highscore.txt", "w") as f:
        f.write(str(score))

def menu():
    highscore = load_highscore()
    font = pygame.font.SysFont(None, 40)
    big_font = pygame.font.SysFont(None, 70)

    bg_x = 0
    while True:
        if bg:
            screen.blit(bg, (0, 0))
        else:
            screen.fill((20,20,40))

        bg_x -= 0.3
        if bg_x <= -WIDTH:
            bg_x = 0

        screen.blit(bg, (bg_x, 0))
        screen.blit(bg, (bg_x + WIDTH, 0))

        # Judul
        title = big_font.render("SKY BATTLE", True, WHITE)
        screen.blit(title, (WIDTH//2 - 160, 100))

        # High Score
        hs_text = font.render(f"High Score: {highscore}", True, WHITE)
        screen.blit(hs_text, (WIDTH//2 - 110, 200))

        # Instruksi
        start_text = font.render("Press ENTER to Start", True, WHITE)
        exit_text = font.render("Press ESC to Exit", True, WHITE)

        screen.blit(start_text, (WIDTH//2 - 150, 260))
        screen.blit(exit_text, (WIDTH//2 - 120, 300))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return  # masuk ke game
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

# ======================
# GAME
# ======================
def game():
    player = Player(50, HEIGHT//2, 60, 40, 5, player_img)

    bullets = []
    enemies = []

    spawn_timer = 0
    score = 0
    lives = 3

    font = pygame.font.SysFont(None, 30)
    big_font = pygame.font.SysFont(None, 60)

    bg_x = 0  # 🔥 scrolling

    running = True
    game_over = False

    highscore = load_highscore()

    while running:
        # ======================
        # BACKGROUND SCROLLING
        # ======================
        if bg:
            bg_x -= 2
            if bg_x <= -WIDTH:
                bg_x = 0
            screen.blit(bg, (bg_x, 0))
            screen.blit(bg, (bg_x + WIDTH, 0))
        else:
            screen.fill((135,206,235))

        # ======================
        # EVENT
        # ======================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    bullets.append(player.shoot())
                    if shoot_sound:
                        shoot_sound.play()

                if event.key == pygame.K_r and game_over:
                    return game()
                
                if event.key == pygame.K_m and game_over:
                    return

        if not game_over:
            keys = pygame.key.get_pressed()
            player.move(keys)

            # Spawn musuh
            spawn_timer += 1
            if spawn_timer > 40:
                if random.choice([True, False]):
                    enemies.append(CarEnemy())
                else:
                    enemies.append(AirEnemy())
                spawn_timer = 0

            # Bullet update
            for b in bullets[:]:
                b.update()
                if b.rect.x > WIDTH:
                    bullets.remove(b)

            # Enemy update
            for e in enemies[:]:
                e.update()

                if e.rect.x < 0:
                    enemies.remove(e)

                # TABRAKAN PLAYER
                if player.rect.colliderect(e.rect):
                    enemies.remove(e)
                    lives -= 1
                    if lives <= 0:
                        game_over = True

                        if score > highscore:
                            highscore = score
                            save_highscore(highscore)

                # PELURU KENA MUSUH
                for b in bullets:
                    if e.rect.colliderect(b.rect):
                        bullets.remove(b)
                        if e in enemies:
                            enemies.remove(e)
                        score += 10
                        break

        # ======================
        # DRAW
        # ======================
        player.draw(screen, BLUE)

        for b in bullets:
            b.draw(screen, WHITE)

        for e in enemies:
            e.draw(screen, RED)

        # UI
        screen.blit(font.render(f"Lives: {lives}", True, WHITE), (10,10))
        screen.blit(font.render(f"Score: {score}", True, WHITE), (10,40))
        screen.blit(font.render(f"High Score: {highscore}", True, WHITE), (10,70))  

        if game_over:
            screen.blit(big_font.render("GAME OVER", True, RED), (270,150))
            screen.blit(font.render("Press R to Restart", True, WHITE), (310,220))
            screen.blit(font.render("Press M for Menu", True, WHITE), (312.5,250))
            screen.blit(font.render(f"Score: {score}", True, WHITE), (360,280))
            screen.blit(font.render(f"High Score: {highscore}", True, WHITE), (325,310))

        pygame.display.update()
        clock.tick(60)

    pygame.quit()

while True:
    menu()
    game()