from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18, GLUT_BITMAP_TIMES_ROMAN_24, GLUT_BITMAP_HELVETICA_12, GLUT_BITMAP_HELVETICA_10
import math
import random
import time

# Global Game State Variables 
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
enemy_spawn_timer = 0
collectible_spawn_timer = 0
obstacle_spawn_timer = 0
BOSS_SCORE_INTERVAL = 50  

# Initialize starfield
def init_starfield():
    global stars
    stars = []
    for _ in range(200):
        x = random.uniform(-800, 800)
        y = random.uniform(-800, 800)
        z = random.uniform(-1000, 1000)
        stars.append([x, y, z])

# Initialize obstacles
def init_obstacles():
    global obstacles
    obstacles = []
    for _ in range(15): 
        x = random.uniform(-600, 600)
        y = random.uniform(-50, 100)
        z = random.uniform(-600, 600)
        if abs(x) > 100 or abs(z) > 100:
            obstacles.append({"pos": [x, y, z], "type": "asteroid"})

# Drawing Functions
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
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

def draw_player_spaceship():
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

def draw_bullet(pos):
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    glColor3f(1, 1, 0)  
    glutSolidCube(8)
    glPopMatrix()

def draw_collectible(collectible_data):
    pos = collectible_data["pos"]
    item_type = collectible_data["type"]
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    
    if item_type == "health":
        glColor3f(1, 0.2, 0.5)  # Pink/red for love heart
        draw_3d_heart()
    elif item_type == "shield":
        glColor3f(1, 1, 0)  # Yellow sphere (Shield)
        gluSphere(gluNewQuadric(), 12, 8, 8)
    elif item_type == "score":
        glColor3f(1, 0.5, 0)  # Red-orange gem (Score)
        glPushMatrix()
        glRotatef(glutGet(GLUT_ELAPSED_TIME) * 0.1, 0, 1, 0)  # Rotating gem
        gluSphere(gluNewQuadric(), 10, 8, 8)
        glPopMatrix()
    
    glPopMatrix()

def draw_obstacle(obstacle_data):
    pos = obstacle_data["pos"]
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    
    if obstacle_data["type"] == "asteroid":
        glColor3f(0.4, 0.4, 0.4)  # Gray asteroid
        glPushMatrix()
        glRotatef(glutGet(GLUT_ELAPSED_TIME) * 0.05, 1, 1, 0)  # Slow rotation
        
        # Create irregular asteroid shape
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
            
            # Restore matrices
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
            break

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
    
    angle = math.radians(player_rot_y)
    return [math.sin(angle), 0, math.cos(angle)]

def keyboardListener(key, x, y):
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
    elif key in (b'f', b'F'): 
        auto_aim = not auto_aim
    elif key == b' ': 
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
        if player_pos[1] < -10:  # Don't go too low
            player_pos[1] = -10
    
    glutPostRedisplay()

def mouseListener(button, state, x, y):
    global camera_mode
    
    # Left mouse button fires a bullet
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        fire_bullet()

    # Right mouse button toggles camera views
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        camera_mode = 1 - camera_mode

    glutPostRedisplay()

