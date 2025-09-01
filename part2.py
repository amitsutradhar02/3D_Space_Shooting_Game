# Enemies and Spawning Module
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_TIMES_ROMAN_24
import math
import random
import time


player_pos = [0, 0, 0]
player_score = 0
is_boss_active = False
is_game_over = False
cheat_mode = False
boss_warning_timer = 0
BOSS_SCORE_INTERVAL = 50

# Game object lists
enemies = []
bullets = []
collectibles = []

# Game parameters
enemy_spawn_timer = 0

def draw_text(x, y, text, font=GLUT_BITMAP_TIMES_ROMAN_24):
  
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_triangle():
   
    glBegin(GL_TRIANGLES)
    # Front face
    glVertex3f(0, 10, 15)
    glVertex3f(-10, -10, -5)
    glVertex3f(10, -10, -5)
    
    # Left face
    glVertex3f(0, 10, 15)
    glVertex3f(-10, -10, -5)
    glVertex3f(0, -10, -15)
    
    # Right face
    glVertex3f(0, 10, 15)
    glVertex3f(10, -10, -5)
    glVertex3f(0, -10, -15)
    
    # Bottom face
    glVertex3f(-10, -10, -5)
    glVertex3f(10, -10, -5)
    glVertex3f(0, -10, -15)
    glEnd()

def draw_scary_boss():

    # Main body - large sphere
    glColor3f(0.8, 0.2, 0.2)  
    gluSphere(gluNewQuadric(), 15, 20, 20) 
    
    # Spikes around the boss
    glColor3f(1, 0, 0)  
    for i in range(8):
        angle = i * 45
        glPushMatrix()
        glRotatef(angle, 0, 1, 0)
        glTranslatef(18, 0, 0)
        glRotatef(90, 0, 1, 0)
        gluCylinder(gluNewQuadric(), 2, 0, 8, 6, 1)
        glPopMatrix()
    
    # Eyes
    glColor3f(1, 1, 0)  
    glPushMatrix()
    glTranslatef(-5, 5, 12)
    gluSphere(gluNewQuadric(), 3, 8, 8)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(5, 5, 12)
    gluSphere(gluNewQuadric(), 3, 8, 8)
    glPopMatrix()
    
    # Pupils
    glColor3f(0, 0, 0)  
    glPushMatrix()
    glTranslatef(-5, 5, 14)
    gluSphere(gluNewQuadric(), 1, 8, 8)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(5, 5, 14)
    gluSphere(gluNewQuadric(), 1, 8, 8)
    glPopMatrix()

def draw_enemy(enemy_data):
    
    pos = enemy_data["pos"]
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    
    enemy_type = enemy_data["type"]
    if enemy_type == "normal":
        # Normal enemy - 3D triangle (pyramid)
        glColor3f(1, 0, 0)  
        glScalef(1, 1, 1)  
        draw_triangle()
    elif enemy_type == "tough":
        # Tough enemy - Triangle front + rectangular body (2x bigger)
        glColor3f(0.8, 0.4, 0)  
        glScalef(2, 2, 2) 
        
        # Front triangle
        glPushMatrix()
        glTranslatef(0, 0, 10)
        draw_triangle()
        glPopMatrix()
        
        # Rectangular body
        glColor3f(0.6, 0.3, 0)
        glPushMatrix()
        glScalef(0.8, 0.6, 1.5)
        glutSolidCube(15)
        glPopMatrix()
        
    elif enemy_type == "boss":
        # Boss enemy - Scary design (5x bigger)
        glScalef(3, 3, 3)  
        draw_scary_boss()
    
    glPopMatrix()

def draw_boss_health_bar():
 
    for enemy in enemies:
        if enemy["type"] == "boss":
            hp_percent = enemy["hp"] / enemy["max_hp"]
            
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            gluOrtho2D(0, 1000, 0, 800)
            
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()
            
            # Background bar
            glColor3f(0.3, 0.3, 0.3)
            glBegin(GL_QUADS)
            glVertex2f(200, 750)
            glVertex2f(800, 750)
            glVertex2f(800, 720)
            glVertex2f(200, 720)
            glEnd()
            
            # Health bar
            glColor3f(1, 0, 0)
            glBegin(GL_QUADS)
            glVertex2f(200, 750)
            glVertex2f(200 + 600 * hp_percent, 750)
            glVertex2f(200 + 600 * hp_percent, 720)
            glVertex2f(200, 720)
            glEnd()
            
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
            break

