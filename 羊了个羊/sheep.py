import pgzrun
import pygame
import random
import math
import os
from pygame import Rect  # 导入 Rect

# 加载字体
FONT_NAME = 'SimHei.ttf'  # 自定义字体名称
FONT_SIZE = 40  # 字体大小
SMALL_FONT_SIZE = 20
custom_font = pygame.font.Font(FONT_NAME, FONT_SIZE)  # 加载自定义字体
small_font=pygame.font.Font(FONT_NAME, SMALL_FONT_SIZE)
# 游戏基本属性
TITLE = '宝了个贝'
WIDTH = 600
HEIGHT = 720
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50
BUTTON_X = WIDTH - BUTTON_WIDTH - 20
BUTTON_Y = 20
last_tile = None  # 用于存储最后一次点击的牌和它的原始位置

# 牌的常量
TILE_WIDTH = 60
TILE_HEIGHT = 66
DOCK_POSITION = Rect((90, 564), (TILE_WIDTH * 7, TILE_HEIGHT))
DIFFICULTY = 0

# 游戏状态
game_started = False  # 是否开始游戏
game_over = False     # 游戏是否结束
time_left = 300        # 倒计时时间（秒）
in_menu = True        # 是否在主菜单

# 游戏中的牌
tiles = []  # 上方的所有牌
docks = []  # 牌堆里的牌

# 初始化牌组函数
def init_tiles():
    global tiles, docks, time_left, game_over, game_started, difficulty
    tiles = []
    docks = []
   
    # 根据难度选择生成不同层数的牌
    layers = 5 
    pic_num = 5 
    if difficulty == 2: 
        layers = 6 
        pic_num=8
    elif difficulty == 3 :
        layers = 7  # 简单4层，中等5层，困难6层
        pic_num=12
    
    time_left = 120 # 时间设置两分钟
    game_over = False
    game_started = True
    tile_types = list(range(1, pic_num+1)) * 12  # pic_num种牌，每种12张
    random.shuffle(tile_types)
    tile_index = 0

    
    con_layers=layers
    # 计算中心点坐标
    center_x = WIDTH // 2
    center_y = HEIGHT // 2

    for layer in range(layers):
        # 每一层的牌数量和布局
        rows = con_layers - layer
        cols = con_layers - layer

        # 计算层的起始坐标以使得这一层牌居中
        start_x = center_x - (cols * TILE_WIDTH * 0.5) + 30
        start_y = center_y - (rows * TILE_HEIGHT * 0.5) - 10

        for row in range(rows):
            for col in range(cols):
                tile_type = tile_types[tile_index]
                tile_index += 1
                tile = Actor(f'p{tile_type}')
                if(difficulty==3):
                    tile.pos = start_x + col * tile.width, start_y + row * tile.height * 0.9-30
                else:
                    tile.pos = start_x + col * tile.width, start_y + row * tile.height * 0.9
                tile.tag = tile_type
                tile.layer = layer
                # 顶层的牌是可点击的，其他层根据是否被覆盖来决定
                tile.status = 1 if layer == layers - 1 else 0  # 顶层牌可点，其他不可点
                tiles.append(tile)

    # 额外的4张牌放在最下方
    num=5
    if difficulty==3: 
        num=4
    for i in range(num):
        tile_type = tile_types[tile_index]
        tile_index += 1
        tile = Actor(f'p{tile_type}')
        if(difficulty==3):
            tile.pos = 210 + i * tile.width, 516
        else:
            tile.pos = 210 + i * tile.width-30, 516
        tile.tag = tile_type
        tile.layer = 0
        tile.status = 1
        tiles.append(tile)

# 游戏绘制函数
def draw():
    if in_menu:
        draw_start_screen()  # 绘制主菜单
    elif not game_started:
        draw_start_screen()  # 绘制开始界面
    else:
        draw_game_screen()  # 绘制游戏界面

# 绘制开始界面
def draw_start_screen():
    screen.clear()
    screen.blit('start_background', (0, 0))  # 开始界面的背景
    
    #使用自定义字体绘制中文
    text_surface = custom_font.render("选择难度", True, (255, 255, 255))
    screen.blit(text_surface, (WIDTH / 2 - text_surface.get_width() / 2, HEIGHT / 2 - 150))
    
    text_surface = custom_font.render("1. 简单", True, (255, 255, 255))
    screen.blit(text_surface, (WIDTH / 2 - text_surface.get_width() / 2, HEIGHT / 2 - 50))
    
    text_surface = custom_font.render("2. 中等", True, (255, 255, 255))
    screen.blit(text_surface, (WIDTH / 2 - text_surface.get_width() / 2, HEIGHT / 2))
    
    text_surface = custom_font.render("3. 困难", True, (255, 255, 255))
    screen.blit(text_surface, (WIDTH / 2 - text_surface.get_width() / 2, HEIGHT / 2 + 50))

