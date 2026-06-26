import pygame
import numpy as np
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import math

# 初始化 Pygame 和 OpenGL
pygame.init()
display = (1920, 1080)
screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
pygame.display.set_caption("我的世界 - Python 版本")

# OpenGL 设置
glEnable(GL_DEPTH_TEST)
glEnable(GL_TEXTURE_2D)
gluPerspective(45, (display[0] / display[1]), 0.1, 500.0)
glTranslatef(0.0, 0.0, -15)

# 方块类型
BLOCK_TYPES = {
    0: (0.2, 0.2, 0.2),      # 空气 (不可见)
    1: (0.8, 0.6, 0.4),      # 泥土
    2: (0.2, 0.8, 0.2),      # 草
    3: (0.6, 0.3, 0.1),      # 木头
    4: (0.8, 0.8, 0.8),      # 石头
    5: (0.9, 0.9, 0.5),      # 沙子
    6: (0.4, 0.2, 0.1),      # 深棕色木头
}

class Block:
    """方块类"""
    def __init__(self, x, y, z, block_type):
        self.x = x
        self.y = y
        self.z = z
        self.block_type = block_type
        self.vertices = self.get_vertices()
        self.edges = self.get_edges()
    
    def get_vertices(self):
        """获取方块的8个顶点"""
        x, y, z = self.x, self.y, self.z
        return [
            (x, y, z),
            (x+1, y, z),
            (x+1, y+1, z),
            (x, y+1, z),
            (x, y, z+1),
            (x+1, y, z+1),
            (x+1, y+1, z+1),
            (x, y+1, z+1),
        ]
    
    def get_edges(self):
        """获取方块的12条边"""
        return [
            (0, 1), (1, 2), (2, 3), (3, 0),  # 前面
            (4, 5), (5, 6), (6, 7), (7, 4),  # 后面
            (0, 4), (1, 5), (2, 6), (3, 7),  # 连接边
        ]
    
    def draw(self):
        """绘制方块"""
        if self.block_type == 0:
            return
        
        color = BLOCK_TYPES[self.block_type]
        glColor3f(*color)
        
        glBegin(GL_QUADS)
        
        # 六个面
        faces = [
            (0, 1, 2, 3),  # 前
            (4, 7, 6, 5),  # 后
            (0, 4, 5, 1),  # 底
            (2, 6, 7, 3),  # 顶
            (0, 3, 7, 4),  # 左
            (1, 5, 6, 2),  # 右
        ]
        
        for face in faces:
            for vertex_idx in face:
                glVertex3fv(self.vertices[vertex_idx])
        
        glEnd()
        
        # 绘制方块边界
        glColor3f(0.0, 0.0, 0.0)
        glLineWidth(1)
        glBegin(GL_LINES)
        
        for edge in self.edges:
            for vertex_idx in edge:
                glVertex3fv(self.vertices[vertex_idx])
        
        glEnd()

class World:
    """世界类"""
    def __init__(self, width=50, height=50, depth=50):
        self.width = width
        self.height = height
        self.depth = depth
        self.blocks = {}
        self.generate_world()
    
    def generate_world(self):
        """生成世界地形"""
        print("正在生成世界...")
        
        for x in range(self.width):
            for z in range(self.depth):
                # 使用 Perlin 噪声生成高度
                height = self.get_terrain_height(x, z)
                
                for y in range(self.height):
                    if y < height:
                        block_type = self.determine_block_type(x, y, z, height)
                        self.blocks[(x, y, z)] = Block(x, y, z, block_type)
                    else:
                        # 天空
                        self.blocks[(x, y, z)] = Block(x, y, z, 0)
        
        print(f"世界生成完成！共生成 {len(self.blocks)} 个方块")
    
    def get_terrain_height(self, x, z):
        """使用简单噪声生成地形高度"""
        # 简单的正弦/余弦混合噪声
        noise = math.sin(x * 0.05) * 5 + math.cos(z * 0.05) * 5
        noise += random.Random(x * 100 + z).random() * 2
        height = int(15 + noise)
        return max(5, min(30, height))
    
    def determine_block_type(self, x, y, z, height):
        """确定方块类型"""
        if y < 5:
            return 4  # 石头
        elif y < height - 1:
            return 1  # 泥土
        elif y == height - 1:
            return 2  # 草
        elif y < height:
            return 1  # 泥土
        else:
            return 0  # 空气
    
    def draw(self):
        """绘制所有方块"""
        for block in self.blocks.values():
            if block.block_type != 0:  # 不绘制空气方块
                block.draw()

class Camera:
    """摄像机类"""
    def __init__(self):
        self.pos = [25, 20, 25]
        self.rot = [0, 0]
    
    def update(self):
        """更新摄像机位置和旋转"""
        keys = pygame.key.get_pressed()
        speed = 0.5
        
        # WASD 控制移动
        if keys[K_w]:
            self.pos[2] -= speed
        if keys[K_s]:
            self.pos[2] += speed
        if keys[K_a]:
            self.pos[0] -= speed
        if keys[K_d]:
            self.pos[0] += speed
        if keys[K_SPACE]:
            self.pos[1] += speed
        if keys[K_LSHIFT]:
            self.pos[1] -= speed
        
        # 鼠标控制旋转
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[2]:  # 右键
            mouse_x, mouse_y = pygame.mouse.get_rel()
            self.rot[0] += mouse_y * 0.5
            self.rot[1] += mouse_x * 0.5
        else:
            pygame.mouse.get_rel()
        
        # 应用摄像机变换
        glLoadIdentity()
        glRotatef(self.rot[0], 1, 0, 0)
        glRotatef(self.rot[1], 0, 1, 0)
        glTranslatef(-self.pos[0], -self.pos[1], -self.pos[2])

def main():
    """主函数"""
    clock = pygame.time.Clock()
    world = World(60, 40, 60)
    camera = Camera()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        camera.update()
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.5, 0.7, 1.0, 1.0)  # 天空蓝色
        
        world.draw()
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()