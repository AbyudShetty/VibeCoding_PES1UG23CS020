import pygame
import os

class Ball:
    def __init__(self, x, y, vel_x, vel_y, screen_width, screen_height, sounds=None):
        self.x = x
        self.y = y
        self.radius = 10
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.sounds = sounds or {}

    def move(self):
        self.x += self.vel_x
        self.y += self.vel_y

        # Bounce off top/bottom walls
        if self.y - self.radius <= 0 or self.y + self.radius >= self.screen_height:
            self.vel_y *= -1
            if "wall" in self.sounds:
                self.sounds["wall"].play()

    def rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)

    def check_collision(self, player, ai):
        ball_rect = self.rect()
        player_rect = player.rect()
        ai_rect = ai.rect()

        # Player paddle hit
        if ball_rect.colliderect(player_rect):
            self.x = player_rect.right + self.radius
            self.vel_x *= -1
            if "paddle" in self.sounds:
                self.sounds["paddle"].play()

        # AI paddle hit
        elif ball_rect.colliderect(ai_rect):
            self.x = ai_rect.left - self.radius
            self.vel_x *= -1
            if "paddle" in self.sounds:
                self.sounds["paddle"].play()

    def reset(self):
        self.x = self.screen_width // 2
        self.y = self.screen_height // 2
        self.vel_x *= -1
        self.vel_y *= -1
