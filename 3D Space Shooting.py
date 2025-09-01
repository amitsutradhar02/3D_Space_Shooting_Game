# Player and Input Module
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18, GLUT_BITMAP_TIMES_ROMAN_24, GLUT_BITMAP_HELVETICA_12, GLUT_BITMAP_HELVETICA_10
import math
import random
import time


camera_pos = [0, 200, 200]
player_pos = [0, 0, 0]      
player_rot_y = 0            
player_lives = 10          
player_score = 0            
is_paused = False           
is_game_over = False        
camera_mode = 0             
cheat_mode = False          
shoot_mode = 0              
is_boss_active = False      
boss_warning_timer = 0      
shield_active = False       
shield_timer = 0           
auto_aim = False           

# Game object lists
bullets = []
enemies = []  
collectibles = []
obstacles = []
stars = []

# Game parameters
bullet_cooldown = 0.2
last_bullet_time = 0.0


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    """Draws text on the screen at a fixed position."""
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

def draw_bullet(pos):
    """Draws a bullet as a yellow cube."""
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    glColor3f(1, 1, 0)  
    glutSolidCube(8)
    glPopMatrix()

def draw_player_spaceship():
    """Draws the player's ship with a cone, cube, and wings."""
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(player_rot_y, 0, 1, 0)
    
    # Shield effect
    if shield_active:
        glColor4f(0, 1, 1, 0.3)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        gluSphere(gluNewQuadric(), 50, 10, 10)
        glDisable(GL_BLEND)
    
    # Body (Cube) 
    glColor3f(0.5, 0.5, 0.5)
    glPushMatrix()
    glScalef(1.0, 0.5, 1.5)
    glutSolidCube(25)
    glPopMatrix()
    
    # Wings (Cubes) 
    glColor3f(0, 0, 1)  
    glPushMatrix()
    glTranslatef(18, 0, -6)
    glScalef(0.3, 0.1, 0.6)
    glutSolidCube(25)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(-18, 0, -6)
    glScalef(0.3, 0.1, 0.6)
    glutSolidCube(25)
    glPopMatrix()
    
    glPopMatrix()

def find_nearest_enemy():
    if not enemies:
        return None
    
    nearest_enemy = None
    nearest_distance = float('inf')
    
    for enemy in enemies:
        dx = enemy["pos"][0] - player_pos[0]
        dy = enemy["pos"][1] - player_pos[1]
        dz = enemy["pos"][2] - player_pos[2]
        distance = math.sqrt(dx**2 + dy**2 + dz**2)
        
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_enemy = enemy
    
    return nearest_enemy

def get_aim_direction():
    if auto_aim:
        target = find_nearest_enemy()
        if target:
            dx = target["pos"][0] - player_pos[0]
            dy = target["pos"][1] - player_pos[1]
            dz = target["pos"][2] - player_pos[2]
            length = math.sqrt(dx**2 + dy**2 + dz**2)
            if length > 0:
                return [dx/length, dy/length, dz/length]
    
    # Default direction (where player is facing)
    angle = math.radians(player_rot_y)
    return [math.sin(angle), 0, math.cos(angle)]

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 1.25, 0.1, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if camera_mode == 0: 
        angle = math.radians(player_rot_y)
        cam_x = player_pos[0] - math.sin(angle) * 200
        cam_y = player_pos[1] + 100
        cam_z = player_pos[2] - math.cos(angle) * 200
        gluLookAt(cam_x, cam_y, cam_z,
                  player_pos[0], player_pos[1], player_pos[2],
                  0, 1, 0)
    elif camera_mode == 1: 
        angle = math.radians(player_rot_y)
        cam_x = player_pos[0]
        cam_y = player_pos[1] + 10
        cam_z = player_pos[2]
        gluLookAt(cam_x, cam_y, cam_z,
                  player_pos[0] + math.sin(angle) * 100,
                  player_pos[1],
                  player_pos[2] + math.cos(angle) * 100,
                  0, 1, 0)

def keyboardListener(key, x, y):
    """Handles keyboard inputs for player movement and game state."""
    global player_pos, player_rot_y, is_paused, cheat_mode, last_bullet_time, shoot_mode, is_game_over, auto_aim
    
    if is_game_over and key not in (b'r', b'R'):
        return
        
    # Movement keys
    if key in (b'w', b'W'):
        angle = math.radians(player_rot_y)
        player_pos[0] += math.sin(angle) * 15
        player_pos[2] += math.cos(angle) * 15
    elif key in (b's', b'S'):
        angle = math.radians(player_rot_y)
        player_pos[0] -= math.sin(angle) * 15
        player_pos[2] -= math.cos(angle) * 15
    elif key in (b'a', b'A'):
        player_rot_y += 5
    elif key in (b'd', b'D'):
        player_rot_y -= 5
    
    # Game control keys
    if key in (b'p', b'P'):
        is_paused = not is_paused
    elif key in (b'r', b'R'):
        reset_game()
    elif key in (b'c', b'C'):
        cheat_mode = not cheat_mode
    elif key in (b'v', b'V'):
        global camera_mode
        camera_mode = 1 - camera_mode
    elif key in (b'f', b'F'):  # Auto-aim toggle
        auto_aim = not auto_aim
    elif key == b' ':  # Spacebar for shooting
        fire_bullet()
    
    glutPostRedisplay()

