# import thư viện và class
import pygame, os
import sys
import numpy as np
from pygame.locals import *
from search_way import *

# chuyển thư mục làm việc vào 
os.chdir('./AI_1')
# khởi tạo game
pygame.init()

# tạo nhạc
pygame.mixer.init()
pygame.mixer.music.load('assets/music_dra.mp3')
pygame.mixer.music.play(-1)

#----------------------------------------------------------------
# đặt thông số
SIZE = WIGHT, HEIGHT = 900, 900
scale = 1
block = 50
height = 900
width = 1500
fps = 23

#----------------------------------------------------------------
# chỉnh thông tin
screen = pygame.display.set_mode((width, height))
title = pygame.display.set_caption('Nhặt bi rồng')
icon = pygame.image.load('assets/Logo-IUH.jpg')
logo = pygame.display.set_icon(icon)
clock = pygame.time.Clock()

# tải hình ảnh 
robot = pygame.transform.scale(pygame.image.load('assets/U3.png'), (block, block))
goal = pygame.transform.scale(pygame.image.load('assets/dragonball.png'), (block,block))
intro = pygame.transform.scale(pygame.image.load('assets/intro1.png'), (width, height))
end = pygame.transform.scale(pygame.image.load('assets/end.jpeg'), (width, height))

# tải ảnh nhân vật
walk_Left = [pygame.transform.scale(pygame.image.load(f'assets/L{i}.png'), (block, block))for i in range(1,4)]*5
walk_Right=[pygame.transform.scale(pygame.image.load(f'assets/R{i}.png'), (block, block))for i in range(1,4)]*5
walk_Up=[pygame.transform.scale(pygame.image.load(f'assets/U{i}.png'), (block, block))for i in range(1,4)]*5
walk_Down=[pygame.transform.scale(pygame.image.load(f'assets/D{i}.png'), (block, block))for i in range(1,4)]*5

# tạo font chữ
font = pygame.font.SysFont("Time new romand", 50)

# đặt màu
yellow_color=(255, 255, 0)
black_color=(0, 0, 0)