# 绘制游戏界面
def draw_game_screen():
    screen.clear()
    screen.blit('back', (0, 0))  # 背景

    # 绘制所有牌
    for tile in tiles:
        tile.draw()
        if tile.status == 0:
            screen.blit('mask', tile.topleft)  # 遮罩不可点击的牌

    # 绘制牌堆中的牌
    for index, tile in enumerate(docks):
        tile.left = DOCK_POSITION.x + index * TILE_WIDTH
        tile.top = DOCK_POSITION.y
        tile.draw()

    # 显示剩余时间
    screen.draw.text(f"time: {int(time_left)}s", (10, 10), fontsize=40, color="white")

    # 绘制“返回主菜单”按钮
    draw_menu_button()

    if time_left == 0:
        screen.blit('end', (0, 0))
        text_surface = custom_font.render("点击屏幕返回主菜单", True, (255, 255, 255))
        screen.blit(text_surface, (WIDTH / 2 - text_surface.get_width() / 2, HEIGHT / 2 - 150))

    # 游戏结束或胜利提示
    if len(docks) >= 7:
        game_over = True  # 超过7张牌，游戏失败
        screen.blit('end', (0, 0))
        text_surface = custom_font.render("点击屏幕返回主菜单", True, (255, 255, 255))
        screen.blit(text_surface, (WIDTH / 2 - text_surface.get_width() / 2, HEIGHT / 2 - 150))
    if not tiles:
        screen.blit('win', (0, 0))  # 没有剩余牌，胜利
        text_surface = custom_font.render("点击屏幕返回主菜单", True, (255, 255, 255))
        screen.blit(text_surface, (WIDTH / 2 - text_surface.get_width() / 2, HEIGHT / 2 - 150))

# 绘制“返回主菜单”按钮
def draw_menu_button():
    screen.draw.filled_rect(Rect((BUTTON_X, BUTTON_Y), (BUTTON_WIDTH, BUTTON_HEIGHT)), (255, 0, 0))  # 红色背景按钮
    text_surface = small_font.render("返回主菜单", True, (255, 255, 255))
    
    screen.blit(text_surface, ((BUTTON_X + BUTTON_WIDTH // 2)-47, (BUTTON_Y + BUTTON_HEIGHT // 2)-10))

# 更新函数，用于处理倒计时
def update(dt):
    global time_left, game_over
    if game_started and not game_over:
        time_left -= dt  # 每帧减少时间
        if time_left <= 0:  # 时间用完则游戏失败
            
           
            time_left = 0
            game_over = True  # 游戏结束
# 鼠标点击响应函数
def on_mouse_down(pos):
    global game_started, docks, game_over, difficulty, in_menu

    if in_menu:  # 如果在主菜单
        if 250 < pos[0] < 350 and 300 < pos[1] < 350:
            difficulty = 1  # 简单
        elif 250 < pos[0] < 350 and 350 < pos[1] < 400:
            difficulty = 2  # 中等
        elif 250 < pos[0] < 350 and 400 < pos[1] < 450:
            difficulty = 3  # 困难

        if difficulty > 0:  # 玩家选择了难度，开始游戏
            in_menu = False
            game_started = True
            init_tiles()
            music.play('bgm')
        return

    # 检查是否点击了“返回主菜单”按钮
    if BUTTON_X < pos[0] < BUTTON_X + BUTTON_WIDTH and BUTTON_Y < pos[1] < BUTTON_Y + BUTTON_HEIGHT:
        in_menu = True
        game_started = False
        return

    if game_over:  # 游戏结束时点击屏幕返回主菜单
        in_menu = True
        return

    if len(docks) >= 7 or not tiles or game_over:  # 如果游戏结束，则不再响应点击
        in_menu = True
        return

    # 遍历所有牌，找出最上面的可点击的牌
    for tile in reversed(tiles):
        if tile.status == 1 and tile.collidepoint(pos):  # 可点击的牌
            tile.status = 2  # 标记为已选中
            tiles.remove(tile)
            diff = [t for t in docks if t.tag != tile.tag]  # 获取不相同的牌
            if len(docks) - len(diff) < 2:  # 相同牌不超过2张
 
                docks.append(tile)
            else:
                docks = diff  # 消除相同牌

            # 更新被覆盖牌的状态
            for lower_tile in tiles:
                if lower_tile.layer == tile.layer - 1 and lower_tile.colliderect(tile):
                    # 检查当前牌是否有被其他牌覆盖
                    for upper_tile in tiles:
                        if upper_tile.layer == lower_tile.layer + 1 and upper_tile.colliderect(lower_tile):
                            break
                    else:
                        lower_tile.status = 1  # 如果没有牌覆盖它，设置为可点击
            return

# 开始游戏循环
pgzrun.go()