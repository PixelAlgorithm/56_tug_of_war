import math
import pygame


class Rope:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.center_y = screen_height // 2
        self.marker_x = screen_width // 2

        self.left_win_x = 180
        self.right_win_x = screen_width - 180
        self.pull_step = 12

        self.velocity = 0.0
        self.tension = 0.0

    def pull_left(self, strength=1.0):
        self.marker_x -= int(self.pull_step * strength)
        self.velocity -= strength * 1.5
        self.tension = min(1.0, self.tension + 0.35 * strength)

    def pull_right(self, strength=1.0):
        self.marker_x += int(self.pull_step * strength)
        self.velocity += strength * 1.5
        self.tension = min(1.0, self.tension + 0.35 * strength)

    def update(self):
        # Decay momentum and tension smoothly each frame
        self.velocity *= 0.88
        self.tension = max(0.0, self.tension - 0.02)

    def check_winner(self):
        if self.marker_x <= self.left_win_x:
            return "PLAYER"
        if self.marker_x >= self.right_win_x:
            return "COMPUTER"
        return None

    def reset(self):
        self.marker_x = float(self.screen_width // 2)
        self.velocity = 0.0
        self.tension = 0.0

    def render(self, surface):
        start_x = 60
        end_x = self.screen_width - 60
        flag_wave = 0.0

        if self.tension > 0.02:
            time_factor = pygame.time.get_ticks() * 0.03
            span = end_x - start_x
            points = []
            for x in range(start_x, end_x + 1, 16):
                # Sine envelope ensures the ends stay anchored at the pullers
                envelope = math.sin(math.pi * (x - start_x) / span)
                wave = math.sin((x * 0.05) + time_factor) * (self.tension * 3.5) * envelope
                points.append((x, int(self.center_y + wave)))

            if points[-1][0] < end_x:
                points.append((end_x, self.center_y))

            pygame.draw.lines(surface, (180, 140, 90), False, points, 10)

            # Wave offset for the flag at current marker position
            marker_envelope = math.sin(math.pi * (self.marker_x - start_x) / span)
            flag_wave = math.sin((self.marker_x * 0.05) + time_factor) * (self.tension * 3.5) * marker_envelope
        else:
            pygame.draw.line(
                surface,
                (180, 140, 90),
                (start_x, self.center_y),
                (end_x, self.center_y),
                10
            )

        pygame.draw.line(
            surface,
            (50, 200, 50),
            (self.left_win_x, self.center_y - 40),
            (self.left_win_x, self.center_y + 40),
            4
        )
        pygame.draw.line(
            surface,
            (200, 50, 50),
            (self.right_win_x, self.center_y - 40),
            (self.right_win_x, self.center_y + 40),
            4
        )

        pygame.draw.line(
            surface,
            (120, 120, 120),
            (self.screen_width // 2, self.center_y - 20),
            (self.screen_width // 2, self.center_y + 20),
            2
        )

        flag_rect = pygame.Rect(int(self.marker_x) - 12, int(self.center_y + flag_wave) - 24, 24, 48)
        pygame.draw.rect(surface, (230, 40, 40), flag_rect, border_radius=4)
        pygame.draw.rect(surface, (255, 255, 255), flag_rect, width=2, border_radius=4)