#------------------------------------------------------------------------------
class Play():
    def __init__(self,map):
        self.walkCount = 0 # số bước đi của nhân vật
        self.end_map = False # trạng thái kết thúc map
        self.pos_x=None # vị trí nhân vật trên trục x
        self.pos_y=None # vị trí nhân vật trên trục y
        # trạng thái hướng đi của nhân vật
        self.left=False
        self.right=False
        self.up=False
        self.down=False
        self.vel=10 # tốc độ chạy của nhân vật
        
        # load data
        f = open(f'map/map{map}.csv', 'r')
        self.data=np.array([i.split(',') for i in f.readlines()]).astype(int).transpose()
        # load ảnh map
        self.img_bg=pygame.transform.scale(pygame.image.load(f'assets/map{map}.png'),(900,900))
        # lấy tọa độ vị trí của nhân vật trên map
        self.pos_nv = (np.array(self.get_point(1))*block)
        self.rect = robot.get_rect() # vẽ khung cho nhân vật

    # hàm lấy tọa độ tại vị trí có giá trị num
    def get_point(self, num):
        p = list(zip(*np.where(self.data==num)))
        return p[0] if len(p)==1 else -1

    # hàm lấy danh sách vật cản 
    def get_barrier(self, num):
        return list(zip(*np.where(self.data==num)))

    # hàm tạo chuyển động nhân vật
    def redrawGameWindow(self):
        if self.left:
            screen.blit(walk_Left[self.walkCount%3], self.rect)
            self.walkCount += 1
        elif self.right:
            screen.blit(walk_Right[self.walkCount%3], self.rect)
            self.walkCount += 1
        elif self.up:
            screen.blit(walk_Down[self.walkCount%3], self.rect)
            self.walkCount += 1
        elif self.down:
            screen.blit(walk_Up[self.walkCount%3], self.rect)
            self.walkCount += 1
        else:
            screen.blit(robot, self.rect)
    
    def constrain(self, x, y, x_, y_):
        bar = self.get_barrier(-1)
        if (x_, y_) in bar:
            return x, y
        return x_, y_
    # hàm tạo hướng đi cho nhân vật
    def animation(self):
        self.rect.x = self.pos_x
        self.rect.y = self.pos_y
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.pos_x > self.vel:
            self.pos_x -= self.vel
            self.left=True
            self.right=False
            self.up=False
            self.down=False
            
        elif keys[pygame.K_RIGHT] and self.pos_x < 900 - block - self.vel:
            self.pos_x += self.vel
            self.right=True
            self.left=False
            self.up=False
            self.down=False
            
        elif keys[pygame.K_UP] and self.pos_y > self.vel-10:
            self.pos_y -= self.vel
            self.up=True
            self.left=False
            self.right=False
            self.down=False
        
        elif keys[pygame.K_DOWN] and self.pos_y < 900 - block - self.vel:
            self.pos_y += self.vel
            self.down=True
            self.left=False
            self.right=False
            self.up=False
        else:
            self.right = False
            self.left = False
            self.up = False
            self.down = False

    # hàm chạy đến đích theo thuật toán
    def run(self):
        self.animation()
        self.redrawGameWindow()
        pos_goal = np.array(self.get_point(2))*block
        # lấy tọa độ đích đến
        draw_goal = pygame.Rect(pos_goal[0], pos_goal[1], 5, 5)
        draw_goal.center = (pos_goal[0]+25, pos_goal[1]+25)
        # khi chạm vào goal thì kết thúc màn chơi
        if self.rect.colliderect(draw_goal):
            self.end_map = True

    # chuyển tỷ lệ các tọa độ trong data sang tỷ lệ hiển thị
    def scale(self,list_auto):
        return [(list_auto[i][0]*block,list_auto[i][1]*block) for i in range(len(list_auto))]
    
    # hàm chuyển tỷ lệ 1 tọa độ
    def scale_x_y(self,x,y):
        return (x*block,y*block)
    
    # hàm này chia ra các tọa độ để tọa độ để chạy cho mượt
    '''
        VD: đi từ A(0, 0) đến B(5, 0)
        thì sẽ đi (0, 0) -> (1, 0) -> (2,0) -> (3, 0) -> (4, 0) -> (5, 0)
    '''
    def ai_move_coor(self,coor_auto):
        # lấy tọa độ nhân vật
        pos_x = self.pos_nv[0]
        pos_y = self.pos_nv[1]
        coor=[]
        # gán biến tạm xác định tọa độ hiện tại
        bandau_x=pos_x
        bandau_y=pos_y
        for i in range(1,len(coor_auto)):
            # nếu như tọa độ y bằng nhau thì so sánh 2 tọa độ x, nếu tọa độ hiện tại >= (<=)tọa độ tiếp theo thì thêm vào list coor với step tăng lên 10 or giảm đi 10
            if bandau_y==coor_auto[i][1] and bandau_x >=coor_auto[i][0]:
                for j in range(bandau_x,coor_auto[i][0]-10,-10):
                    coor.append((j,coor_auto[i][1]))
        
            if bandau_y==coor_auto[i][1] and bandau_x <=coor_auto[i][0]:
                for j in range(bandau_x,coor_auto[i][0],10):
                    coor.append((j,coor_auto[i][1]))

            # nếu như tọa độ x bằng nhau thì so sánh 2 tọa độ y, nếu tọa độ y hiện tại >= (<=)tọa độ y tiếp theo thì thêm vào list coor với step tăng lên 10 or giảm đi 10
            if bandau_x==coor_auto[i][0] and bandau_y<=coor_auto[i][1]:
                for j in range(bandau_y,coor_auto[i][1]+10,10):
                    coor.append((bandau_x,j))
            
            if bandau_x==coor_auto[i][0] and bandau_y>=coor_auto[i][1]:
                for j in range(bandau_y,coor_auto[i][1]-10,-10):
                    coor.append((bandau_x,j))
            # gán lại tọa độ hiện tại
            bandau_y=coor_auto[i][1]
            bandau_x=coor_auto[i][0]
        
        coor=np.array(coor)
        return coor

