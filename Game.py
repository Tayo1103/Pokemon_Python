import pygame
from pygame.locals import *
import time
import math
import random
import requests
import io
from urllib.request import urlopen

pygame.init()

game_width = 500
game_height = 500
size = (game_width, game_height)
game = pygame.display.set_mode(size)
pygame.display.set_caption("Pokémon Battle!")
icon = pygame.image.load("C:\\Users\\Acer NITRO 5\\Documents\\Mengoding\\Pokemon Python\\Assets\\Images\\icon.png")
pygame.display.set_icon(icon)

battle_background = pygame.image.load("C:\\Users\\Acer NITRO 5\\Documents\\Mengoding\\Pokemon Python\\Assets\\Images\\Background Battle.png")
battle_background = pygame.transform.scale(battle_background, (game_width, game_height))

black = (0, 0, 0)
gold = (218, 165, 32)
grey = (200, 200, 200)
green = (0, 200, 0)
red = (200, 0, 0)
white = (255, 255, 255)

base_url = "https://pokeapi.co/api/v2"

class Move():
    
    def __init__(self, url):
        
        req = requests.get(url)
        self.json = req.json()
        
        self.name = self.json["name"]
        self.power = self.json["power"]
        self.type = self.json["type"]["name"]

attack_sound = pygame.mixer.Sound("C:\\Users\\Acer NITRO 5\\Documents\\Mengoding\\Pokemon Python\\Assets\\Sounds\\Attack Sound Effect.mp3")
heal_sound = pygame.mixer.Sound("C:\\Users\\Acer NITRO 5\\Documents\\Mengoding\\Pokemon Python\\Assets\\Sounds\\Heal Sound Effect.mp3")

