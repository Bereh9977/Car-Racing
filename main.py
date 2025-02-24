import pygame
from game_objects import Cars, Bots, Roads, Obstacles, Finish, Score
from menus import Menu, MapsMenu, CarsMenu, ModesMenu
from music import overlay_music_in_loop, next_track, mute_music, music_playing
from utilities import scale_image

pygame.init()

class GameSys:
    def __init__(self):
        self.running = True
        self.aspect_ratio = (1920, 1080)
        self.screen = pygame.display.set_mode(self.aspect_ratio)
        pygame.display.set_caption('Car Racing')
        self.background = pygame.image.load('img/garage_blur.png')
        self.car = Cars(400, 997, 0, 0, 0, 'img/car1.png', 'wasd')
        self.bot = Bots(400, 992, 0, 0, 0, [])
        self.menu = Menu(800, 450)
        self.roads = Roads('img/winter.jpg', 0)
        self.obs = Obstacles(0, 0, 'img/snowflake.png','img/banana.png', 'img/sand.png')
        self.road_contour = pygame.image.load('img/winter_edge.png')
        self.road_contour_mask = pygame.mask.from_surface(self.road_contour)
        self.countdown_images = [
            pygame.image.load('img/3.png'),
            scale_image(pygame.image.load('img/2.png'), 2),
            pygame.image.load('img/1.png'),
            pygame.image.load('img/GO.png')
        ]
        self.in_menu = True
        self.score = Score("img/coin.png")
        self.maps_page = MapsMenu(80, 100, self.score)
        self.cars_page = CarsMenu(90, 100, self.score)
        self.modes_page = ModesMenu(100, 100)
        self.choosing_map = False
        self.choosing_car = False
        self.choosing_mode = False
        self.map_choice = '0'
        self.mode_choice = '0'
        self.car1 = Cars(400, 997, 0, 0.5, 0, 'img/car5.png', 'wasd')
        self.car2 = Cars(500, 997, 0, 0.5, 0, 'img/car5.png', 'arrows')
        self.pause_font = pygame.font.Font("fonts/AveriaSansLibre-Bold.ttf", 36)
        self.pause_text = self.pause_font.render('Paused', True, (255, 255, 255))
        self.pause_rect = self.pause_text.get_rect(center=(self.aspect_ratio[0]//2 - 15, self.aspect_ratio[1]//2))      
        
    def run(self):
        new_game = True
        # Змінна для регулювання кількості кадрів на секунду
        clock = pygame.time.Clock()
        while self.running:
            if new_game:
                self.in_menu = True
                self.show_menu()
                self.menu.countdown(self.countdown_images, self.screen, self.roads, self.car, self.car1, self.car2, self.bot, self.aspect_ratio, self.mode_choice)
                # Після запуску гри встановлюємо newGame у False, щоб запобігти повторному перезапуску
                new_game = False
            self.roads.draw(self.screen)
            self.finish.draw(self.screen)
            self.obs.draw_obstackles(self.screen, self.map_choice)

            if self.mode_choice == 'single':
                self.score.draw_coins(self.screen)
                self.car.draw(self.screen)
                self.car.update_car(self.obs, self.map_choice, self.score)
                self.bot.draw(self.screen)  # Малюємо бота
                # Завершення гри, якщо фініш було перетнуто (пройдено всі кола)
                new_game = self.finish.crossed(self.screen, self.aspect_ratio, self.car, self.bot, self.score)  # self.running = not 
                self.score.draw_score(self.screen)

            else:
                self.car1.draw(self.screen)
                self.car1.update_car(self.obs, self.map_choice, self.score, self.mode_choice)
                self.car2.draw(self.screen)
                self.car2.update_car(self.obs, self.map_choice, self.score, self.mode_choice)
                # Завершення гри, якщо фініш було перетнуто (пройдено всі кола)
                new_game = self.finish.crossed(self.screen, self.aspect_ratio, self.car1, self.car2)  # self.running = not 

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if not self.handle_pause():  # Викликаємо метод паузи
                            new_game = True
                            break  # Якщо handle_pause повернув False, перериваємо цю ітерацію
                    elif event.key == pygame.K_n:
                        if music_playing.is_set():
                            next_track()
                    elif event.key == pygame.K_m:
                        mute_music()
            cars = [self.car, self.car1, self.car2]

            for car in cars:
                if car.collide(self.road_contour_mask):
                    car.bounce()

            self.bot.move()
            # Ліміт fps = 500
            clock.tick(500)

        # print(points_str)
        pygame.quit()    

    def show_menu(self):
        while self.in_menu:
            self.screen.blit(self.background, (0, 0))  
            self.menu.draw(self.screen)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.in_menu = False
                    pygame.quit()
                    exit()
                    return

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.menu.start_rect.collidepoint(event.pos):
                        overlay_music_in_loop("soundeffects/button_sound.mp3")
                        self.in_menu = False
                        self.choosing_mode = True
                        self.show_modes()
                    elif self.menu.options_rect.collidepoint(event.pos):
                        overlay_music_in_loop("soundeffects/button_sound.mp3")
                        self.menu.show_options(self.screen, self.running, self.background)  
                        
                    elif self.menu.rating_btn_rect.collidepoint(event.pos):
                        overlay_music_in_loop("soundeffects/button_sound.mp3")
                        self.menu.show_rating(self.screen, self.running, self.in_menu, self.background)

    def show_maps(self):
        while self.choosing_map:
            self.screen.blit(self.background, (0, 0))  
            self.maps_page.draw(self.screen)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.choosing_map = False
                    pygame.quit()
                    return

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.map_choice = self.maps_page.check_click(event.pos)
                    if self.map_choice:
                        self.choose_maps(self.map_choice)

    def choose_maps(self, map_choice):
        print(f"Selected map: {map_choice}")
        self.roads = Roads(f"img/{map_choice}.jpg", 0)
        self.choosing_map = False
        if self.mode_choice == 'single':
            self.create_objects_single(map_choice)
        else:
            self.create_objects_doubles(map_choice)

    def show_cars(self):
        if self.mode_choice == 'doubles':
            self.choosing_car = False
            self.choosing_map = True
            self.show_maps()
            
        while self.choosing_car:
            self.screen.blit(self.background, (0, 0))  
            self.cars_page.draw(self.screen)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.choosing_car = False
                    pygame.quit()
                    return

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    car_choice = self.cars_page.check_click(event.pos)
                    if car_choice:
                        self.choose_cars(car_choice)

    def choose_cars(self, car_choice):
        print(f"Selected car: {car_choice}")
        self.choosing_car = False
        if car_choice == 'car1':
            self.image = 'img/car1.png'
        elif car_choice == 'car2':
            self.image = 'img/car2.png'
        elif car_choice == 'car3':
            self.image = 'img/car3.png'
        elif car_choice == 'car4':
            self.image = 'img/car4.png'
        else:
            self.image = 'img/car5.png'

        self.choosing_map = True
        self.show_maps()       

    def show_modes(self):
        while self.choosing_mode:
            self.screen.blit(self.background, (0, 0))  
            self.modes_page.draw(self.screen)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.choosing_mode = False
                    pygame.quit()
                    return

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.mode_choice = self.modes_page.check_click(event.pos, self.mode_choice)
                    if self.mode_choice:
                        self.choose_modes()

    def choose_modes(self):
        print(f"Selected mode: {self.mode_choice}")
        self.choosing_mode = False
        self.choosing_car = True
        self.show_cars()

    def create_objects_single(self, map_choice):
        if map_choice == 'winter':
            self.finish_location = (275, 230)
            self.finish = Finish('img/finish.png', *self.finish_location, 90, 0.308, "bottom")
            self.car = Cars(1350, 250, 0, 0.75, 270, self.image, 'wasd')
            self.bot = Bots(1350, 287, 0, 0.67, 270, [(1654, 265), (1774, 309), (1822, 391), (1807, 657), 
            (1721, 723), (1575, 681), (1539, 550), (1450, 468), (1317, 500), (1273, 607), (1197, 701), (1036, 739), 
            (990, 815), (956, 929), (890, 990), (497, 1010), (184, 981), (138, 868), (139, 739), (162, 631),
            (225, 564), (384, 550), (637, 549), (727, 485), (739, 365), (644, 289), (268, 285)])
            self.road_contour = pygame.image.load('img/winter_edge.png')                       
        elif map_choice == 'summer':
            self.finish_location = (183, 985)
            self.finish = Finish('img/finish.png', *self.finish_location, 142, 0.21, "bottom")
            self.car = Cars(1745, 945, 0, 0.5, 52, self.image, 'wasd')
            self.bot = Bots(1755, 925, 0, 0.48, 52, [(1491, 749), (1344, 634), (1243, 555), (1200, 474), (1236, 383), 
            (1308, 282), (1376, 185), (1366, 109), (1293, 62), (1203, 92), (1106, 121), (1024, 90), (944, 110), 
            (858, 163), (759, 132), (671, 144), (591, 228), (492, 381), (475, 475), (541, 545), (695, 643), 
            (792, 598), (796, 505), (764, 401), (812, 328), (903, 332), (938, 378), (934, 446), (901, 525), 
            (942, 606), (1064, 700), (1112, 768), (1102, 847), (1028, 898), (965, 875), (891, 816), (808, 757), 
            (719, 740), (643, 809), (583, 881), (523, 918), (440, 909), (362, 887), (306, 917), (208, 1032)])
            self.road_contour = pygame.image.load('img/summer_edge.png')
        elif map_choice == 'beach':
            self.finish_location = (1488, 993)
            self.finish = Finish('img/finish.png', *self.finish_location, 0, 0.308)
            self.car = Cars(95, 990, 0, 0.75, 270, self.image, 'wasd')
            self.bot = Bots(95, 950, 0, 0.67, 270, [(336, 962), (489, 945), (547, 826), (490, 706), (329, 661), 
            (268, 540), (347, 413), (619, 413), (709, 504), (714, 918), (767, 989), (901, 1005), (973, 921), 
            (1005, 660), (1125, 596), (1248, 530), (1293, 407), (1428, 347), (1529, 414), (1566, 534), 
            (1703, 602), (1808, 671), (1822, 767), (1780, 855), (1657, 894), (1575, 946), (1541, 1028)])
            self.road_contour = pygame.image.load('img/beach_edge.png')
        elif map_choice == 'champions_field':
            self.finish_location = (292, 668)
            self.finish = Finish('img/finish.png', *self.finish_location, 0, 0.37, required_circles = 2)
            self.car = Cars(342, 730, 0, 0.98, 180, self.image, 'wasd')
            self.bot = Bots(372, 730, 0, 1, 180, [(376, 853), (458, 908), (557, 952), (706, 931), (861, 943), 
            (1140, 925), (1368, 950), (1499, 884), (1556, 767), (1541, 560), (1565, 337), (1526, 216), 
            (1413, 154), (1200, 158), (927, 136), (661, 154), (441, 162), (355, 282), (342, 428), (340, 700)])
            self.road_contour = pygame.image.load('img/champions_field_edge.png')
        elif map_choice == 'map2':
            self.finish_location = (128, 400)
            self.finish = Finish('img/finish.png', *self.finish_location, 0, 0.5, required_circles = 2)
            self.car = Cars(200, 487, 0, 1.07, 180, self.image, 'wasd')
            self.bot = Bots(240, 487, 0, 0.95, 180, [(230, 770), (306, 907), (670, 943), (918, 882), (1214, 967), 
            (1459, 852), (1557, 602), (1575, 330), (1460, 181), (1220, 81), (1097, 69), (986, 87), (911, 157), 
            (921, 264), (1079, 326), (1207, 395), (1264, 512), (1230, 592), (1094, 651), (752, 636), (625, 538), 
            (639, 338), (639, 175), (572, 110), (427, 119), (301, 168), (227, 242), (186, 419)])
            self.road_contour = pygame.image.load('img/map2_contour.png')
        else:
            self.finish_location = (55, 278)
            self.finish = Finish('img/finish.png', *self.finish_location, 0, 0.53, required_circles = 2)
            self.car = Cars(160, 365, 0, 1.1, 180, self.image, 'wasd')
            self.bot = Bots(120, 365, 0, 0.95, 180, [(166, 629), (161, 861), (280, 970), 
            (560, 845), (697, 674), (995, 685), (1225, 561), (1569, 519), (1742, 413), 
            (1665, 242), (1362, 245), (943, 219), (686, 87), (401, 71), (184, 158), (98, 386)])
            self.road_contour = pygame.image.load('img/map3_contour.png')        

        self.road_contour_mask = pygame.mask.from_surface(self.road_contour)
        self.score = Score("img/coin.png", map_choice)


    def create_objects_doubles(self, map_choice):
        if map_choice == 'winter':
            self.finish_location = (275, 230)
            self.finish = Finish('img/finish.png', *self.finish_location, 90, 0.308, "bottom")
            self.car1 = Cars(1350, 250, 0, 0.75, 270, 'img/car1.png', 'wasd')
            self.car2 = Cars(1350, 287, 0, 0.75, 270, 'img/car2.png', 'arrows')
            self.road_contour = pygame.image.load('winter_edge.png')                       
        elif map_choice == 'summer':
            self.finish_location = (183, 985)
            self.finish = Finish('img/finish.png', *self.finish_location, 142, 0.21, "bottom")
            self.car1 = Cars(1745, 945, 0, 0.5, 52, 'img/car1.png', 'wasd')
            self.car2 = Cars(1755, 925, 0, 0.5, 52, 'img/car2.png', 'arrows')
            self.road_contour = pygame.image.load('img/summer_edge.png')
        elif map_choice == 'beach':
            self.finish_location = (1488, 993)
            self.finish = Finish('finish.png', *self.finish_location, 0, 0.308)
            self.car1 = Cars(95, 990, 0, 0.75, 270, 'img/car1.png', 'wasd')
            self.car2 = Cars(95, 950, 0, 0.75, 270, 'img/car2.png', 'arrows')
            self.road_contour = pygame.image.load('img/beach_edge.png')
        elif map_choice == 'champions_field':
            self.finish_location = (292, 668)
            self.finish = Finish('img/finish.png', *self.finish_location, 0, 0.37, required_circles = 2)
            self.car1 = Cars(342, 730, 0, 0.95, 180, 'img/car1.png', 'wasd')
            self.car2 = Cars(372, 730, 0, 0.95, 180, 'img/car2.png', 'arrows')
            self.road_contour = pygame.image.load('img/champions_field_edge.png')
        elif map_choice == 'map2':
            self.finish_location = (128, 400)
            self.finish = Finish('img/finish.png', *self.finish_location, 0, 0.5, required_circles = 2)
            self.car1 = Cars(200, 487, 0, 1.07, 180, 'img/car1.png', 'wasd')
            self.car2 = Cars(240, 487, 0, 1.07, 180, 'img/car2.png', 'arrows')
            self.road_contour = pygame.image.load('img/map2_contour.png')
        else:
            self.finish_location = (55, 278)
            self.finish = Finish('img/finish.png', *self.finish_location, 0, 0.53, required_circles = 2)
            self.car1 = Cars(160, 365, 0, 1.1, 180, 'img/car1.png', 'wasd')
            self.car2 = Cars(120, 365, 0, 1.1, 180, 'img/car2.png', 'arrows')
            self.road_contour = pygame.image.load('img/map3_contour.png')        

        self.road_contour_mask = pygame.mask.from_surface(self.road_contour)

    def handle_pause(self):
        """
        Обробляє стан паузи гри, дозволяючи змінювати налаштування або вийти в головне меню.

        Ця функція викликається, коли гравець натискає `ESC` під час гри. Вона зупиняє 
        основний ігровий цикл та відображає меню паузи. У меню можна:
        - Відкрити налаштування.
        - Вийти в головне меню.
        - Продовжити гру, натиснувши `ESC`.

        Повертає:
            bool: `True`, якщо гравець продовжує гру.
                `False`, якщо гравець виходить у головне меню або закриває гру.
        """
        paused = True     
        while paused:
            for event in pygame.event.get():
                # Обробка кліків миші
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Відкрити меню налаштувань
                    if self.menu.options_rect.collidepoint(event.pos):
                        self.menu.show_options(self.screen, self.running, self.background)

                    # Вийти в головне меню
                    if self.menu.menu_back_rect.collidepoint(event.pos):
                        return False  

                # Закрити гру
                if event.type == pygame.QUIT:
                    self.running = False
                    quit()
                    return False  

                # Продовжити гру, якщо натиснуто ESC
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return True  

            # Малюємо екран паузи
            overlay = pygame.Surface(self.aspect_ratio, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Напівпрозорий чорний фон
            self.screen.blit(self.background, (0, 0))  
            self.screen.blit(self.pause_text, self.pause_rect)
            self.screen.blit(self.menu.imageOptions, self.menu.options_rect.topleft)  
            self.screen.blit(self.menu.menu_back_bnt, self.menu.menu_back_rect)
            pygame.display.flip()  

        return True

if __name__ == "__main__":
    game = GameSys()
    game.run()