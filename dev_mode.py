import pygame
import pickle
from os import path


pygame.init()

fps = 60
tile_size = 25
cols = 20

clock = pygame.time.Clock()

margin = 75
screen_width = tile_size * cols
screen_height = (tile_size * cols) + margin

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Developer Mode')

#icon
programIcon = pygame.image.load('img/black_pawn.png')
pygame.display.set_icon(programIcon)

white = (255, 255, 255)

#load images
bg_img = pygame.image.load('img/pozadi2.png')
bg_img = pygame.transform.scale(bg_img, (screen_width, screen_height - margin))
dirt_img = pygame.image.load('img/kocka2.png')
grass_img = pygame.image.load('img/kocka2.png')
enemy_figure = pygame.image.load('img/white_rook.png')
enemy_figure2 = pygame.image.load('img/white_knight.png')
enemy_figure3 = pygame.image.load('img/white_bishop.png')
platform_x_img = pygame.image.load('img/platform_hor.png')
platform_y_img = pygame.image.load('img/platform_ver.png')
lava_img = pygame.image.load('img/white_pawn.png')
coin_img = pygame.image.load('img/knjig.png')
exit_img = pygame.image.load('img/white_king.png')
save_img = pygame.image.load('img/save_btn.png')   
save_img = pygame.transform.scale(save_img, (50, 50))
load_img = pygame.image.load('img/load_btn.png')
load_img = pygame.transform.scale(load_img, (50, 50))


clicked = False
level = 1


black=(0,0,0)

font = pygame.font.SysFont('Futura', 24)

world_data = []
for row in range(20):
	r = [0] * 20
	world_data.append(r)

for tile in range(0, 20):
	world_data[19][tile] = 1
	world_data[0][tile] = 1
	world_data[tile][0] = 1
	world_data[tile][19] = 1

def tekst(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

def draw_grid():
	for c in range(21):
		
		pygame.draw.line(screen, white, (c * tile_size, 0), (c * tile_size, screen_height - margin))
		
		pygame.draw.line(screen, white, (0, c * tile_size), (screen_width, c * tile_size))


def draw_world():
	for row in range(20):
		for col in range(20):
			if world_data[row][col] > 0:
				if world_data[row][col] == 1:
					
					img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 6:
					
					img = pygame.transform.scale(enemy_figure, (tile_size, int(tile_size * 0.75)))
					screen.blit(img, (col * tile_size, row * tile_size + (tile_size * 0.25)))
				if world_data[row][col] == 2:
					
					img = pygame.transform.scale(platform_x_img, (tile_size, tile_size // 2))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 3:
					
					img = pygame.transform.scale(platform_y_img, (tile_size, tile_size // 2))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 5:
					#pawn
					img = pygame.transform.scale(lava_img, (tile_size, tile_size // 2))
					screen.blit(img, (col * tile_size, row * tile_size + (tile_size // 2)))
				if world_data[row][col] == 4:
					
					img = pygame.transform.scale(coin_img, (tile_size // 2, tile_size // 2))
					screen.blit(img, (col * tile_size + (tile_size // 4), row * tile_size + (tile_size // 4)))
				if world_data[row][col] == 7:
					
					img = pygame.transform.scale(enemy_figure2, (tile_size, int(tile_size * 0.75)))
					screen.blit(img, (col * tile_size, row * tile_size + (tile_size * 0.25)))
				if world_data[row][col] == 8:
					
					img = pygame.transform.scale(enemy_figure3, (tile_size, int(tile_size * 0.75)))
					screen.blit(img, (col * tile_size, row * tile_size + (tile_size * 0.25)))
				if world_data[row][col] == 9:
					
					img = pygame.transform.scale(exit_img, (tile_size, int(tile_size * 1.5)))
					screen.blit(img, (col * tile_size, row * tile_size - (tile_size // 2)))



class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self):
		action = False

		
		pos = pygame.mouse.get_pos()

		
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button
		screen.blit(self.image, (self.rect.x, self.rect.y))

		return action


save_button = Button(screen_width // 2 + 50, screen_height - 80, save_img)
load_button = Button(screen_width // 2 + 150, screen_height - 80, load_img)

#main game loop
run = True
while run:

	clock.tick(fps)

	#draw background
	screen.fill(black)
	screen.blit(bg_img, (0, 0))

	
	if save_button.draw():
		#save level data
		pickle_out = open(f'level{level}_data', 'wb')
		pickle.dump(world_data, pickle_out)
		pickle_out.close()
	if load_button.draw():
		
		if path.exists(f'level{level}_data'):
			pickle_in = open(f'level{level}_data', 'rb')
			world_data = pickle.load(pickle_in)


	
	draw_grid()
	draw_world()


	
	tekst(f'Level: {level}', font, white, tile_size, screen_height - 60)
	tekst('Press UP or DOWN to change level', font, white, tile_size, screen_height - 40)

	#event handler
	for event in pygame.event.get():
		
		if event.type == pygame.QUIT:
			run = False
		
		if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
			clicked = True
			pos = pygame.mouse.get_pos()
			x = pos[0] // tile_size
			y = pos[1] // tile_size
			
			if x < 20 and y < 20:
				#update tile value
				if pygame.mouse.get_pressed()[0] == 1:
					world_data[y][x] += 1
					if world_data[y][x] > 10:
						world_data[y][x] = 0
				elif pygame.mouse.get_pressed()[2] == 1:
					world_data[y][x] -= 1
					if world_data[y][x] < 0:
						world_data[y][x] = 9
		if event.type == pygame.MOUSEBUTTONUP:
			clicked = False
		
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP:
				level += 1
			elif event.key == pygame.K_DOWN and level > 1:
				level -= 1

	
	pygame.display.update()

pygame.quit()

