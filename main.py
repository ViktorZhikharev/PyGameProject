import pygame, os, sys, random, time, datetime, math, copy

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

def stat_update():
    global maxscore, playtime
    fl = open('records.txt', 'r')
    li = [i.strip() for i in fl]
    if maxscore > int(li[0]):
        li[0] = maxscore
    if playtime.total_seconds() > float(li[1]):
        li[1] = playtime.total_seconds()
    fl.close()
    fr = open('records.txt', 'w')
    fr.write(str(li[0]) + '\n')
    fr.write(str(li[1]))
    fr.close()


class PGlist:
    def __init__(self, height):
        self.width = 1
        self.height = height
        self.board = [[0] * 1 for _ in range(height)]
        self.left = 10
        self.top = 10
        self.cell_size = 30

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, canvas):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j] == 0:
                    pygame.draw.rect(canvas, pygame.Color('white'), (self.left + j * self.cell_size[0], self.top + i * self.cell_size[1], self.cell_size[0], self.cell_size[1]), 1)
                elif self.board[i][j] == 1:
                    pygame.draw.rect(canvas, pygame.Color('white'), (self.left + j * self.cell_size[0], self.top + i * self.cell_size[1], self.cell_size[0], self.cell_size[1]), 0)

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        self.on_click(cell)

    def get_cell(self, mouse_pos):
        if (mouse_pos[1] not in range(self.left, self.left + self.cell_size[1] * len(self.board)) or
            mouse_pos[0] not in range(self.top, self.top + self.cell_size[0] * len(self.board[0]))):
            return None
        else:
            return (mouse_pos[1] - self.left) // self.cell_size[1], (mouse_pos[0] - self.top) // self.cell_size[0]

    def on_click(self, cell_coords):
        global selector, check, finexit
        if cell_coords == (0, 0):
            selector = 100
            check = False
        elif cell_coords == (4, 0):
            selector = 101
            check = False
        elif cell_coords == (5, 0):
            finexit = True
            check = False
        else:
            selector = cell_coords[0]
            check = False


class Kaboom(pygame.sprite.Sprite):
    def __init__(self, pos, image, delay=10):
        super().__init__(all_sprites)
        self.image = load_image(image)
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
        self.border = False
        
    def update(self):
        if self.rect.x not in range(width) or self.rect.y not in range(height):
            self.border = True
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
            self.kill()

    def kill(self):
        if not self.border:
            Kaboom((self.rect.x, self.rect.y), 'kaboom.png')
        super().kill()


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
        self.image = load_image(image)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.vector = Vect(180, spd)

    def update(self):
        if self.rect.x not in range(-200, width) or self.rect.y not in range(- 200, height):
            self.kill()
        self.rect = self.rect.move(*self.vector.tuple())

    def kill(self, bul=False):
        if bul:
            Kaboom((self.rect.x, self.rect.y), 'kaboom.png', 10)
        super().kill()


class Bomber(Plane):
    def __init__(self, pos):
        super().__init__(pos, 'bmb.png', 0.3)

    def kill(self, key=False):
        global score, ammo
        if key:
            score += 100
            ammo += 10
            Kaboom((self.rect.x, self.rect.y - 50), 'bomberboom.png', 20)
        else:
            score -= 100
        super().kill()


class Fighter(Plane):
    def __init__(self, pos):
        super().__init__(pos, 'fgt.png', 0.6)

    def kill(self, key=False):
        global score, ammo
        if key:
            score += 50
            ammo += 15
            Kaboom((self.rect.x, self.rect.y - 25), 'fighterboom.png', 15)
        else:
            score -= 50
        super().kill()


class Rocket(Plane):
    def __init__(self, pos):
        super().__init__(pos, 'rct.png', 1)

    def kill(self, key=False):
        global score, ammo
        if key:
            score += 150
            ammo += 45
            Kaboom((self.rect.x, self.rect.y - 25), 'bomberboom.png', 20)
        else:
            score -= 150
        super().kill()


