import pygame


class Puller:
    """Represents a puller character anchor on either side of the rope."""

    def __init__(self, x, y, color, label):
        self.x = x
        self.y = y
        self.color = color
        self.label = label
        self.font = pygame.font.SysFont(None, 24)
        self.lean_offset = 0.0
        self.target_lean = 0.0

    def update(self, target_lean=None):
        """Smoothly interpolate leaning offset toward target."""
        if target_lean is not None:
            self.target_lean = target_lean
        self.lean_offset += (self.target_lean - self.lean_offset) * 0.2

    def reset(self):
        """Reset leaning state."""
        self.lean_offset = 0.0
        self.target_lean = 0.0

    def render(self, surface):
        """Draw avatar with leaning animation and label."""
        lean = int(self.lean_offset)

        # Body - anchored at feet (bottom), tilting at torso (top)
        top_left = (self.x - 20 + lean, self.y - 35)
        top_right = (self.x + 20 + lean, self.y - 35)
        bottom_right = (self.x + 20, self.y + 35)
        bottom_left = (self.x - 20, self.y + 35)
        pygame.draw.polygon(surface, self.color, [top_left, top_right, bottom_right, bottom_left])

        # Head - tilts along with upper body
        pygame.draw.circle(surface, (240, 210, 180), (self.x + lean, self.y - 50), 16)

        # Name / control tag
        label_surf = self.font.render(self.label, True, (240, 240, 240))
        surface.blit(label_surf, (self.x - label_surf.get_width() // 2, self.y + 45))