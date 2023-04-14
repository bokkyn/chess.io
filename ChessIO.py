import pygame
from pygame.locals import *
from pygame import mixer
import pickle
import subprocess
from os import path


pygame.init()

tile_size = 37.5

clock = pygame.time.Clock()
fps = 50

#širina i visina screena
width_sc = 750
height_sc = 750

tile_size = 37.5
game_over = 0

main_menu = True
level = 1
max_level = 9
score = 0


font = pygame.font.SysFont("pressstartregular", 50)

font_score = pygame.font.SysFont("pressstartregular", 30)

screen = pygame.display.set_mode((width_sc, height_sc))
pygame.display.set_caption('Chess.io')


programIcon = pygame.image.load('img/black_pawn.png')

pygame.display.set_icon(programIcon)

#učitat pozadinske slike
bg_img = pygame.image.load('img/pozadi2.png')
restart_img = pygame.image.load('img/restart_btn.png')
restart_img = pygame.transform.scale(restart_img, (100, 75))

start_img = pygame.image.load('img/start_btn.png')
figura_img = pygame.image.load('img/start_btn.png')

pobjeda_img = pygame.image.load('img/sahmat bili.png')
poraz_img = pygame.image.load('img/sahmat crni.png')
exit_img = pygame.image.load('img/exit_btn.png')
dev_img=pygame.image.load('img/dev_mode.png')

#boje (za font)
white = (255, 255, 255)
blue = (0, 0, 255)
red=(255,0,0)
black=(0,0,0)

#zvukovi #############################################################################################
pygame.mixer.music.load('img/sounds.mp3')
pygame.mixer.music.play(-1, 0.0, 5000)
coin_fx = pygame.mixer.Sound('img/coin-collect.mp3')
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('img/jumpp.mp3')
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('img/over.mp3')
game_over_fx.set_volume(0.5)



def tekst(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))




class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.clicked = False
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		

	def draw(self):
		action = False

		
		pozicija = pygame.mouse.get_pos()

		
		if self.rect.collidepoint(pozicija):
			key = pygame.key.get_pressed()
			if (pygame.mouse.get_pressed()[0] == 1 and self.clicked == False) or key[pygame.K_SPACE]:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		screen.blit(self.image, self.rect)

		return action


class Player():
	def __init__(self, x, y):
		self.reset(x, y)

	def update(self, game_over):
		x_os = 0
		y_os = 0
		walk_cooldown = 50
		col_thresh = 20

		if game_over == 0:
			#get keypresses
			key = pygame.key.get_pressed()
			if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
				jump_fx.play()
				self.vel_y = -15                   #koliko visoko skaće
				self.jumped = True
			if key[pygame.K_SPACE] == False:
				self.jumped = False
			if key[pygame.K_LEFT]:
				x_os -= 5                            #kolko ide u koju stranu
				self.counter += 1
				self.direction = -1
			if key[pygame.K_RIGHT]:
				x_os += 5
				self.counter += 1
				self.direction = 1
			if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
				self.counter = 0
				self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]


			
			if self.counter > walk_cooldown:
				self.counter = 0	
				self.index += 1
				if self.index >= len(self.images_right):
					self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]


			#add gravity
			self.vel_y += 1                      #koliko je jaka gravitacija
			if self.vel_y > 10:
				self.vel_y = 10                  #max  koliko je ubrzanje
			y_os += self.vel_y

			
			self.in_air = True
			for tile in world.tile_list:
				#u x smjeru
				if tile[1].colliderect(self.rect.x + x_os, self.rect.y, self.width, self.height):
					x_os = 0
				#u y smjeru
				if tile[1].colliderect(self.rect.x, self.rect.y + y_os, self.width, self.height):
					#skok
					if self.vel_y < 0:
						y_os = tile[1].bottom - self.rect.top
						self.vel_y = 0
					#padanje
					elif self.vel_y >= 0:
						y_os = tile[1].top - self.rect.bottom
						self.vel_y = 0
						self.in_air = False


			#ako se sudari s neprijateljem igra je gotova
			if pygame.sprite.spritecollide(self, enemy_group, False):
				game_over = -1
				game_over_fx.play()  #zvuk za kraj

			#dodir s pijunima
			if pygame.sprite.spritecollide(self, pawn_group, False):
				game_over = -1
				game_over_fx.play()

			#izlaz
			if pygame.sprite.spritecollide(self, next_group, False):
				game_over = 1

