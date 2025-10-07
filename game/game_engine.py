import pygame
import os
from .paddle import Paddle
from .ball import Ball

WHITE = (255, 255, 255)

class GameEngine:
    def __init__(self, width, height):
        pygame.mixer.init()
        self.width = width
        self.height = height
        self.paddle_width = 10
        self.paddle_height = 100

        # Load sounds
        base_path = os.path.join(os.path.dirname(__file__), "sounds")
        self.sounds = {
            "paddle": pygame.mixer.Sound(os.path.join(base_path, "paddle_hit.wav")),
            "wall": pygame.mixer.Sound(os.path.join(base_path, "wall_bounce.wav")),
        }

        self.sounds["paddle"].set_volume(0.2)
        self.sounds["wall"].set_volume(0.2)

        # Valorant Reaver kill sounds
        self.player_kill_sounds = [
            pygame.mixer.Sound(os.path.join(base_path, "player", f"kill{i}.wav")) for i in range(1, 5)
        ]
        self.player_kill_sounds.append(pygame.mixer.Sound(os.path.join(base_path, "player", "ace.wav")))

        self.ai_kill_sounds = [
            pygame.mixer.Sound(os.path.join(base_path, "ai", f"kill{i}.wav")) for i in range(1, 5)
        ]
        self.ai_kill_sounds.append(pygame.mixer.Sound(os.path.join(base_path, "ai", "ace.wav")))

        # Game objects
        self.player = Paddle(10, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ai = Paddle(width - 20, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ball = Ball(width // 2, height // 2, 7, 7, width, height, self.sounds)

        self.player_score = 0
        self.ai_score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.state = "playing"
        self.winning_score = 5
        self.winner_text = ""

    def handle_input(self):
        keys = pygame.key.get_pressed()

        if self.state == "playing":
            if keys[pygame.K_w]:
                self.player.move(-10, self.height)
            if keys[pygame.K_s]:
                self.player.move(10, self.height)

        elif self.state == "replay_menu":
            if keys[pygame.K_3]:
                self.restart_game(3)
            elif keys[pygame.K_5]:
                self.restart_game(5)
            elif keys[pygame.K_7]:
                self.restart_game(7)
            elif keys[pygame.K_ESCAPE]:
                self.state = "exiting"

    def update(self):
        if self.state != "playing":
            return

        self.ball.move()
        self.ball.check_collision(self.player, self.ai)

        # Scoring events
        if self.ball.x <= 0:
            self.ai_score += 1
            self.play_kill_sound("ai", self.ai_score)
            self.ball.reset()
        elif self.ball.x >= self.width:
            self.player_score += 1
            self.play_kill_sound("player", self.player_score)
            self.ball.reset()

        self.ai.auto_track(self.ball, self.height)
        self.check_game_over()

    def play_kill_sound(self, side, score):
        index = min(score, 5) - 1
        if side == "player":
            self.player_kill_sounds[index].play()
        elif side == "ai":
            self.ai_kill_sounds[index].play()

    def check_game_over(self):
        if self.player_score >= self.winning_score:
            self.state = "game_over"
            self.winner_text = "Player Wins!"
        elif self.ai_score >= self.winning_score:
            self.state = "game_over"
            self.winner_text = "AI Wins!"

    def restart_game(self, best_of):
        self.winning_score = (best_of + 1) // 2
        self.player_score = 0
        self.ai_score = 0
        self.ball.reset()
        self.state = "playing"

    def render(self, screen):
        pygame.draw.rect(screen, WHITE, self.player.rect())
        pygame.draw.rect(screen, WHITE, self.ai.rect())
        pygame.draw.ellipse(screen, WHITE, self.ball.rect())
        pygame.draw.aaline(screen, WHITE, (self.width // 2, 0), (self.width // 2, self.height))

        player_text = self.font.render(str(self.player_score), True, WHITE)
        ai_text = self.font.render(str(self.ai_score), True, WHITE)
        screen.blit(player_text, (self.width // 4, 20))
        screen.blit(ai_text, (self.width * 3 // 4, 20))

        if self.state == "game_over":
            big_font = pygame.font.SysFont("Arial", 60, bold=True)
            win_text = big_font.render(self.winner_text, True, WHITE)
            screen.blit(win_text, (self.width // 2 - win_text.get_width() // 2,
                                   self.height // 2 - win_text.get_height() // 2))
            pygame.display.flip()
            pygame.time.delay(2000)
            self.state = "replay_menu"

        if self.state == "replay_menu":
            menu_font = pygame.font.SysFont("Arial", 40)
            text_lines = [
                "Play Again?",
                "Press 3 for Best of 3",
                "Press 5 for Best of 5",
                "Press 7 for Best of 7",
                "Press ESC to Exit"
            ]
            for i, line in enumerate(text_lines):
                txt_surface = menu_font.render(line, True, WHITE)
                screen.blit(txt_surface, (self.width // 2 - txt_surface.get_width() // 2,
                                          self.height // 2 - 100 + i * 50))
