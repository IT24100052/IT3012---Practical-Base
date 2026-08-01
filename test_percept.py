from visual_grid_game import VisualGridHuntGame

env = VisualGridHuntGame(width=6, height=6, num_food=3, num_opponents=1)

print("Facing:", env.facing)
print("What I sense:", env.get_percept())

env.execute_action("Right")

print("Facing after moving Right:", env.facing)
print("What I sense now:", env.get_percept())