def spawn_enemy():
   
    angle = math.radians(random.uniform(-30, 30))
    distance = random.uniform(300, 500)
    x = player_pos[0] + math.sin(angle) * distance
    z = player_pos[2] + math.cos(angle) * distance
    y = random.uniform(-20, 50)
    
    if random.random() < 0.7:
        enemies.append({"pos": [x, y, z], "type": "normal", "hp": 1, "score": 2, "speed": 0.4})
    else:
        enemies.append({"pos": [x, y, z], "type": "tough", "hp": 3, "score": 5, "speed": 0.6})

def spawn_boss():
    
    global is_boss_active, boss_warning_timer
    is_boss_active = True
    enemies.clear()
    
    distance = 400
    angle = math.radians(0) 
    x = player_pos[0] + math.sin(angle) * distance
    z = player_pos[2] + math.cos(angle) * distance
    
    enemies.append({"pos": [x, 50, z], "type": "boss", "hp": 10, "max_hp": 10, "score": 10, "speed": 0.3})
    boss_warning_timer = 180

def update_game_state_enemies():
    global player_score, is_boss_active, is_game_over
    
    # Move enemies towards player
    for enemy in enemies:
        dx = player_pos[0] - enemy["pos"][0]
        dy = player_pos[1] - enemy["pos"][1]
        dz = player_pos[2] - enemy["pos"][2]
        dist = math.sqrt(dx**2 + dy**2 + dz**2)
        
        if dist > 0:
            speed = enemy.get("speed", 0.3)
            enemy["pos"][0] += (dx / dist) * speed
            enemy["pos"][1] += (dy / dist) * speed * 0.2
            enemy["pos"][2] += (dz / dist) * speed

    # Bullet-Enemy collisions
    bullets_to_remove = []
    enemies_to_remove = []
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            distance = math.sqrt(
                (bullet["pos"][0] - enemy["pos"][0])**2 +
                (bullet["pos"][1] - enemy["pos"][1])**2 +
                (bullet["pos"][2] - enemy["pos"][2])**2
            )
            collision_radius = 15 if enemy["type"] == "normal" else 30 if enemy["type"] == "tough" else 60
            
            if distance < collision_radius:
                enemy["hp"] -= 1
                if enemy["hp"] <= 0:
                    player_score += enemy["score"]
                    enemies_to_remove.append(enemy)
                    if enemy["type"] == "boss":
                        is_boss_active = False
                bullets_to_remove.append(bullet)
                break
    
    for bullet in bullets_to_remove:
        if bullet in bullets:
            bullets.remove(bullet)
    for enemy in enemies_to_remove:
        if enemy in enemies:
            enemies.remove(enemy)

    # Player-Enemy collisions
    global player_lives 
    if not shield_active:
        for enemy in enemies[:]:
            distance = math.sqrt(
                (player_pos[0] - enemy["pos"][0])**2 +
                (player_pos[1] - enemy["pos"][1])**2 +
                (player_pos[2] - enemy["pos"][2])**2
            )
            collision_radius = 25 if enemy["type"] == "normal" else 45 if enemy["type"] == "tough" else 75
            
            if distance < collision_radius:
                if not cheat_mode:
                    if enemy["type"] == "boss":
                        player_lives = 0
                    else:
                        player_lives -= 1
                enemies.remove(enemy)
                if player_lives <= 0:
                    is_game_over = True
                break

    # Boss spawning logic
    if (player_score > 0 and player_score % BOSS_SCORE_INTERVAL == 0 and 
        not is_boss_active and len([e for e in enemies if e["type"] == "boss"]) == 0):
        spawn_boss()
        
    # Enemy spawning 
    global enemy_spawn_timer
    enemy_spawn_timer += 1
    if not is_boss_active and len(enemies) < 3 and enemy_spawn_timer > 120:
        spawn_enemy()
        enemy_spawn_timer = 0
    
    if boss_warning_timer > 0:
        boss_warning_timer -= 1


def idle():
   
    if is_paused or is_game_over:
        glutPostRedisplay()
        return

    update_game_state_enemies()
    glutPostRedisplay()

def showScreen():
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    for enemy in enemies:
        draw_enemy(enemy)
        
    if is_boss_active:
        draw_boss_health_bar()
        
    if boss_warning_timer > 0:
        draw_text(320, 500, "BOSS APPROACHING!", GLUT_BITMAP_TIMES_ROMAN_24)

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
    
    glutMainLoop()

if __name__ == "__main__":
    main()