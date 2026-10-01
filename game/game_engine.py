import random
import pygame
from game.rope import Rope
from game.player import Puller


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.rope = Rope(width, height)
        self.player = Puller(90, height // 2, (50, 120, 220), "PLAYER (A/D)")
        self.computer = Puller(width - 90, height // 2, (220, 80, 50), "COMPUTER")

        self.last_key = None
        self.winner = None
        self.game_state = "PLAYING"

        self.computer_pull_cooldown = 180
        self.last_computer_pull = pygame.time.get_ticks()

        self.match_start_time = pygame.time.get_ticks()
        self.match_time = 0.0
        self.sudden_death = False

        self.font_big = pygame.font.SysFont(None, 48)
        self.font_medium = pygame.font.SysFont(None, 32)
        self.font_small = pygame.font.SysFont(None, 26)

    def handle_event(self, event):
        if self.game_state != "PLAYING":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_a, pygame.K_d):
                if event.key != self.last_key:
                    pull_multiplier = 2.0 if self.sudden_death else 1.0
                    self.rope.pull_left(pull_multiplier)
                    self.last_key = event.key
        
    def update(self):
        self.rope.update()

        if self.game_state == "PLAYING":
            now = pygame.time.get_ticks()
            self.match_time = (now - self.match_start_time) / 1000.0
            if self.match_time >= 45.0:
                self.sudden_death = True

            # Player leans backward (left, negative) when pulling; jerked forward (right) when losing ground
            player_target = max(-14.0, min(8.0, self.rope.velocity * 3.5))
            # Computer leans backward (right, positive) when pulling; jerked forward (left) when losing ground
            computer_target = max(-8.0, min(14.0, self.rope.velocity * 3.5))
            self.player.update(player_target)
            self.computer.update(computer_target)
        else:
            if self.winner == "PLAYER":
                self.player.update(-12.0)
                self.computer.update(-12.0)
            elif self.winner == "COMPUTER":
                self.player.update(12.0)
                self.computer.update(12.0)
            return

        # Dynamic computer difficulty: panic surge when player gets close to winning
        cooldown = self.computer_pull_cooldown
        strength_multiplier = 1.0

        danger_threshold = self.rope.left_win_x + 100
        if self.rope.marker_x < danger_threshold:
            danger_factor = (danger_threshold - self.rope.marker_x) / 100.0
            danger_factor = min(max(danger_factor, 0.0), 1.0)
            cooldown = self.computer_pull_cooldown - int(danger_factor * 60)
            strength_multiplier = 1.0 + (danger_factor * 0.25)

        now = pygame.time.get_ticks()
        if now - self.last_computer_pull >= cooldown:
            pull_multiplier = 2.0 if self.sudden_death else 1.0
            computer_variance = random.uniform(0.7, 1.2) * strength_multiplier * pull_multiplier
            self.rope.pull_right(computer_variance)
            self.last_computer_pull = now

        result = self.rope.check_winner()
        if result:
            self.winner = result
            self.game_state = "GAME_OVER"

    def reset(self):
        self.rope.reset()
        self.player.reset()
        self.computer.reset()
        self.last_key = None
        self.winner = None
        self.game_state = "PLAYING"
        self.last_computer_pull = pygame.time.get_ticks()
        self.match_start_time = pygame.time.get_ticks()
        self.match_time = 0.0
        self.sudden_death = False

    def render(self, screen):
        screen.fill((30, 32, 36))

        mud_rect = pygame.Rect(self.width // 2 - 120, self.height // 2 - 80, 240, 160)
        pygame.draw.rect(screen, (45, 38, 30), mud_rect, border_radius=12)

        self.rope.render(screen)
        self.player.render(screen)
        self.computer.render(screen)

        # Match Timer display
        mins = int(self.match_time) // 60
        secs = int(self.match_time) % 60
        timer_text = f"TIME: {mins:02d}:{secs:02d}"
        timer_color = (255, 90, 80) if self.sudden_death else (240, 240, 240)
        timer_surf = self.font_medium.render(timer_text, True, timer_color)
        screen.blit(timer_surf, (self.width // 2 - timer_surf.get_width() // 2, 12))

        # Sudden Death indicator or normal instructions
        if self.sudden_death:
            sd_surf = self.font_small.render(
                "⚡ SUDDEN DEATH: 2X PULL DISTANCE! ⚡", True, (255, 80, 80)
            )
            screen.blit(sd_surf, (self.width // 2 - sd_surf.get_width() // 2, 38))
            inst_y = 62
        else:
            inst_y = 40

        inst_surf = self.font_small.render(
            "Alternate [A] and [D] keys rapidly to pull!", True, (210, 210, 210)
        )
        screen.blit(inst_surf, (self.width // 2 - inst_surf.get_width() // 2, inst_y))

        if self.game_state == "GAME_OVER":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            win_text = f"{self.winner} WINS!"
            color = (80, 220, 80) if self.winner == "PLAYER" else (240, 80, 80)
            text_surf = self.font_big.render(win_text, True, color)
            screen.blit(
                text_surf,
                (self.width // 2 - text_surf.get_width() // 2, self.height // 2 - 60)
            )

            final_time_surf = self.font_small.render(
                f"Final Match Time: {int(self.match_time)}s", True, (200, 200, 200)
            )
            screen.blit(
                final_time_surf,
                (self.width // 2 - final_time_surf.get_width() // 2, self.height // 2 - 10)
            )

            restart_surf = self.font_small.render(
                "Press [R] to Play Again", True, (240, 240, 240)
            )
            screen.blit(
                restart_surf,
                (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 25)
            )