def info(s, g, barrier):
    o = Search(height//block, height//block, barrier)
    df = o.viewInfo(s, g)
    df['Total'] = df['Time (ms)']+df['Number of Steps']
    return df
# hàm tính toán lấy đường đi tối ưu nhất với công thức đơn giản = time(m) + len(f(x))
def calc(s, g, barrier):
    o = Search(height//block, height//block, barrier) # khởi tạo thuật toán
    x = o.runAll(s, g) # chạy tất cả thuật toán
    alg = [i[1]+len(i[2]) for i in x] # lấy giá trị để so sánh
    id = alg.index(min(alg)) # lấy chỉ số có giá trị min
    return x[id] # trả về thuật toán được chọn

# tạo hiệu ứng chuyển cảnh với fade_counter dùng để tăng độ dài kéo dần tới WEIGHT
def loading_next_map():
    fade_counter=0
    run=True
    while run:
        if fade_counter < height:
            fade_counter += 20
            # chia thành 10 dòng để tạo hiệu ứng
            for y in range(0, 10, 2):
                # left, top, width, height = 0, y*100, fade_counter, 100
                pygame.draw.rect(screen, (0, 0, 0),(0, y*100, fade_counter, 100))
                # left, top, width, height = height-fade_counter, (y+1)*100, height, 100
                pygame.draw.rect(screen, (0, 0, 0), (height-fade_counter, (y+1)*100, height, 100))
                pygame.display.update()
        else:
            run=False

# vẽ chữ lên màn hình
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# load map và vẽ chữ lên màn hình
def load_drawtext():
    loading_next_map()
    draw_text("BRO, NEXT MAP NOW!", font,(255, 255, 255), height//4, height//4)
    draw_text("PRESS SPACE TO PLAY NEXT MAP",font, (255, 255, 255),  height//4, height//4+100)
    draw_text("PRESS TAB TO AUTO PLAY",font, (255, 255, 255),  height//4, height//4+200)
    draw_text("PRESS ESC TO EXIT",font, (255, 255, 255),  height//4, height//4+300)

#Vẽ map hiện tại và chế độ có tự động 
def load_number_map(m,str_auto):
    screen.fill((0,0,0))
    lv = font.render(f'Map {m}', False, black_color, yellow_color)
    stt = font.render(f'Auto: {str_auto}', False, black_color, yellow_color)
    
    screen.blit(lv, (1000, 100)) # hiển thị map đang chạy
    screen.blit(stt, (1000, 200)) # hiển thị chế độ
    pygame.display.update()

# Hàm người chơi
def player(map):
    per=Play(map)
    pos_nv = per.pos_nv
    # gán tọa độ nhân vật
    per.pos_x = pos_nv[0]
    per.pos_y = pos_nv[1]
    run =True
    
    # có thoát chế độ người chơi ko, 
    status_cv_auto=False 
    while run:
        screen.blit(per.img_bg,(0,0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if not per.end_map:
            keys=pygame.key.get_pressed()
            if not keys[pygame.K_TAB]:
                per.run()
            else:
                status_cv_auto=True
                run =False
        else:
            run =False
        pygame.display.update()
        # fps
        clock.tick(fps)
    return status_cv_auto


def ai(map):
    play_ai=Play(map)
    
    # lấy tọa độ vật cản, điểm bắt đầu, điểm kết thúc 
    barrier= play_ai.get_barrier(-1)
    start=play_ai.get_point(1)
    goal_key=play_ai.get_point(2)

    print(info(start,goal_key,barrier))
    # lấy đường đi
    way = calc(start, goal_key, barrier)[-1] 
    # chia nhỏ thành các khoảng giữa 2 ô đi
    coor=play_ai.ai_move_coor(play_ai.scale(way))
    # gán tọa độ hiện tại để so sánh tọa độ tại vị trí tiếp theo lớn hơn hay nhỏ hơn để vẽ animation cho bot
    ani_x=start[0]
    ani_y=start[1]
    # hiệu ứng
    val_L=0
    val_R=0
    val_U=0
    val_D=0
    
    i=0
    run=True
    while run:
        if not play_ai.end_map:
            while i<len(coor):
                screen.blit(play_ai.img_bg,(0,0))
                # tạo hiệu ứng để bot đi bên phải
                if coor[i][1]==ani_y and coor[i][0]>ani_x:
                    screen.blit(walk_Right[val_R%3],(coor[i][0],coor[i][1]))
                    val_R+=1
                # tạo hiệu ứng để bot đi bên trái
                elif coor[i][1]==ani_y and coor[i][0]<ani_x:
                    screen.blit(walk_Left[val_L%3],(coor[i][0],coor[i][1]))
                    val_L+=1
                # tạo hiệu ứng để bot đi lên trên
                elif coor[i][0]==ani_x and coor[i][1]>=ani_y:
                    screen.blit(walk_Up[val_U%3],(coor[i][0],coor[i][1]))
                    val_U+=1
                # tạo hiệu ứng để bot đi xuống dưới
                elif coor[i][0]==ani_x and coor[i][1]<=ani_y:
                    screen.blit(walk_Down[val_D%3],(coor[i][0],coor[i][1]))
                    val_D+=1

                # gán tọa độ vị trí hiện tại
                ani_x=coor[i][0]
                ani_y=coor[i][1]
                i+=1
                pygame.display.update()
                clock.tick(fps)
            play_ai.end_map=True
            
        elif play_ai.end_map:
            run=False
        pygame.display.update()
        clock.tick(fps)

def main():
    m=0 # biến thể hiện vị trí map
    auto_ai = False
    screen.blit(intro, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()   
                sys.exit()
            
            keys=pygame.key.get_pressed()
            # tạo sự kiện nhấn nút space để chuyển map
            if keys[pygame.K_SPACE]:
                m+=1
                if m==8:
                    screen.blit(end, (0, 0))
                    pygame.display.update()
                    # pygame.time.delay(2000)
                elif m>=9:
                    m+=1
                else:
                    str_auto="Turn off"
                    load_number_map(m,str_auto)
                    status=player(m)
                    if not status:
                        load_drawtext()
            
            if keys[pygame.K_TAB]:
                str_auto="Turn on"
                
                load_number_map(m,str_auto)
                ai(m)
                load_drawtext()
                
            if keys[pygame.K_ESCAPE]:
                pygame.quit()   
                sys.exit()
        clock.tick(fps)
        pygame.display.update()

if __name__ == "__main__":
    main()