def fire_bullet():
    global last_bullet_time
    
    current_time = time.time()
    if current_time - last_bullet_time < bullet_cooldown:
        return
        
    aim_direction = get_aim_direction()
    
    if shoot_mode == 0:  # Single Shot Mode
        bullet_vel = [aim_direction[0] * 20, aim_direction[1] * 20, aim_direction[2] * 20]
        bullets.append({"pos": [player_pos[0], player_pos[1], player_pos[2]], "vel": bullet_vel})
    elif shoot_mode == 1:  # Spread Shot Mode
        for i in range(-1, 2):
            if auto_aim:
                # For auto-aim spread, create slight variations of the aim direction
                spread_x = aim_direction[0] + i * 0.3
                spread_z = aim_direction[2] + i * 0.3
                # Normalize
                length = math.sqrt(spread_x**2 + aim_direction[1]**2 + spread_z**2)
                if length > 0:
                    bullet_vel = [spread_x/length * 15, aim_direction[1]/length * 15, spread_z/length * 15]
                else:
                    bullet_vel = [i * 5, 0, 15]
            else:
                # Normal spread shot
                spread_angle = math.radians(player_rot_y + i * 15)
                bullet_vel = [math.sin(spread_angle) * 15, 0, math.cos(spread_angle) * 15]
            
            bullets.append({"pos": [player_pos[0], player_pos[1], player_pos[2]], "vel": bullet_vel})
    
    last_bullet_time = current_time

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 1.25, 0.1, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if camera_mode == 0:  # Third-person view
        angle = math.radians(player_rot_y)
        cam_x = player_pos[0] - math.sin(angle) * 200
        cam_y = player_pos[1] + 100
        cam_z = player_pos[2] - math.cos(angle) * 200
        gluLookAt(cam_x, cam_y, cam_z,
                  player_pos[0], player_pos[1], player_pos[2],
                  0, 1, 0)
    elif camera_mode == 1:  # First-person view
        angle = math.radians(player_rot_y)
        cam_x = player_pos[0]
        cam_y = player_pos[1] + 10
        cam_z = player_pos[2]
        gluLookAt(cam_x, cam_y, cam_z,
                  player_pos[0] + math.sin(angle) * 100,
                  player_pos[1],
                  player_pos[2] + math.cos(angle) * 100,
                  0, 1, 0)

def spawn_enemy():
   
    angle = math.radians(player_rot_y)
    
    spread_angle = random.uniform(-30, 30)
    spawn_angle = math.radians(player_rot_y + spread_angle)
    
 
    distance = random.uniform(300, 500)
    

    x = player_pos[0] + math.sin(spawn_angle) * distance
    z = player_pos[2] + math.cos(spawn_angle) * distance
    y = random.uniform(-20, 50)
    
    if random.random() < 0.7:  
        enemies.append({"pos": [x, y, z], "type": "normal", "hp": 1, "score": 2, "speed": 0.4})
    else:  
        enemies.append({"pos": [x, y, z], "type": "tough", "hp": 3, "score": 5, "speed": 0.6})

def spawn_boss():
    global is_boss_active
    is_boss_active = True
    enemies.clear()
    
    angle = math.radians(player_rot_y)
    
    distance = 400  
    x = player_pos[0] + math.sin(angle) * distance
    z = player_pos[2] + math.cos(angle) * distance
    
    enemies.append({"pos": [x, 50, z], "type": "boss", "hp": 10, "max_hp": 10, "score": 10, "speed": 0.3})

def spawn_collectible():

    angle = random.uniform(0, 2 * math.pi)  # Full circle around player
    distance = random.uniform(150, 400)
    x = player_pos[0] + math.cos(angle) * distance
    z = player_pos[2] + math.sin(angle) * distance
    y = random.uniform(0, 30)
    
    item_type = random.choices(["health", "shield", "score"], weights=[0.5, 0.2, 0.3])[0]
    collectibles.append({"pos": [x, y, z], "type": item_type})