class Pokemon(pygame.sprite.Sprite):
    
    def __init__(self, name, level, x, y):
        
        pygame.sprite.Sprite.__init__(self)
        
        req = requests.get(f"{base_url}/pokemon/{name.lower()}")
        self.json = req.json()
        
        self.name = name
        self.level = level
        
        self.x = x
        self.y = y
        
        self.num_potions = 3
        
        stats = self.json["stats"]
        for stat in stats:
            if stat["stat"]["name"] == "hp":
                self.current_hp = stat["base_stat"] + self.level
                self.max_hp = stat["base_stat"] + self.level
            elif stat["stat"]["name"] == "attack":
                self.attack = stat["base_stat"]
            elif stat["stat"]["name"] == "defense":
                self.defense = stat["base_stat"]
            elif stat['stat']["name"] == "speed":
                self.speed = stat["base_stat"]
                
        self.types = []
        for i in range(len(self.json["types"])):
            type = self.json["types"][i]
            self.types.append(type["type"]["name"])
            
        self.size = 150
        
        self.set_sprite("front_default")
    
    def perform_attack(self, other, move):
        display_message(f"{self.name} used {move.name}!")
        
        time.sleep(1)

        attack_sound.play()

        original_position = (self.x, self.y)

        attack_position = (other.x, other.y)

        for step in range(0, 50, 5):
            self.x = original_position[0] + (attack_position[0] - original_position[0]) * (step / 50)
            self.y = original_position[1] + (attack_position[1] - original_position[1]) * (step / 50)
            game.fill(white)
            game.blit(battle_background, (0, 0))
            self.draw()
            other.draw()
            pygame.display.update()
            pygame.time.delay(20)

        damage = (2 * self.level + 10) / 250 * self.attack / other.defense * move.power
        if move.type in self.types:
            damage *= 1.5
        random_num = random.randint(1, 10000)
        if random_num <= 625:
            damage *= 1.5
        damage = math.floor(damage)

        other.take_damage(damage)

        for step in range(50, 0, -5):
            self.x = original_position[0] + (attack_position[0] - original_position[0]) * (step / 50)
            self.y = original_position[1] + (attack_position[1] - original_position[1]) * (step / 50)
            game.fill(white)
            game.blit(battle_background, (0, 0))
            self.draw()
            other.draw()
            pygame.display.update()
            pygame.time.delay(20)

        self.x = original_position[0]
        self.y = original_position[1]

        if other.current_hp <= 0:
            game_status = "fainted"
        else:
            game_status = "player turn"
        
        time.sleep(1)
        
    def take_damage(self, damage):
        
        self.current_hp -= damage

        if self.current_hp < 0:
            self.current_hp = 0
    
    def use_potion(self):

        if self.num_potions > 0:

            self.current_hp += 20
            if self.current_hp > self.max_hp:
                self.current_hp = self.max_hp

            self.num_potions -= 1

            heal_sound.play()
        
    def set_sprite(self, side):

        image = self.json["sprites"][side]
        image_stream = urlopen(image).read()
        image_file = io.BytesIO(image_stream)
        self.image = pygame.image.load(image_file).convert_alpha()

        scale = self.size / self.image.get_width()
        new_width = self.image.get_width() * scale
        new_height = self.image.get_height() * scale
        self.image = pygame.transform.scale(self.image, (new_width, new_height))
        
    def set_moves(self):
        
        self.moves = []

        for i in range(len(self.json["moves"])):

            versions = self.json["moves"][i]["version_group_details"]
            for j in range(len(versions)):
                
                version = versions[j]

                if version["version_group"]["name"] != "red-blue":
                    continue

                learn_method = version["move_learn_method"]["name"]
                if learn_method != "level-up":
                    continue

                level_learned = version["level_learned_at"]
                if self.level >= level_learned:
                    move = Move(self.json["moves"][i]["move"]["url"])

                    if move.power is not None:
                        self.moves.append(move)

        if len(self.moves) > 4:
            self.moves = random.sample(self.moves, 4)
        
    def draw(self, alpha=255):
        sprite = self.image.copy()

        transparency = (255, 255, 255, alpha)
        sprite.fill(transparency, None, pygame.BLEND_RGBA_MULT)

        game.blit(sprite, (self.x, self.y))

        if game_status == "select pokemon":
            font = pygame.font.Font(pygame.font.get_default_font(), 18)
            name_text = font.render(self.name, True, black)
            name_rect = name_text.get_rect()

            name_rect.centerx = self.x + self.image.get_width() // 2
            name_rect.bottom = self.y - 5

            game.blit(name_text, name_rect)
        
    def draw_hp(self):
        bar_width = 200
        bar_scale = bar_width // self.max_hp

        for i in range(self.max_hp):
            bar = (self.hp_x + bar_scale * i, self.hp_y, bar_scale, 20)
            pygame.draw.rect(game, red, bar)
        
        for i in range(self.current_hp):
            bar = (self.hp_x + bar_scale * i, self.hp_y, bar_scale, 20)
            pygame.draw.rect(game, green, bar)

        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        text = font.render(f"HP: {self.current_hp} / {self.max_hp}", True, black)
        text_rect = text.get_rect()
        text_rect.x = self.hp_x
        text_rect.y = self.hp_y + 30
        game.blit(text, text_rect)

        name_font = pygame.font.Font(pygame.font.get_default_font(), 18)
        name_text = name_font.render(self.name, True, black)
        name_rect = name_text.get_rect()
        name_rect.centerx = self.hp_x + bar_width // 4.5
        name_rect.bottom = self.hp_y - 5
        game.blit(name_text, name_rect)
        
    def get_rect(self):
        
        return Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

def display_message(message):

    pygame.draw.rect(game, white, (10, 350, 480, 140))
    pygame.draw.rect(game, black, (10, 350, 480, 140), 3)

    font = pygame.font.Font(pygame.font.get_default_font(), 20)
    text = font.render(message, True, black)
    text_rect = text.get_rect()
    text_rect.x = 30
    text_rect.y = 410
    game.blit(text, text_rect)
    
    pygame.display.update()

def create_button(width, height, left, top, text_cx, text_cy, label):

    mouse_cursor = pygame.mouse.get_pos()
    
    button = Rect(left, top, width, height)

    if button.collidepoint(mouse_cursor):
        pygame.draw.rect(game, gold, button)
    else:
        pygame.draw.rect(game, white, button)

    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    text = font.render(f'{label}', True, black)
    text_rect = text.get_rect(center=(text_cx, text_cy))
    game.blit(text, text_rect)
    
    return button

menu_soundtrack = pygame.mixer.music.load("C:\\Users\\Acer NITRO 5\\Documents\\Mengoding\\Pokemon Python\\Assets\\Sounds\\Soundtrack Menu.mp3")
pygame.mixer.music.play(-1)