class Cloud(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(load_image('cloud.png'), (random.randint(100, 200), random.randint(50, 100)))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.bottom = height
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.vector = Vect(180, 0.2)

    def update(self):
        self.rect = self.rect.move(*self.vector.tuple())
        if self.rect.x not in range(-200, width):
            self.kill()


class NukeBullet(Bullet):
    def kill(self):
        if not self.border:
            NukeKaboom((self.rect.x - 75, self.rect.y - 75), 'nukekaboom.png', 60)
        super().kill()


class NukeKaboom(Kaboom):
    def update(self):
        k = False
        for i in all_sprites.sprites():
            if pygame.sprite.collide_mask(self, i) and issubclass(type(i), Plane):
                k = True
                bang = i
        else:
            if k:
                bang.kill(True)
        if self.ttl != 0:
                self.ttl -= 1
        else:
            self.kill()


class Bunker(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__(all_sprites)
        self.image = load_image(image)
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.bottom = height
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.border = False


AA_vect = Vect(270, 1.3)


if __name__ == '__main__':
    pygame.display.set_caption('PyGameProject')
    pygame.init()
    selector = 0
    finexit = False
    while True: 
        all_sprites = pygame.sprite.Group()
        if selector == 0:
            board = PGlist(6)
            board.set_view(100, 100, (500, 100))
            Background('mainmenu.png')
            running = check = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        finexit = True
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        board.get_click(event.pos)
                if not check:
                    running = False
                screen.fill((0, 0, 0))
                all_sprites.update()
                all_sprites.draw(screen)
                board.render(screen)
                font = pygame.font.Font(None, 50)
                text1 = font.render('Green Mountains', True, (255, 255, 255))
                text1_x = 350 - text1.get_width() // 2
                text1_y = 250 - text1.get_height() // 2
                text1_w = text1.get_width()
                text1_h = text1.get_height()
                screen.blit(text1, (text1_x, text1_y))
                text2 = font.render('Help', True, (255, 255, 255))
                text2_x = 350 - text2.get_width() // 2
                text2_y = 150 - text2.get_height() // 2
                text2_w = text2.get_width()
                text2_h = text2.get_height()
                screen.blit(text2, (text2_x, text2_y))
                text3 = font.render('Records', True, (255, 255, 255))
                text3_x = 350 - text3.get_width() // 2
                text3_y = 550 - text3.get_height() // 2
                text3_w = text3.get_width()
                text3_h = text3.get_height()
                screen.blit(text3, (text3_x, text3_y))
                text4 = font.render('Exit', True, (255, 255, 255))
                text4_x = 350 - text4.get_width() // 2
                text4_y = 650 - text4.get_height() // 2
                text4_w = text4.get_width()
                text4_h = text4.get_height()
                screen.blit(text4, (text4_x, text4_y))
                text5 = font.render('Battleship', True, (255, 255, 255))
                text5_x = 350 - text5.get_width() // 2
                text5_y = 350 - text5.get_height() // 2
                text5_w = text5.get_width()
                text5_h = text5.get_height()
                screen.blit(text5, (text5_x, text5_y))
                text6 = font.render('Megapolis', True, (255, 255, 255))
                text6_x = 350 - text6.get_width() // 2
                text6_y = 450 - text6.get_height() // 2
                text6_w = text6.get_width()
                text6_h = text6.get_height()
                screen.blit(text6, (text6_x, text6_y))
                pygame.display.flip()
        if selector == 1:
            aa_pos = (420, 530)
            Bunker((aa_pos[0] - 20, aa_pos[1] - 5), 'bunker.png')
            mountain = Background('lvl1.png')
        if selector == 2:
            aa_pos = (700, 569)
            mountain = Background('lvl2.png')
        if selector == 3:
            aa_pos = (920, 550)
            Bunker((aa_pos[0] - 20, aa_pos[1] - 5), 'bunker.png')
            mountain = Background('lvl3.png')
        elif selector == 100:
            Background('help.png')
            screen.fill((0, 0, 0))
            all_sprites.draw(screen)
            pygame.display.flip()
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        finexit = True
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                            selector = 0
                time.sleep(0.01)
        elif selector == 101:
            f = open('records.txt', 'r')
            font = pygame.font.Font(None, 100)
            screen.fill((0, 0, 0))
            helptext = [i.strip() for i in f]
            stext = font.render('best score: ' + helptext[0], True, (0, 255, 255))
            stext_x = width // 2 - stext.get_width() // 2
            stext_y = height // 2 - stext.get_height() // 2
            stext_w = stext.get_width()
            stext_h = stext.get_height()
            screen.blit(stext, (stext_x, stext_y))
            stext = font.render('best time: ' + str(datetime.timedelta(microseconds=(float(helptext[1]) * (10 ** 6)))), True, (0, 255, 255))
            stext_x = width // 2 - stext.get_width() // 2
            stext_y = height // 2 - stext.get_height() // 2 + 150
            stext_w = stext.get_width()
            stext_h = stext.get_height()
            screen.blit(stext, (stext_x, stext_y))
            pygame.display.flip()
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        finexit = True
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                            selector = 0
                time.sleep(0.01)
        if selector in range(1, 100):
            starttime = datetime.datetime.now()
            fc = 0
            score = 0
            maxscore = 0
            ammo = 100
            lvlcount = 960
            running = check = check2 = True
            shoot = tl = tr = False
            spd = 12
            clock = pygame.time.Clock()
            while running:
                if score < 0:
                    if check2:
                        check2 = False
                        fintime = datetime.datetime.now()
                        playtime = fintime - starttime
                        stat_update()
                    screen.fill((0, 0, 0))
                    font = pygame.font.Font(None, 150)
                    stext = font.render('Game Over', True, (0, 255, 255))
                    stext_x = width // 2 - stext.get_width() // 2
                    stext_y = height // 2 - stext.get_height() // 2
                    stext_w = stext.get_width()
                    stext_h = stext.get_height()
                    screen.blit(stext, (stext_x, stext_y))
                    font = pygame.font.Font(None, 50)
                    stext = font.render('Your time: ' + str(playtime), True, (0, 255, 255))
                    stext_x = width // 2 - stext.get_width() // 2
                    stext_y = height // 2 - stext.get_height() // 2 + 150
                    stext_w = stext.get_width()
                    stext_h = stext.get_height()
                    screen.blit(stext, (stext_x, stext_y))
                    stext = font.render('Max score: ' + str(maxscore), True, (0, 255, 255))
                    stext_x = width // 2 - stext.get_width() // 2
                    stext_y = height // 2 - stext.get_height() // 2 + 200
                    stext_w = stext.get_width()
                    stext_h = stext.get_height()
                    screen.blit(stext, (stext_x, stext_y))
                    stext = font.render('Press [escape] to go to menu', True, (0, 255, 255))
                    stext_x = width // 2 - stext.get_width() // 2
                    stext_y = height // 2 - stext.get_height() // 2 + 250
                    stext_w = stext.get_width()
                    stext_h = stext.get_height()
                    screen.blit(stext, (stext_x, stext_y))
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                            finexit = True
                        if event.type == pygame.KEYUP:
                            if event.key == pygame.K_ESCAPE:
                                running = False
                                selector = 0
                    pygame.display.flip()
                else:
                    screen.fill((66, 170, 255))
                    all_sprites.draw(screen)
                    all_sprites.update()
                    font = pygame.font.Font(None, 50)
                    stext = font.render('Score: ' + str(score), True, (100, 255, 100))
                    stext_x = width - 150 - stext.get_width() // 2
                    stext_y = 50 - stext.get_height() // 2
                    stext_w = stext.get_width()
                    stext_h = stext.get_height()
                    screen.blit(stext, (stext_x, stext_y))
                    atext = font.render('Ammo: ' + str(ammo), True, (100, 255, 100))
                    atext_x = 150 - atext.get_width() // 2
                    atext_y = 50 - atext.get_height() // 2
                    atext_w = atext.get_width()
                    atext_h = atext.get_height()
                    screen.blit(atext, (atext_x, atext_y))
                    ltext = font.render('level: ' + str(fc // 10000 + 1), True, (100, 255, 100))
                    ltext_x = width // 2 - ltext.get_width() // 2
                    ltext_y = 50 - ltext.get_height() // 2
                    ltext_w = ltext.get_width()
                    ltext_h = ltext.get_height()
                    screen.blit(ltext, (ltext_x, ltext_y))
                    dt = clock.tick(120)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                            finexit = True
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
                            if event.key == pygame.K_ESCAPE:
                                score = -100
                    if shoot and fc % spd == 0 and ammo > 0:
                        if fc < 50000:
                            ammo -= 1
                            Bullet(aa_pos, 'blt1.png')
                            Kaboom(aa_pos, 'kaboom.png', 5)
                        if fc > 50000:
                            ammo -= 25
                            NukeBullet(aa_pos, 'blt1.png')
                            Kaboom(aa_pos, 'kaboom.png', 5) 
                    if fc < 10000:
                        if fc % lvlcount == 0:
                            Bomber((width - 1, random.randint(80, 250)))
                    elif fc >= 10000 and fc < 100000:
                        if lvlcount == 0:
                            lvlcount = 1
                        if fc % lvlcount == 0:
                            if random.choice([True, False]):
                                Bomber((width - 1, random.randint(80, 250)))
                            else:
                                Fighter((width - 1, random.randint(80, 350)))
                    else:
                        if fc % lvlcount == 0:
                            chose = random.randint(1,  5)
                            if chose == 1 or chose == 2:
                                Bomber((width - 1, random.randint(80, 250)))
                            elif chose == 3 or chose == 4:
                                Fighter((width - 1, random.randint(80, 350)))
                            else:
                                Rocket((width - 1, random.randint(80, 350)))
                    if tl:
                        AA_vect.turn(-1)
                    if tr:
                        AA_vect.turn(1)
                    fc += 1
                    if fc % 10000 == 0:
                        lvlcount //= 2
                    if not random.randint(0, 1000):
                        Cloud((1480, random.randint(80, 250)))
                    pygame.display.flip()
                    if fc == 20000:
                        spd = 8
                    if fc == 30000:
                        spd = 4
                    if fc == 50000:
                        spd = 24
                    if maxscore <= score:
                        maxscore = score
        if finexit:
            break
    pygame.quit()