"""
Script de visualisation du système de suivi de ligne
Crée un diagramme expliquant le fonctionnement
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def create_system_diagram():
    """Crée un diagramme du système de suivi de ligne"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Système de Suivi de Ligne Autonome', fontsize=16, fontweight='bold')
    
    # 1. Architecture du système
    ax1 = axes[0, 0]
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.axis('off')
    ax1.set_title('Architecture du Système', fontweight='bold')
    
    # Éléments du système
    boxes = [
        {'pos': (1, 8), 'size': (3, 1), 'text': 'PiCamera', 'color': 'lightblue'},
        {'pos': (1, 6), 'size': (3, 1), 'text': 'Détection\nde Ligne', 'color': 'lightgreen'},
        {'pos': (1, 4), 'size': (3, 1), 'text': 'Calcul de\nCommande', 'color': 'lightyellow'},
        {'pos': (1, 2), 'size': (3, 1), 'text': 'Arduino', 'color': 'lightcoral'},
        {'pos': (1, 0.5), 'size': (3, 1), 'text': 'Moteurs', 'color': 'lightgray'},
    ]
    
    for box in boxes:
        rect = patches.Rectangle(box['pos'], box['size'][0], box['size'][1],
                                linewidth=2, edgecolor='black', facecolor=box['color'])
        ax1.add_patch(rect)
        ax1.text(box['pos'][0] + box['size'][0]/2, box['pos'][1] + box['size'][1]/2,
                box['text'], ha='center', va='center', fontweight='bold')
    
    # Flèches
    arrows = [(2.5, 8), (2.5, 6), (2.5, 4), (2.5, 2), (2.5, 0.5)]
    for i in range(len(arrows)-1):
        ax1.arrow(arrows[i][0], arrows[i][1]-0.5, 0, -0.8,
                 head_width=0.3, head_length=0.2, fc='black', ec='black')
    
    # Feedback loop
    ax1.annotate('', xy=(5, 8.5), xytext=(5, 1),
                arrowprops=dict(arrowstyle='->', lw=2, color='red', linestyle='dashed'))
    ax1.text(5.5, 4.5, 'Feedback\nLoop', color='red', fontweight='bold', rotation=90)
    
    # 2. Détection de ligne (exemple visuel)
    ax2 = axes[0, 1]
    ax2.set_xlim(0, 160)
    ax2.set_ylim(0, 128)
    ax2.set_title('Détection de Ligne', fontweight='bold')
    ax2.set_xlabel('X (pixels)')
    ax2.set_ylabel('Y (pixels)')
    
    # Ligne simulée (courbe)
    x_line = np.linspace(60, 100, 100)
    y_line = np.linspace(0, 128, 100)
    ax2.plot(x_line, y_line, 'white', linewidth=10, label='Ligne blanche')
    ax2.set_facecolor('gray')
    
    # Centroïde
    cx, cy = 80, 64
    ax2.plot(cx, cy, 'ro', markersize=10, label=f'Centroïde ({cx}, {cy})')
    
    # Centre de l'image
    center_x = 80
    ax2.axvline(center_x, color='blue', linestyle='--', linewidth=2, label='Centre image')
    
    # Zone morte
    dead_zone = 10
    ax2.axvline(center_x - dead_zone, color='yellow', linestyle=':', linewidth=1, alpha=0.5)
    ax2.axvline(center_x + dead_zone, color='yellow', linestyle=':', linewidth=1, alpha=0.5)
    ax2.fill_betweenx([0, 128], center_x - dead_zone, center_x + dead_zone,
                      color='yellow', alpha=0.2, label='Zone morte')
    
    ax2.legend(loc='upper right', fontsize=8)
    ax2.grid(True, alpha=0.3)
    
    # 3. Calcul de la commande
    ax3 = axes[1, 0]
    ax3.set_xlim(-80, 80)
    ax3.set_ylim(0, 120)
    ax3.set_title('Commande de Direction', fontweight='bold')
    ax3.set_xlabel('Erreur (pixels)')
    ax3.set_ylabel('Vitesse moteur')
    
    # Courbes de vitesse en fonction de l'erreur
    errors = np.linspace(-80, 80, 100)
    left_speeds = []
    right_speeds = []
    
    dead_zone = 10
    base_speed = 100
    
    for error in errors:
        if abs(error) < dead_zone:
            left_speeds.append(base_speed)
            right_speeds.append(base_speed)
        elif error < 0:
            correction = min(abs(error) / 80, 1.0)
            left_speeds.append(base_speed * (1 - correction * 0.5))
            right_speeds.append(base_speed)
        else:
            correction = min(error / 80, 1.0)
            left_speeds.append(base_speed)
            right_speeds.append(base_speed * (1 - correction * 0.5))
    
    ax3.plot(errors, left_speeds, 'b-', linewidth=2, label='Moteur gauche')
    ax3.plot(errors, right_speeds, 'r-', linewidth=2, label='Moteur droit')
    ax3.axvline(0, color='gray', linestyle='--', linewidth=1)
    ax3.axvline(-dead_zone, color='yellow', linestyle=':', linewidth=1, alpha=0.5)
    ax3.axvline(dead_zone, color='yellow', linestyle=':', linewidth=1, alpha=0.5)
    ax3.fill_betweenx([0, 120], -dead_zone, dead_zone,
                     color='yellow', alpha=0.2, label='Zone morte')
    
    ax3.legend(loc='upper right')
    ax3.grid(True, alpha=0.3)
    
    # Annotations
    ax3.annotate('Tourne à gauche', xy=(-40, 75), xytext=(-60, 90),
                arrowprops=dict(arrowstyle='->', lw=1.5), fontsize=9)
    ax3.annotate('Tourne à droite', xy=(40, 75), xytext=(50, 90),
                arrowprops=dict(arrowstyle='->', lw=1.5), fontsize=9)
    ax3.annotate('Tout droit', xy=(0, 100), xytext=(15, 110),
                arrowprops=dict(arrowstyle='->', lw=1.5), fontsize=9)
    
    # 4. États du robot
    ax4 = axes[1, 1]
    ax4.set_xlim(-5, 5)
    ax4.set_ylim(-2, 8)
    ax4.axis('off')
    ax4.set_title('États de Navigation', fontweight='bold')
    
    # Robot (vue du dessus)
    def draw_robot(ax, x, y, left_speed, right_speed, label):
        # Corps
        rect = patches.Rectangle((x-0.3, y-0.5), 0.6, 1, 
                                linewidth=2, edgecolor='black', facecolor='lightgray')
        ax.add_patch(rect)
        
        # Roues
        # Gauche
        left_color = 'green' if left_speed > 80 else 'orange' if left_speed > 50 else 'red'
        left_wheel = patches.Rectangle((x-0.4, y-0.3), 0.1, 0.6,
                                      linewidth=1, edgecolor='black', facecolor=left_color)
        ax.add_patch(left_wheel)
        
        # Droite
        right_color = 'green' if right_speed > 80 else 'orange' if right_speed > 50 else 'red'
        right_wheel = patches.Rectangle((x+0.3, y-0.3), 0.1, 0.6,
                                       linewidth=1, edgecolor='black', facecolor=right_color)
        ax.add_patch(right_wheel)
        
        # Flèche de direction
        if left_speed == right_speed:
            ax.arrow(x, y+0.5, 0, 0.5, head_width=0.2, head_length=0.15, fc='blue', ec='blue')
        elif left_speed < right_speed:
            ax.annotate('', xy=(x-0.3, y+0.7), xytext=(x, y+0.5),
                       arrowprops=dict(arrowstyle='->', lw=2, color='blue'))
        else:
            ax.annotate('', xy=(x+0.3, y+0.7), xytext=(x, y+0.5),
                       arrowprops=dict(arrowstyle='->', lw=2, color='blue'))
        
        # Label
        ax.text(x, y-1.2, label, ha='center', fontsize=9, fontweight='bold')
        ax.text(x-0.5, y-1.5, f'L:{left_speed}', ha='center', fontsize=7, color=left_color)
        ax.text(x+0.5, y-1.5, f'R:{right_speed}', ha='center', fontsize=7, color=right_color)
    
    # Trois états
    draw_robot(ax4, -3, 5, 100, 100, 'Ligne centrée\n(Tout droit)')
    draw_robot(ax4, 0, 5, 50, 100, 'Ligne à gauche\n(Tourne gauche)')
    draw_robot(ax4, 3, 5, 100, 50, 'Ligne à droite\n(Tourne droite)')
    
    # Légende des couleurs
    ax4.text(-4, 1, 'Vitesse:', fontsize=9, fontweight='bold')
    ax4.add_patch(patches.Rectangle((-4, 0.5), 0.3, 0.3, facecolor='green', edgecolor='black'))
    ax4.text(-3.5, 0.65, 'Rapide (>80)', fontsize=8, va='center')
    ax4.add_patch(patches.Rectangle((-4, 0), 0.3, 0.3, facecolor='orange', edgecolor='black'))
    ax4.text(-3.5, 0.15, 'Moyen (50-80)', fontsize=8, va='center')
    ax4.add_patch(patches.Rectangle((-4, -0.5), 0.3, 0.3, facecolor='red', edgecolor='black'))
    ax4.text(-3.5, -0.35, 'Lent (<50)', fontsize=8, va='center')
    
    plt.tight_layout()
    plt.savefig('line_tracking_system.png', dpi=300, bbox_inches='tight')
    print("✓ Diagramme sauvegardé : line_tracking_system.png")
    plt.show()

if __name__ == "__main__":
    print("Génération du diagramme du système...")
    create_system_diagram()
