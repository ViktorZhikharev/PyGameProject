import pygame, os, sys, random, time, math

size = width, height = 1000, 1000
screen = pygame.display.set_mode(size)

def load_image(name, colorkey=None):
    fullname = os.path.join('images', name)
    if not os.path.isfile(fullname):
        print(f"File '{fullname}' not found")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Kaboom(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__(all_sprites)
        self.image = load_image(image, -1)
        self.image = pygame.transform.rotate(self.image, - 45)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.bottom = height
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.ttl = 10

    def update(self):
        if self.ttl != 0:
            self.ttl -= 1
        else:
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__(all_sprites)
        self.image = load_image(image, -1)
        self.image = pygame.transform.rotate(self.image, - 45)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.bottom = height
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.vector = Vect(315, 1)
        
    def update(self):
        if self.rect.x not in range(width) or self.rect.y not in range(height):
            self.kill()
        k = False
        for i in all_sprites.sprites():
            if pygame.sprite.collide_mask(self, i) and type(i).__name__ == 'Plane':
                k = True
                bang = i
        if not pygame.sprite.collide_mask(self, mountain) and not k:
            self.rect = self.rect.move(*self.vector.tuple())
        else:
            if k:
                bang.kill()
            Kaboom((self.rect.x, self.rect.y), 'kaboom.png')
            self.kill()


class Vect():
    def __init__(self, ang, mod):
        self.ang = ang
        self.mod = mod

    def turn(self, ang):
        self.ang += ang
        self.ang %= 360

    def accel(self, deltamod):
        self.mod += deltamod
    
    def tuple(self):
        return dt * self.mod * math.cos(math.radians(self.ang)), dt * self.mod * math.sin(math.radians(self.ang))


class Background(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__(all_sprites)
        self.image = load_image(image, -1)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.bottom = height


class Plane(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__(all_sprites)
        self.image = load_image(image, -1)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.vector = Vect(180, 0.2)

    def update(self):
        if not pygame.sprite.collide_mask(self, mountain):
            self.rect = self.rect.move(*self.vector.tuple())


if __name__ == '__main__':
    pygame.display.set_caption('PyGameProject')
    pygame.init()
    fc = 0
    clock = pygame.time.Clock()
    all_sprites = pygame.sprite.Group()
    mountain = Background('lvl1.png')
    running = check = True
    shoot = False
    while running:
        screen.fill((66, 170, 255))
        all_sprites.draw(screen)
        all_sprites.update()
        dt = clock.tick(120)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                Plane(event.pos, 'pln1.png')
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    shoot = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    shoot = False
        if shoot and fc % 12 == 0:
            Bullet((420, 530), 'blt1.png')
        fc += 1
        pygame.display.flip()
    pygame.quit()