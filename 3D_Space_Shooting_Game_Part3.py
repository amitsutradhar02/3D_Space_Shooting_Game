# World and Collectibles Module
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time


player_pos = [0, 0, 0]
player_lives = 10
player_score = 0
shield_active = False

# Game object lists
collectibles = []
obstacles = []
stars = []

# Game parameters
collectible_spawn_timer = 0


def draw_3d_heart():
    glPushMatrix()
    glRotatef(glutGet(GLUT_ELAPSED_TIME) * 0.1, 0, 1, 0)
    
    glPushMatrix()
    glTranslatef(-5, 5, 0)
    glScalef(0.8, 0.8, 0.6)
    gluSphere(gluNewQuadric(), 8, 8, 8)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(5, 5, 0)
    glScalef(0.8, 0.8, 0.6)
    gluSphere(gluNewQuadric(), 8, 8, 8)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(0, -2, 0)
    glRotatef(45, 0, 0, 1)
    glScalef(0.7, 1.2, 0.6)
    glutSolidCube(12)
    glPopMatrix()
    
    glPopMatrix()

def draw_collectible(collectible_data):
    pos = collectible_data["pos"]
    item_type = collectible_data["type"]
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    
    if item_type == "health":
        glColor3f(1, 0.2, 0.5)
        draw_3d_heart()
    elif item_type == "shield":
        glColor3f(1, 1, 0)
        gluSphere(gluNewQuadric(), 12, 8, 8)
    elif item_type == "score":
        glColor3f(1, 0.5, 0)
        glPushMatrix()
        glRotatef(glutGet(GLUT_ELAPSED_TIME) * 0.1, 0, 1, 0)
        gluSphere(gluNewQuadric(), 10, 8, 8)
        glPopMatrix()
    
    glPopMatrix()

def draw_obstacle(obstacle_data):
    pos = obstacle_data["pos"]
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    
    if obstacle_data["type"] == "asteroid":
        glColor3f(0.4, 0.4, 0.4)
        glPushMatrix()
        glRotatef(glutGet(GLUT_ELAPSED_TIME) * 0.05, 1, 1, 0)
        
        glScalef(1.2, 0.8, 1.1)
        gluSphere(gluNewQuadric(), 30, 8, 6)
        glPopMatrix()
    
    glPopMatrix()

def draw_starfield():
    
    glPointSize(2.0)
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_POINTS)
    for star in stars:
        glVertex3f(star[0], star[1], star[2])
    glEnd()

def init_starfield():
    global stars
    stars = []
    for _ in range(200):
        x = random.uniform(-800, 800)
        y = random.uniform(-800, 800)
        z = random.uniform(-1000, 1000)
        stars.append([x, y, z])

def init_obstacles():
    global obstacles
    obstacles = []
    for _ in range(15):
        x = random.uniform(-600, 600)
        y = random.uniform(-50, 100)
        z = random.uniform(-600, 600)
        if abs(x) > 100 or abs(z) > 100:
            obstacles.append({"pos": [x, y, z], "type": "asteroid"})

def spawn_collectible():
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(150, 400)
    x = player_pos[0] + math.cos(angle) * distance
    z = player_pos[2] + math.sin(angle) * distance
    y = random.uniform(0, 30)
    
    item_type = random.choices(["health", "shield", "score"], weights=[0.5, 0.2, 0.3])[0]
    collectibles.append({"pos": [x, y, z], "type": item_type})


def update_game_state_world():
    global player_lives, player_score, shield_active
    
    for obstacle in obstacles:
        distance = math.sqrt(
            (player_pos[0] - obstacle["pos"][0])**2 +
            (player_pos[1] - obstacle["pos"][1])**2 +
            (player_pos[2] - obstacle["pos"][2])**2
        )
        if distance < 45:
            if not cheat_mode and not shield_active:
                player_lives -= 1
            dx = player_pos[0] - obstacle["pos"][0]
            dz = player_pos[2] - obstacle["pos"][2]
            if dx != 0 or dz != 0:
                length = math.sqrt(dx**2 + dz**2)
                player_pos[0] += (dx / length) * 20
                player_pos[2] += (dz / length) * 20


    collectibles_to_remove = []
    for collectible in collectibles[:]:
        distance = math.sqrt(
            (player_pos[0] - collectible["pos"][0])**2 +
            (player_pos[1] - collectible["pos"][1])**2 +
            (player_pos[2] - collectible["pos"][2])**2
        )
        if distance < 40:
            if collectible["type"] == "health":
                player_lives += 1
            elif collectible["type"] == "shield":
                shield_active = True
            elif collectible["type"] == "score":
                player_score += 10
            collectibles_to_remove.append(collectible)

    for collectible in collectibles_to_remove:
        if collectible in collectibles:
            collectibles.remove(collectible)
    
    global collectible_spawn_timer
    collectible_spawn_timer += 1
    if collectible_spawn_timer > 200 and len(collectibles) < 4:
        spawn_collectible()
        collectible_spawn_timer = 0


def idle():
    update_game_state_world()
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    draw_starfield()

    for obstacle in obstacles:
        draw_obstacle(obstacle)

    for collectible in collectibles:
        draw_collectible(collectible)

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"3D Space Shooter")

    glutDisplayFunc(showScreen)
    glutIdleFunc(idle)
    
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.0, 0.0, 0.1, 1.0)
    
    init_starfield()
    init_obstacles()

    glutMainLoop()

if __name__ == "__main__":
    main()