def specialKeyListener(key, x, y):
    global shoot_mode, player_pos
    
    if key == GLUT_KEY_LEFT and glutGetModifiers() & GLUT_ACTIVE_SHIFT:
        shoot_mode = (shoot_mode + 1) % 2 
    elif key == GLUT_KEY_UP:
        player_pos[1] += 10  # Move up
    elif key == GLUT_KEY_DOWN:
        player_pos[1] -= 10  # Move down
        if player_pos[1] < -10: 
            player_pos[1] = -10
    
    glutPostRedisplay()

def mouseListener(button, state, x, y):
    """Handles mouse inputs for shooting and camera views."""
    global camera_mode
    
    # Left mouse button fires a bullet
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        fire_bullet()

    # Right mouse button toggles camera views
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        camera_mode = 1 - camera_mode

    glutPostRedisplay()

def fire_bullet():
    """Fires bullets based on the current shooting mode and auto-aim."""
    global last_bullet_time
    
    current_time = time.time()
    if current_time - last_bullet_time < bullet_cooldown:
        return
        
    aim_direction = get_aim_direction()
    
    if shoot_mode == 0:  
        bullet_vel = [aim_direction[0] * 20, aim_direction[1] * 20, aim_direction[2] * 20]
        bullets.append({"pos": [player_pos[0], player_pos[1], player_pos[2]], "vel": bullet_vel})
    elif shoot_mode == 1:  
        for i in range(-1, 2):
            if auto_aim:
           
                spread_x = aim_direction[0] + i * 0.3
                spread_z = aim_direction[2] + i * 0.3
               
                length = math.sqrt(spread_x**2 + aim_direction[1]**2 + spread_z**2)
                if length > 0:
                    bullet_vel = [spread_x/length * 15, aim_direction[1]/length * 15, spread_z/length * 15]
                else:
                    bullet_vel = [i * 5, 0, 15]
            else:
              
                spread_angle = math.radians(player_rot_y + i * 15)
                bullet_vel = [math.sin(spread_angle) * 15, 0, math.cos(spread_angle) * 15]
            
            bullets.append({"pos": [player_pos[0], player_pos[1], player_pos[2]], "vel": bullet_vel})
    
    last_bullet_time = current_time

def update_game_state_player():

    global shield_timer, shield_active
    
 
    if shield_active:
        shield_timer -= 1/60
        if shield_timer <= 0:
            shield_active = False

    # Move bullets
    bullets_to_remove = []
    for bullet in bullets[:]:
        bullet["pos"][0] += bullet["vel"][0]
        bullet["pos"][1] += bullet["vel"][1]
        bullet["pos"][2] += bullet["vel"][2]
        
        # Remove bullets that are too far away
        distance_from_player = math.sqrt(
            (bullet["pos"][0] - player_pos[0])**2 +
            (bullet["pos"][1] - player_pos[1])**2 +
            (bullet["pos"][2] - player_pos[2])**2
        )
        if distance_from_player > 1000:
            bullets_to_remove.append(bullet)
    
    for bullet in bullets_to_remove:
        if bullet in bullets:
            bullets.remove(bullet)
            
    # Auto-fire in cheat mode
    if cheat_mode:
        current_time = time.time()
        if current_time - last_bullet_time > 0.1:
            fire_bullet()

def reset_game():

    global player_pos, player_rot_y, player_lives, player_score, is_game_over, is_boss_active, shield_active, shield_timer, boss_warning_timer, auto_aim
    
    player_pos = [0, 0, 0]
    player_rot_y = 0
    player_lives = 10
    player_score = 0
    is_game_over = False
    is_boss_active = False
    shield_active = False
    shield_timer = 0
    boss_warning_timer = 0
    auto_aim = False
    bullets.clear()
    enemies.clear()
    collectibles.clear()
    obstacles.clear()

def idle():
    
    if is_paused or is_game_over:
        glutPostRedisplay()
        return

    update_game_state_player()
    glutPostRedisplay()

def showScreen():

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setupCamera()

    # Draw all game objects
    if camera_mode == 0:  
        draw_player_spaceship()

    for bullet in bullets:
        draw_bullet(bullet["pos"])

    # Draw HUD
    draw_text(10, 770, f"LIVES: {player_lives}")
    draw_text(10, 750, f"SCORE: {player_score}")
    
    # Shooting mode indicator
    mode_text = "SINGLE MODE" if shoot_mode == 0 else "SPREAD MODE"
    draw_text(10, 730, mode_text)
    
    # Camera mode indicator
    cam_text = "THIRD-PERSON" if camera_mode == 0 else "FIRST-PERSON"
    draw_text(10, 710, f"CAMERA: {cam_text}")
    
    # Auto-aim indicator
    aim_text = "AUTO-AIM: ON" if auto_aim else "AUTO-AIM: OFF"
    draw_text(10, 690, aim_text)
    
    # Shield indicator
    if shield_active:
        draw_text(10, 670, f"SHIELD: {shield_timer:.1f}s")
    
    # Cheat mode indicator
    if cheat_mode:
        draw_text(10, 650, "CHEAT MODE ON")
    
    # Game state messages
    if is_paused:
        draw_text(400, 400, "PAUSED", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(350, 370, "Press P to resume", GLUT_BITMAP_HELVETICA_18)
        
    if is_game_over:
        draw_text(380, 400, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(350, 370, "Press R to restart", GLUT_BITMAP_HELVETICA_18)

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"3D Space Shooter")

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.0, 0.0, 0.1, 1.0)
    
    reset_game()

    glutMainLoop()

if __name__ == "__main__":
    main()