pygame.display.update()

level = 30
venusaur = Pokemon("Venusaur", level, 25, 100)
charizard = Pokemon("Charizard", level, 175, 100)
blastoise = Pokemon("Blastoise", level, 325, 100)
butterfree = Pokemon("Butterfree", level, 25, 300)
beedrill = Pokemon("Beedrill", level, 175, 300)
pidgeot = Pokemon("Pidgeot", level, 325, 300)
pokemons = [venusaur, charizard, blastoise, butterfree, beedrill, pidgeot]

player_pokemon = None
rival_pokemon = None

game_status = "select pokemon"
while game_status != "quit":
    for event in pygame.event.get():
        if event.type == QUIT:
            game_status = "quit"
            
        if event.type == KEYDOWN:
            
            if event.key == K_y:

                venusaur = Pokemon("Venusaur", level, 25, 100)
                charizard = Pokemon("Charizard", level, 175, 100)
                blastoise = Pokemon("Blastoise", level, 325, 100)
                butterfree = Pokemon("Butterfree", level, 25, 300)
                beedrill = Pokemon("Beedrill", level, 175, 300)
                pidgeot = Pokemon("Pidgeot", level, 325, 300)
                pokemons = [venusaur, charizard, blastoise, butterfree, beedrill, pidgeot]
                game_status = "select pokemon"

            elif event.key == K_n:
                game_status = "quit"

        if event.type == MOUSEBUTTONDOWN:
            mouse_click = event.pos

            if game_status == "select pokemon":
                battle_soundtrack = pygame.mixer.music.load("C:\\Users\\Acer NITRO 5\\Documents\\Mengoding\\Pokemon Python\\Assets\\Sounds\\Battle Soundtrack.mp3")
                pygame.mixer.music.play(-1)

                for i in range(len(pokemons)):
                    
                    if pokemons[i].get_rect().collidepoint(mouse_click):

                        player_pokemon = pokemons[i]
                        available_rivals = [pokemon for pokemon in pokemons if pokemon != player_pokemon]
                        rival_pokemon = random.choice(available_rivals)

                        rival_pokemon.level = int(rival_pokemon.level * .75)

                        player_pokemon.hp_x = 275
                        player_pokemon.hp_y = 250
                        rival_pokemon.hp_x = 50
                        rival_pokemon.hp_y = 50
                        
                        game_status = "prebattle"

            elif game_status == "player turn":

                if fight_button.collidepoint(mouse_click):
                    game_status = "player move"

                if potion_button.collidepoint(mouse_click):

                    if player_pokemon.num_potions == 0:
                        display_message("No more potions left")
                        time.sleep(2)
                        game_status = "player move"
                    else:
                        player_pokemon.use_potion()
                        display_message(f"{player_pokemon.name} used potion")
                        time.sleep(2)
                        game_status = "rival turn"

            elif game_status == "player move":

                for i in range(len(move_buttons)):
                    button = move_buttons[i]
                    
                    if button.collidepoint(mouse_click):
                        move = player_pokemon.moves[i]
                        player_pokemon.perform_attack(rival_pokemon, move)

                        if rival_pokemon.current_hp == 0:
                            game_status = "fainted"
                        else:
                            game_status = "rival turn"

    if game_status == "select pokemon":
        
        game.fill(white)
        
        font = pygame.font.Font(pygame.font.get_default_font(), 24)
        text = font.render("Choose Your Pokémon!", True, black)
        text_rect = text.get_rect(center=(game_width // 2, 50))
        game.blit(text, text_rect)

        venusaur.draw()
        charizard.draw()
        blastoise.draw()
        butterfree.draw()
        beedrill.draw()
        pidgeot.draw()
        
        mouse_cursor = pygame.mouse.get_pos()
        for pokemon in pokemons:
            
            if pokemon.get_rect().collidepoint(mouse_cursor):
                pygame.draw.rect(game, black, pokemon.get_rect(), 2)
        
        pygame.display.update()
        
    if game_status == "prebattle":
        
        game.fill(white)
        game.blit(battle_background, (0, 0))
        player_pokemon.draw()
        pygame.display.update()
        
        player_pokemon.set_moves()
        rival_pokemon.set_moves()
        
        player_pokemon.x = -50
        player_pokemon.y = 100
        rival_pokemon.x = 250
        rival_pokemon.y = -50
        
        player_pokemon.size = 300
        rival_pokemon.size = 300
        player_pokemon.set_sprite("back_default")
        rival_pokemon.set_sprite("front_default")
        
        game_status = "start battle"
        
    if game_status == "start battle":
        
        alpha = 0
        while alpha < 255:
            
            game.fill(white)
            game.blit(battle_background, (0, 0))
            rival_pokemon.draw(alpha)
            display_message(f"Rival sent out {rival_pokemon.name}!")
            alpha += .4
            
            pygame.display.update()
            
        time.sleep(1)
        
        alpha = 0
        while alpha < 255:
            
            game.fill(white)
            game.blit(battle_background, (0, 0))
            rival_pokemon.draw()
            player_pokemon.draw(alpha)
            display_message(f"Go {player_pokemon.name}!")
            alpha += .4
            
            pygame.display.update()
        
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()

        if rival_pokemon.speed > player_pokemon.speed:
            game_status = "rival turn"
        else:
            game_status = "player turn"
            
        pygame.display.update()

        time.sleep(1)

    if game_status == "player turn":
        
        game.fill(white)
        game.blit(battle_background, (0, 0))
        player_pokemon.draw()
        rival_pokemon.draw()
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        fight_button = create_button(240, 140, 10, 350, 130, 412, "Fight")
        potion_button = create_button(240, 140, 250, 350, 370, 412, f"Use Potion ({player_pokemon.num_potions})")

        pygame.draw.rect(game, black, (10, 350, 480, 140), 3)
        
        pygame.display.update()

    if game_status == "player move":
        
        game.fill(white)
        game.blit(battle_background, (0, 0))
        player_pokemon.draw()
        rival_pokemon.draw()
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        move_buttons = []
        for i in range(len(player_pokemon.moves)):
            move = player_pokemon.moves[i]
            button_width = 240
            button_height = 70
            left = 10 + i % 2 * button_width
            top = 350 + i // 2 * button_height
            text_center_x = left + 120
            text_center_y = top + 35
            button = create_button(button_width, button_height, left, top, text_center_x, text_center_y, move.name.capitalize())
            move_buttons.append(button)
            
        pygame.draw.rect(game, black, (10, 350, 480, 140), 3)
        
        pygame.display.update()
        
    if game_status == "rival turn":
        
        game.fill(white)
        game.blit(battle_background, (0, 0))
        player_pokemon.draw()
        rival_pokemon.draw()
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        display_message('')
        time.sleep(2)
        
        move = random.choice(rival_pokemon.moves)
        rival_pokemon.perform_attack(player_pokemon, move)
        
        if player_pokemon.current_hp == 0:
            game_status = "fainted"
        else:
            game_status = "player turn"
            
        pygame.display.update()
        
    if game_status == "fainted":
        
        alpha = 255
        while alpha > 0:
            
            game.fill(white)
            game.blit(battle_background, (0, 0))
            player_pokemon.draw_hp()
            rival_pokemon.draw_hp()
            
            if rival_pokemon.current_hp == 0:
                player_pokemon.draw()
                rival_pokemon.draw(alpha)
                display_message(f"{rival_pokemon.name} fainted!")
                win_effect = pygame.mixer.music.load("C:\\Users\\Acer NITRO 5\\Documents\\Mengoding\\Pokemon Python\\Assets\\Sounds\\Win Sound Effect.mp3")
                pygame.mixer.music.play()
            else:
                player_pokemon.draw(alpha)
                rival_pokemon.draw()
                display_message(f"{player_pokemon.name} fainted!")
                lose_effect = pygame.mixer.music.load("C:\\Users\\Acer NITRO 5\\Documents\\Mengoding\\Pokemon Python\\Assets\\Sounds\\Lose Sound Effect.mp3")
                pygame.mixer.music.play()
            alpha -= .4
            
            pygame.display.update()
            
        game_status = "gameover"
        
    if game_status == "gameover":
        
        display_message("Play again (Y/N)?")
        
pygame.quit()
