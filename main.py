import pygame, os, sys, random, time, math, copy

size = width, height = 1500, 1000
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
    def __init__(self, pos, image, delay=10):
        super().__init__(all_sprites)
        self.image = load_image(image, -1)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.bottom = height
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.ttl = delay

    def update(self):
        if self.ttl != 0:
            self.ttl -= 1
        else:
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__(all_sprites)
        self.image = load_image(image, -1)
        self.vector = copy.deepcopy(AA_vect)
        self.image = pygame.transform.rotate(self.image, 0 -(self.vector.get_ang()))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.bottom = height
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        
    def update(self):
        if self.rect.x not in range(width) or self.rect.y not in range(height):
            self.kill()
        k = False
        for i in all_sprites.sprites():
            if pygame.sprite.collide_mask(self, i) and issubclass(type(i), Plane):
                k = True
                bang = i
        if not pygame.sprite.collide_mask(self, mountain) and not k:
            self.rect = self.rect.move(*self.vector.tuple())
        else:
            if k:
                bang.kill(True)
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

    def get_ang(self):
        return self.ang


class Background(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__(all_sprites)
        self.image = load_image(image, -1)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.bottom = height


class Plane(pygame.sprite.Sprite):
    def __init__(self, pos, image='pln1.png', spd=0.5):
        super().__init__(all_sprites)
        self.image = load_image(image, -1)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.vector = Vect(180, spd)

    def update(self):
        if self.rect.x not in range(-200, width) or self.rect.y not in range(- 200, height):
            self.kill()
        if not pygame.sprite.collide_mask(self, mountain):
            self.rect = self.rect.move(*self.vector.tuple())

    def kill(self, bul=False):
        if bul:
            Kaboom((self.rect.x, self.rect.y), 'kaboom.png', 10)
        super().kill()


class Bomber(Plane):
    def __init__(self, pos):
        super().__init__(pos, 'bmb.png', 0.3)

    def kill(self, key=False):
        if key:
            Kaboom((self.rect.x, self.rect.y - 50), 'bomberboom.png', 20)
        super().kill()


class Fighter(Plane):
    def __init__(self, pos):
        super().__init__(pos, 'fgt.png', 0.6)

    def kill(self, key=False):
        if key:
            Kaboom((self.rect.x, self.rect.y - 25), 'fighterboom.png', 15)
        super().kill()


class Rocket(Plane):
    def __init__(self, pos):
        super().__init__(pos, 'rct.png', 1)

    def kill(self, key=False):
        if key:
            Kaboom((self.rect.x, self.rect.y - 25), 'bomberboom.png', 20)
        super().kill()


AA_vect = Vect(270, 1.3)


if __name__ == '__main__':
    while True:
        pygame.display.set_caption('PyGameProject')
        pygame.init()
        fc = 0
        lvlcount = 240
        clock = pygame.time.Clock()
        all_sprites = pygame.sprite.Group()
        mountain = Background('lvl1.png')
        running = check = True
        shoot = tl = tr = False
        while running:
            screen.fill((66, 170, 255))
            all_sprites.draw(screen)
            all_sprites.update()
            dt = clock.tick(120)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        shoot = True
                    if event.key == pygame.K_LEFT:
                        tl = True
                    if event.key == pygame.K_RIGHT:
                        tr = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        shoot = False
                    if event.key == pygame.K_LEFT:
                        tl = False
                    if event.key == pygame.K_RIGHT:
                        tr = False
            if shoot and fc % 8 == 0:
                Bullet((420, 530), 'blt1.png')
            if fc < 10000:
                if fc % lvlcount == 0:
                    Bomber((width - 1, random.randint(0, 250)))
            elif fc >= 10000 and fc < 100000:
                if fc % lvlcount == 0:
                    if random.choice([True, False]):
                        Bomber((width - 1, random.randint(0, 250)))
                    else:
                        Fighter((width - 1, random.randint(0, 350)))
            else:
                if fc % lvlcount == 0:
                    chose = random.randint(1,  5)
                    if chose == 1 or chose == 2:
                        Bomber((width - 1, random.randint(0, 250)))
                    elif chose == 3 or chose == 4:
                        Fighter((width - 1, random.randint(0, 350)))
                    else:
                        Rocket((width - 1, random.randint(0, 350)))
            if tl:
                AA_vect.turn(-1)
            if tr:
                AA_vect.turn(1)
            fc += 1
            if fc % 10000 == 0:
                lvlcount //= 2
            pygame.display.flip()
        if not running:
            break
    pygame.quit()