def update_game_state():
    global player_lives, player_score, is_game_over, is_boss_active, shield_timer, shield_active

    # Update shield timer
    if shield_active:
        shield_timer -= 1/60
        if shield_timer <= 0:
            shield_active = False

    # Move bullets
    bullets_to_remove = []
    for bullet in bullets:
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
            if enemy["type"] == "normal":
                collision_radius = 15
            elif enemy["type"] == "tough":
                collision_radius = 30  # 2x bigger
            elif enemy["type"] == "boss":
                collision_radius = 60  # Much bigger for boss
            
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
    if not shield_active:
        for enemy in enemies[:]:
            distance = math.sqrt(
                (player_pos[0] - enemy["pos"][0])**2 +
                (player_pos[1] - enemy["pos"][1])**2 +
                (player_pos[2] - enemy["pos"][2])**2
            )
            if enemy["type"] == "normal":
                collision_radius = 25
            elif enemy["type"] == "tough":
                collision_radius = 45  # 2x bigger
            elif enemy["type"] == "boss":
                collision_radius = 75  # Boss collision - instant death
                if distance < collision_radius and not cheat_mode:
                    player_lives = 0  # Boss kills instantly
                    enemies.remove(enemy)
                    break
            
            if distance < collision_radius and enemy["type"] != "boss":
                if not cheat_mode:
                    player_lives -= 1
                enemies.remove(enemy)
                break

    # Player-Obstacle collisions
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

    # Player-Collectible collisions
    collectibles_to_remove = []
    for collectible in collectibles:
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
                shield_timer = 5.0  
            elif collectible["type"] == "score":
                player_score += 10
            collectibles_to_remove.append(collectible)

    for collectible in collectibles_to_remove:
        if collectible in collectibles:
            collectibles.remove(collectible)

    # Check for game over
    if player_lives <= 0 and not cheat_mode:
        is_game_over = True

    # Boss spawning logic
    if (player_score > 0 and player_score % BOSS_SCORE_INTERVAL == 0 and 
        not is_boss_active and len([e for e in enemies if e["type"] == "boss"]) == 0):
        global boss_warning_timer
        spawn_boss()
        boss_warning_timer = 180  

def reset_game():
    global player_pos, player_rot_y, player_lives, player_score, is_game_over, is_boss_active, shield_active, shield_timer, boss_warning_timer
    
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
    init_obstacles()  
def idle():
    global enemy_spawn_timer, collectible_spawn_timer, boss_warning_timer

    if is_paused or is_game_over:
        glutPostRedisplay()
        return

    update_game_state()

    enemy_spawn_timer += 1
    if not is_boss_active and len(enemies) < 3 and enemy_spawn_timer > 120: 
        spawn_enemy()
        enemy_spawn_timer = 0

    collectible_spawn_timer += 1
    if collectible_spawn_timer > 200 and len(collectibles) < 4:  
        spawn_collectible()
        collectible_spawn_timer = 0

    # Auto-fire in cheat mode
    if cheat_mode:
        current_time = time.time()
        if current_time - last_bullet_time > 0.1:
            fire_bullet()

    # Boss warning timer
    if boss_warning_timer > 0:
        boss_warning_timer -= 1

    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setupCamera()

    # Draw starfield background
    draw_starfield()

    # Draw static obstacles
    for obstacle in obstacles:
        draw_obstacle(obstacle)

    # Draw all game objects
    if camera_mode == 0: 
        draw_player_spaceship()

    for enemy in enemies:
        draw_enemy(enemy)

    for bullet in bullets:
        draw_bullet(bullet["pos"])

    for collectible in collectibles:
        draw_collectible(collectible)

    # Draw boss health bar if boss is active
    if is_boss_active:
        draw_boss_health_bar()

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

    if boss_warning_timer > 0:
        draw_text(320, 500, "BOSS APPROACHING!", GLUT_BITMAP_TIMES_ROMAN_24)

    # Controls help
    draw_text(750, 80, "Controls:", GLUT_BITMAP_HELVETICA_12)
    draw_text(750, 65, "W/S: Forward/Back", GLUT_BITMAP_HELVETICA_10)
    draw_text(750, 52, "A/D: Turn Left/Right", GLUT_BITMAP_HELVETICA_10)
    draw_text(750, 39, "UP/DOWN: Move Up/Down", GLUT_BITMAP_HELVETICA_10)
    draw_text(750, 26, "SPACE: Shoot", GLUT_BITMAP_HELVETICA_10)
    draw_text(750, 13, "F: Toggle Auto-Aim", GLUT_BITMAP_HELVETICA_10)
    draw_text(750, 0, "Shift+Left: Shoot Mode", GLUT_BITMAP_HELVETICA_10)

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Enhanced 3D Space Shooter")

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.0, 0.0, 0.1, 1.0)  # Dark blue background
    
    # Initialize game
    init_starfield()
    init_obstacles()
    reset_game()

    glutMainLoop()

if __name__ == "__main__":
    main()
