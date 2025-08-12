try:
    import pygame as pg
    import random

    pg.font.init()
    pg.mixer.init()

    smallFont = pg.font.SysFont("comicsans", 40)
    largeFont = pg.font.SysFont("comicsans", 60)
    loadScreenFonts = pg.font.Font("Melted Monster.ttf", 100)
    loadScreenFonts2 = pg.font.Font("Melted Monster.ttf", 60)

    FPS = 60
    windowWidth = 1000
    windowHeight = 700
    window = pg.display.set_mode((windowWidth, windowHeight))
    pg.display.set_caption("Rise of the Rotten")

    # ---------------- SOUND SETUP ----------------
    playerImpact = pg.mixer.Sound("Roblox Death Sound - OOF  Sound Effect HD - HomeMadeSoundEffects - Bot.mp3")

    winSound = pg.mixer.Sound("Sonder(chosic.com)-[AudioTrimmer.com].mp3")
    looseSound = pg.mixer.Sound("horror-tense-cinematic-fear-score-379388_x80lyKXu.mp3")
    bulletFireSound = pg.mixer.Sound("Gun+Silencer.mp3")
    bulletHitSound = pg.mixer.Sound("Grenade+1.mp3")
    zombieSound = pg.mixer.Sound("Wet_-squishy-sound-of-zombie-footsteps-in-mud.mp3")

    bulletFireSound.set_volume(0.7)
    bulletHitSound.set_volume(0.9)
    zombieSound.set_volume(0.5)

    fire_channel = pg.mixer.Channel(1)
    hit_channel = pg.mixer.Channel(2)
    zombie_channel = pg.mixer.Channel(3)

    zombie_channel.play(zombieSound, loops=-1)

    # ---------------- IMAGE LOADING ----------------
    bgImage3 = pg.transform.scale(pg.image.load("background4.jpg"), (windowWidth, windowHeight))
    bgImage2 = pg.transform.scale(pg.image.load("background3 (1).png"), (windowWidth, windowHeight))
    bgImage = pg.transform.scale(pg.image.load("backgroud image.jpeg"), (windowWidth, windowHeight))
    happyBackground = pg.transform.scale(
        pg.image.load("pngtree-the-people-in-this-crowd-have-some-face-in-pixel-art-picture-image_2624766-_1_.png"),
        (windowWidth, windowHeight))
    sadBackground = pg.transform.scale(pg.image.load("night-town-under-bombing-war-600nw-2200655185_1.png"),
                                       (windowWidth, windowHeight))
    heroImage = pg.transform.scale(pg.image.load("main player.png"), (150, 150))
    heroImageFlipped = pg.transform.scale(pg.image.load("main player flipped.png"), (150, 150))
    zombieImage1 = pg.transform.scale(pg.image.load("Office Zombie.png"), (120, 150))
    zombieImage2 = pg.transform.scale(pg.image.load("Shot_Gun Zombie.png"), (120, 150))
    zombieImage3 = pg.transform.scale(pg.image.load("zombie 1.png"), (120, 150))
    redZombieLaser = pg.image.load("pixel_laser_red.png")
    greenHeroLaser = pg.image.load("pixel_laser_green.png")
    playerZombie = pg.transform.scale(pg.image.load("secondary zombie.png"), (120, 150))

    level = 0
    heroVel = 4
    zombieVel = 2
    heroLaserVel = 15
    zombieLaserVel = 8
    zombieList = []
    waveLength = 3

    clock = pg.time.Clock()


    class Lasers:
        def __init__(self, x, y, img):
            self.xCoordinate = x
            self.yCoordinate = y
            self.laserImage = img
            self.mask = pg.mask.from_surface(self.laserImage)

        def draw(self, win):
            win.blit(self.laserImage, (self.xCoordinate + 50, self.yCoordinate))

        def offScreen(self, maxWidth):
            return self.xCoordinate >= maxWidth or self.xCoordinate <= 0

        def collide(self, surface):
            return collisionDetection(self, surface)

        def move(self, vel):
            self.xCoordinate += vel


    class Player:
        COOLDOWNRATE = 30

        def __init__(self, x, y, health=100):
            self.xCoordinate = x
            self.yCoordinate = y
            self.maxHealth = health
            self.playerImage = None
            self.laserList = []
            self.laserImage = None
            self.cooldownCounter = 0

        def draw(self, win):
            win.blit(self.playerImage, (self.xCoordinate, self.yCoordinate))
            for laser in self.laserList:
                laser.draw(win)

        def shoot(self):
            if self.cooldownCounter <= 0:
                laserObject = Lasers(self.xCoordinate, self.yCoordinate, self.laserImage)
                self.laserList.append(laserObject)
                self.cooldownCounter = 1

        def coolDown(self):
            if self.cooldownCounter >= self.COOLDOWNRATE:
                self.cooldownCounter = 0
            elif self.cooldownCounter > 0:
                self.cooldownCounter += 1

        def moveLaser(self, vel, surface, maxWidth):
            self.coolDown()
            for laser in self.laserList[:]:
                laser.move(vel)
                if laser.offScreen(maxWidth):
                    self.laserList.remove(laser)
                elif laser.collide(surface):
                    self.laserList.remove(laser)
                    surface.maxHealth -= 10
                    if isinstance(surface, Hero):  # Hero is hit
                        playerImpact.play()
                    else:  # Other targets
                        hit_channel.play(bulletHitSound)

        def collide(self, surface):
            return collisionDetection(self, surface)


    class Hero(Player):
        def __init__(self, x, y):
            super().__init__(x, y)
            self.playerImage = heroImage
            self.laserImage = greenHeroLaser
            self.mask = pg.mask.from_surface(self.playerImage)

        def moveLaser(self, vel, surfaceList, maxWidth):
            self.coolDown()
            for laser in self.laserList[:]:
                laser.move(vel)
                if laser.offScreen(maxWidth):
                    self.laserList.remove(laser)
                else:
                    for surface in surfaceList[:]:
                        if laser.collide(surface):
                            if surface in surfaceList:
                                surfaceList.remove(surface)
                            if laser in self.laserList:
                                self.laserList.remove(laser)
                            surface.maxHealth -= 10
                            hit_channel.play(bulletHitSound)
                            break


    objectDisplayed = None


    class Zombies(Player):
        imageMap = {
            "1": zombieImage1,
            "2": zombieImage2,
            "3": zombieImage3
        }

        def __init__(self, x, y, imageNumber):
            super().__init__(x, y)
            self.playerImage = self.imageMap[imageNumber]
            self.laserImage = redZombieLaser
            self.mask = pg.mask.from_surface(self.playerImage)


    heroObject = Hero(20, int(0.55 * windowHeight))
    bg5 = pg.transform.scale(pg.image.load("background5.jpg"), (windowWidth, windowHeight))
    bg6 = pg.transform.scale(pg.image.load("steampunk.jpg"), (windowWidth, windowHeight))


    def draw():
        global level
        window.blit(bgImage, (0, 0))

        if level >= 5:
            window.blit(obj1Image, (170, 10))

        if level >= 5:
            window.blit(bg6, (0, 0))
            window.blit(obj1Image, (170, 10))
            if heroObject.yCoordinate < .60 * windowHeight:
                heroObject.yCoordinate = .60 * windowHeight
            for zombie in zombieList:
                if zombie.yCoordinate < .60 * windowHeight:
                    zombie.yCoordinate = .60 * windowHeight

        if level >= 10:
            # window.blit(obj2Image, (270, 20))
            window.blit(obj1Image, (170, 10))
            window.blit(obj2Image, (270, 20))

        if level >= 2:
            # window.blit(obj2Image, (270, 20))
            window.blit(bg5, (0, 0))
            window.blit(obj2Image, (270, 20))
            window.blit(obj1Image, (170, 10))
            window.blit(obj2Image, (270, 20))

            if heroObject.yCoordinate < .65 * windowHeight:
                heroObject.yCoordinate = .65 * windowHeight
            for zombie in zombieList:
                if zombie.yCoordinate < .65 * windowHeight:
                    zombie.yCoordinate = .65 * windowHeight

        if level > 14:
            window.blit(obj1Image, (170, 10))
            window.blit(obj2Image, (270, 20))
            window.blit(obj3Image, (340, 15))

        levelFont = smallFont.render(f"Level: {level}", 1, "black")
        window.blit(levelFont, (.02 * windowWidth, .02 * windowHeight))
        healthFont = smallFont.render(f"Health: {heroObject.maxHealth}", 1, "black")
        window.blit(healthFont, (.76 * windowWidth, .02 * windowHeight))


        heroObject.draw(window)
        for zombie in zombieList:
            zombie.draw(window)

        if lost:
            window.blit(sadBackground, (0, 0))
            loosingFont = largeFont.render(f"The Human Race Ended With You", 1, "white")
            window.blit(loosingFont, (windowWidth // 2 - 470, windowHeight // 2 - 200))

        if win:
            window.blit(happyBackground, (0, 0))
            winningFont = largeFont.render(f"You Saved The Human Race !  ", 1, "black")
            window.blit(winningFont, (windowWidth // 2 - 430, windowHeight // 2 - 200))

        pg.display.update()


    def collisionDetection(surface1, surface2):
        offsetX = surface2.xCoordinate - surface1.xCoordinate - 10
        offsetY = surface2.yCoordinate - surface1.yCoordinate - 10
        return surface1.mask.overlap(surface2.mask, (offsetX, offsetY)) is not None


    lost = False
    lostCount = 0
    win = False
    winCount = 0
    levelCount = 0

    obj1Image = pg.transform.scale(pg.image.load("images.png"), (100, 70))
    obj2Image = pg.transform.scale(pg.image.load("antivirus chemical.png"), (50, 50))
    obj3Image = pg.transform.scale(pg.image.load("download.png"), (60, 60))
    objectList = [obj1Image, obj2Image]
    objectList2 = []


    def reset_game():
        global level, lost, lostCount, waveLength, win, winCount, levelCount, heroObject, zombieList, objectList2
        level = 0
        waveLength = 3
        lost = False
        lostCount = 0
        win = False
        winCount = 0
        levelCount = 0
        objectList2 = []
        zombieList.clear()
        heroObject = Hero(20, int(0.55 * windowHeight))
        heroObject.maxHealth = 100


    def mainFunc():
        global level, lost, lostCount, waveLength, win, winCount, levelCount
        runGame = True
        while runGame:
            clock.tick(FPS)
            draw()
            if lost:
                heroObject.playerImage = playerZombie

            if len(zombieList) == 0:
                waveLength += 1
                for _ in range(waveLength):
                    X = random.randrange(1500, 2000)
                    Y = random.randrange(round(.57 * windowHeight), windowHeight - zombieImage1.get_height())
                    NUMBER = random.choice(("1", "2", "3"))
                    zombieObject = Zombies(X, Y, NUMBER)
                    zombieList.append(zombieObject)
                level += 1
                levelCount += 1
                if levelCount >= 1:
                    randomvar2 = random.randrange(0, 2)
                    objectList2.append(objectList[randomvar2])
                    levelCount = 0

            if level >= 15:
                win = True
                winCount += 1
            if win:
                if winCount > FPS * 6:
                    runGame = False
                else:
                    continue

            if heroObject.maxHealth <= 0:
                lost = True
                lostCount += 1
            if lost:
                if lostCount > FPS * 6:
                    runGame = False
                else:
                    continue

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()

            keyPressed = pg.key.get_pressed()
            if keyPressed[pg.K_UP] and heroObject.yCoordinate + heroVel > (0.55 * windowHeight):
                heroObject.yCoordinate -= heroVel
            if keyPressed[pg.K_DOWN] and heroObject.yCoordinate + heroVel + heroImage.get_height() < windowHeight:
                heroObject.yCoordinate += heroVel
            if keyPressed[pg.K_LEFT] and heroObject.xCoordinate + heroVel > 0:
                heroObject.xCoordinate -= heroVel
            if keyPressed[pg.K_RIGHT] and heroObject.xCoordinate + heroVel + heroImage.get_width() < windowWidth:
                heroObject.xCoordinate += heroVel
            if keyPressed[pg.K_LCTRL]:
                heroObject.playerImage = heroImageFlipped
            if keyPressed[pg.K_RCTRL]:
                heroObject.playerImage = heroImage
            if keyPressed[pg.K_z]:
                heroObject.shoot()
                fire_channel.play(bulletFireSound)

            for zombie in zombieList[:]:
                zombie.moveLaser(-zombieLaserVel, heroObject, windowWidth)
                randomVar = random.randrange(0, 2 * 60)
                if randomVar == 1:
                    zombie.shoot()
                zombie.xCoordinate -= zombieVel

                if zombie.xCoordinate + zombieImage1.get_width() <= 0:
                    zombieList.remove(zombie)
                if zombie.collide(heroObject):
                    zombieList.remove(zombie)
                    heroObject.maxHealth -= 10

            heroObject.moveLaser(heroLaserVel, zombieList, windowWidth)

        # when game ends -> go back to menu
        frontMenu()


    # tittle = pg.font.SysFont("comicsans", 100)
    tittleImage = pg.transform.scale(pg.image.load("bg.jpg"), (windowWidth, windowHeight))

    instruction = False
    def frontMenu():
        global instruction
        rungame = True
        while rungame:
            # window.fill("black")
            window.blit(tittleImage, (0, 0))
            tittleFont = loadScreenFonts.render(f"Rise Of The Rotten", 1, (134, 0, 0))
            frontFont = loadScreenFonts2.render(f"Press SPACE to start! ", 1 ,"white")
            window.blit(tittleFont, (.07 * windowWidth, .2 * windowHeight))
            window.blit(frontFont, (windowWidth // 2 - 320, .75 * windowHeight))
            # if instruction:
            #     instructionFont = smallFont.render(f"Z = Shoot, Arrow-Keys to Move, CTRL To Flip", 1, (128,128,128))
            #     window.blit(instructionFont, (.08 * windowWidth, .02 * windowHeight))

            pg.display.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    rungame = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        reset_game()
                        mainFunc()
                    # if event.key == pg.K_i:
                    #     instruction = True




    if __name__ == '__main__':
        frontMenu()

except:
    print("Important Note: When downloading the assets and the python file copy of all of the asset files and put it together inside a folder with the python file to run the program")