####################################################################################Vidi ovaj cili dio
			for platform in platform_group:
				if platform.rect.colliderect(self.rect.x + x_os, self.rect.y, self.width, self.height):
					x_os = 0
				if platform.rect.colliderect(self.rect.x, self.rect.y + y_os, self.width, self.height):
					if abs((self.rect.top + y_os) - platform.rect.bottom) < col_thresh:
						self.vel_y = 0
						y_os = platform.rect.bottom - self.rect.top
					elif abs((self.rect.bottom + y_os) - platform.rect.top) < col_thresh:
						self.rect.bottom = platform.rect.top - 1
						self.in_air = False
						y_os = 0
					if platform.move_x != 0:
						self.rect.x += platform.move_direction


			
			self.rect.x += x_os
			self.rect.y += y_os



		elif game_over == -1:
			
			#poraz crnoga-poraz u igri
			picture_poraz = pygame.image.load("img/sahmat crni.png")
			picture_poraz = pygame.transform.scale(picture_poraz, (275, 275))
			screen.blit(picture_poraz, ((width_sc // 2)-130, (height_sc // 2)-100))
			tekst('GAME OVER!', font, black, (width_sc // 2) - 235, height_sc // 2-100)


		#nacrta pijuna
		screen.blit(self.image, self.rect)
		return game_over


	def reset(self, x, y):
		self.images_right = []
		self.images_left = []
		self.index = 0
		self.counter = 0
		for num in range(1, 5):
			img_right = pygame.image.load(f'img/black_pawn.png')
			img_right = pygame.transform.scale(img_right, (30, 60))
			img_left = pygame.transform.flip(img_right, True, False)
			self.images_right.append(img_right)
			self.images_left.append(img_left)
		self.image = self.images_right[self.index]
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.vel_y = 0
		self.jumped = False
		self.direction = 0
		self.in_air = True



class World():
	def __init__(self, data):
		self.tile_list = []

		#slike
		tlo_img = pygame.image.load('img/kocka2.png')
		

		redovi = 0
		for row in data:
			stupci = 0
			for tile in row:
				if tile == 1:
					img = pygame.transform.scale(tlo_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = stupci * tile_size
					img_rect.y = redovi * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 6:
					enemy_figure = Enemy(stupci * tile_size, redovi * tile_size)  #+doli, gori
					enemy_group.add(enemy_figure)
				if tile == 2:
					platform = Platform(stupci * tile_size, redovi * tile_size, 1, 0)
					platform_group.add(platform)
				if tile == 3:
					platform = Platform(stupci * tile_size, redovi * tile_size, 0, 1)
					platform_group.add(platform)
				if tile == 5:
					lava = Pawn(stupci * tile_size, redovi * tile_size)
					pawn_group.add(lava)
				if tile == 4:
					coin = Knjiga(stupci * tile_size + (tile_size // 2), redovi * tile_size + (tile_size // 2))
					coin_group.add(coin)
				if tile == 8:
					enemy_figure3 = Enemy3(stupci * tile_size, redovi * tile_size)
					enemy_group.add(enemy_figure3)
				if tile == 7:
					enemy_figure2 = Enemy2(stupci * tile_size, redovi * tile_size)
					enemy_group.add(enemy_figure2)
				if tile == 9:
					exit = Exit(stupci * tile_size, redovi * tile_size - (tile_size // 2))
					next_group.add(exit)
				stupci += 1
			redovi += 1


	def draw(self):
		for tile in self.tile_list:
			screen.blit(tile[0], tile[1])



class Enemy(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('img/white_rook.png')
		self.rect = self.image.get_rect()
		self.image = pygame.transform.scale(self.image, (tile_size, tile_size))
		self.rect.x = x  #kolko ide u stranu
		self.rect.y = y
		self.move_direction = 1  #brzina mjenjanja, al idu i dalje
		self.move_counter = 0

	def update(self):
		self.rect.x += self.move_direction   #u kojem će smjeru ići
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1
			
class Enemy2(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('img/white_knight.png')
		self.rect = self.image.get_rect()
		self.image = pygame.transform.scale(self.image, (tile_size, tile_size))
		self.rect.x = x
		self.rect.y = y
		self.move_direction = 1  #brzina mjenjanja, al idu i dalje
		self.move_counter = 0

	def update(self):
		self.rect.y += self.move_direction     #u kojem će smjeru ići
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1
			
class Enemy3(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('img/white_bishop.png')
		self.rect = self.image.get_rect()
		self.image = pygame.transform.scale(self.image, (tile_size, tile_size))
		self.rect.x = x
		self.rect.y = y
		self.move_direction = 1  #brzina mjenjanja, al idu i dalje
		self.move_counter = 0

	def update(self):
		self.rect.y += self.move_direction     #u kojem će smjeru ići
		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1

class Knjiga(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/knjig.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size))
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)

class Platform(pygame.sprite.Sprite):
	def __init__(self, x, y, move_x, move_y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/platform.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_counter = 0
		self.move_direction = 1
		self.move_x = move_x
		self.move_y = move_y


	def update(self):
		self.rect.x += self.move_direction * self.move_x
		self.rect.y += self.move_direction * self.move_y
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1


tekst(f'Level: {level}', font, white, tile_size, height_sc - 60)


class Pawn(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/white_pawn.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y



#reset
def reset_level(level):
	player.reset(100, height_sc - 130)
	enemy_group.empty()
	platform_group.empty()
	coin_group.empty()
	pawn_group.empty()
	next_group.empty()

	################################################################
	if path.exists(f'level{level}_data'):
		pickle_in = open(f'level{level}_data', 'rb')
		world_data = pickle.load(pickle_in)
	world = World(world_data)
	return world

class Exit(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/white_king.png')
		self.image = pygame.transform.scale(img, (tile_size, int(tile_size)+15))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y



player = Player(100, height_sc - 130)

enemy_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
pawn_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
next_group = pygame.sprite.Group()

#load in level data and create world  #####################učitavanje svijetova
if path.exists(f'level{level}_data'):
	pickle_in = open(f'level{level}_data', 'rb')
	world_data = pickle.load(pickle_in)
world = World(world_data)


#create buttons
restart_button = Button(width_sc // 2 - 50, height_sc // 2 + 100, restart_img)
start_button = Button(width_sc // 2 - 350, (height_sc // 2)-100, start_img)
exit_button = Button(width_sc // 2 + 100, (height_sc // 2)-100, exit_img)
figura_button=Button(width_sc // 2-125, (height_sc // 2)+100, dev_img)


run = True
while run:

	clock.tick(fps)

	screen.blit(bg_img, (0, 0))
	

	if main_menu == True:
	
		key = pygame.key.get_pressed()
		if exit_button.draw():
			run = False
		if start_button.draw() or key[pygame.K_SPACE]:
			main_menu = False
		if figura_button.draw():
			main_menu = True
			subprocess.run(["python","dev_mode.py"])
	else:
		world.draw()

		if game_over == 0:
			enemy_group.update()
			platform_group.update()
			if pygame.sprite.spritecollide(player, coin_group, True):
				score += 1
				coin_fx.play()
			tekst( str(score), font_score, black, tile_size - 15, 15)
		
		enemy_group.draw(screen)
		platform_group.draw(screen)
		pawn_group.draw(screen)
		coin_group.draw(screen)
		next_group.draw(screen)

		game_over = player.update(game_over)

		#ako je izgubio
		if game_over == -1:
			key = pygame.key.get_pressed()
			if restart_button.draw() or key[pygame.K_SPACE]:
				world_data = []
				world = reset_level(level)
				game_over = 0
				score = 0

		#ako je prošao dalje
		if game_over == 1:
			
			level += 1
			if level <= max_level:
				#reset level
				world_data = []
				world = reset_level(level)
				game_over = 0
			else:
				picture_pobjeda = pygame.image.load("img/sahmat bili.png")
				picture_pobjeda = pygame.transform.scale(picture_pobjeda, (275, 275))
				screen.blit(picture_pobjeda, ((width_sc // 2)-130, (height_sc // 2)-100))
				tekst('YOU WIN!', font, red, (width_sc // 2) - 190, height_sc // 2-100)
				key = pygame.key.get_pressed()
				if restart_button.draw() or key[pygame.K_SPACE]:
					level = 1
					world_data = []
					world = reset_level(level)
					game_over = 0
					score = 0

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

	pygame.display.update()

pygame.quit()