import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk
import random

class LifeSimulation:
    def __init__(self, root):
        self.root = root
        self.root.title("Life Simulation Prototype")
        
        # Simulation parameters
        self.running = False
        self.time_step = 0
        
        # Initialize organisms (x, y, species_id, energy, age)
        self.organisms = np.array([
            [random.randint(50, 750), random.randint(50, 550), 0, 100, 0] 
            for _ in range(50)
        ] + [
            [random.randint(50, 750), random.randint(50, 550), 1, 100, 0] 
            for _ in range(30)
        ])
        
        # Species data
        self.species_data = pd.DataFrame({
            'species_id': [0, 1],
            'name': ['Species A', 'Species B'],
            'birth_rate': [0.02, 0.015],
            'death_rate': [0.01, 0.008],
            'color': ['red', 'blue']
        })
        
        # History for graphing
        self.history = pd.DataFrame(columns=['time', 'species_0', 'species_1'])
        
        self.setup_ui()
        
    def setup_ui(self):
        # Control panel
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Buttons
        self.start_btn = ttk.Button(control_frame, text="Start", command=self.start_simulation)
        self.start_btn.grid(row=0, column=0, padx=5)
        
        self.pause_btn = ttk.Button(control_frame, text="Pause", command=self.pause_simulation)
        self.pause_btn.grid(row=0, column=1, padx=5)
        
        self.reset_btn = ttk.Button(control_frame, text="Reset", command=self.reset_simulation)
        self.reset_btn.grid(row=0, column=2, padx=5)
        
        # Parameters
        ttk.Label(control_frame, text="Birth Rate:").grid(row=0, column=3, padx=5)
        self.birth_scale = ttk.Scale(control_frame, from_=0.001, to=0.05, orient=tk.HORIZONTAL)
        self.birth_scale.set(0.02)
        self.birth_scale.grid(row=0, column=4, padx=5)
        
        ttk.Label(control_frame, text="Death Rate:").grid(row=0, column=5, padx=5)
        self.death_scale = ttk.Scale(control_frame, from_=0.001, to=0.05, orient=tk.HORIZONTAL)
        self.death_scale.set(0.01)
        self.death_scale.grid(row=0, column=6, padx=5)
        
        # Canvas for organisms
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg='white')
        self.canvas.grid(row=1, column=0, padx=10, pady=10)
        
        # Matplotlib graph
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Population')
        self.ax.set_title('Population Over Time')
        
        self.graph_canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.graph_canvas.get_tk_widget().grid(row=1, column=1, padx=10, pady=10)
        
    def start_simulation(self):
        self.running = True
        self.update_simulation()
        
    def pause_simulation(self):
        self.running = False
        
    def reset_simulation(self):
        self.running = False
        self.time_step = 0
        self.organisms = np.array([
            [random.randint(50, 750), random.randint(50, 550), 0, 100, 0] 
            for _ in range(50)
        ] + [
            [random.randint(50, 750), random.randint(50, 550), 1, 100, 0] 
            for _ in range(30)
        ])
        self.history = pd.DataFrame(columns=['time', 'species_0', 'species_1'])
        self.draw_organisms()
        self.update_graph()
        
    def update_simulation(self):
        if not self.running:
            return
            
        # Update organism ages
        self.organisms[:, 4] += 1
        
        # Random movement
        self.organisms[:, 0] += np.random.randint(-5, 6, size=len(self.organisms))
        self.organisms[:, 1] += np.random.randint(-5, 6, size=len(self.organisms))
        
        # Keep in bounds
        self.organisms[:, 0] = np.clip(self.organisms[:, 0], 10, 790)
        self.organisms[:, 1] = np.clip(self.organisms[:, 1], 10, 590)
        
        # Death (simple random chance)
        death_rate = self.death_scale.get()
        survive = np.random.random(len(self.organisms)) > death_rate
        self.organisms = self.organisms[survive]
        
        # Birth (simple random chance)
        birth_rate = self.birth_scale.get()
        new_organisms = []
        for org in self.organisms:
            if np.random.random() < birth_rate:
                # Create offspring near parent
                new_org = org.copy()
                new_org[0] += np.random.randint(-20, 21)
                new_org[1] += np.random.randint(-20, 21)
                new_org[4] = 0  # Reset age
                new_organisms.append(new_org)
        
        if new_organisms:
            self.organisms = np.vstack([self.organisms, new_organisms])
        
        # Update visualization
        self.draw_organisms()
        self.update_graph()
        
        self.time_step += 1
        
        # Continue loop
        self.root.after(50, self.update_simulation)
        
    def draw_organisms(self):
        self.canvas.delete("all")
        
        for org in self.organisms:
            x, y, species_id, energy, age = org
            color = self.species_data.loc[self.species_data['species_id'] == species_id, 'color'].values[0]
            self.canvas.create_oval(x-5, y-5, x+5, y+5, fill=color, outline='')
            
    def update_graph(self):
        # Count populations
        species_counts = {}
        for species_id in [0, 1]:
            count = np.sum(self.organisms[:, 2] == species_id)
            species_counts[f'species_{species_id}'] = count
        
        # Add to history
        new_row = pd.DataFrame([{'time': self.time_step, **species_counts}])
        self.history = pd.concat([self.history, new_row], ignore_index=True)
        
        # Update plot
        self.ax.clear()
        if len(self.history) > 0:
            self.ax.plot(self.history['time'], self.history['species_0'], 'r-', label='Species A')
            self.ax.plot(self.history['time'], self.history['species_1'], 'b-', label='Species B')
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Population')
        self.ax.set_title('Population Over Time')
        self.ax.legend()
        self.graph_canvas.draw()

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = LifeSimulation(root)
    root.mainloop()