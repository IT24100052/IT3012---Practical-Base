import random
import tkinter as tk


class VisualGridHuntGame:
    """
    Pacman-style grid environment.
    Supports food, walls, toxic traps, and opponents.
    """

    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, custom_walls=None):

        # Environment state (E)
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]

        # Walls
        if custom_walls:
            self.walls = set(custom_walls)
        else:
            self.walls = {
                (2, 2),
                (2, 3),
                (5, 5),
                (6, 5),
                (3, 7)
            }

        # Food generation
        self.food_positions = set()

        while len(self.food_positions) < num_food:

            food = (
                random.randint(0, self.width - 1),
                random.randint(0, self.height - 1)
            )

            if (
                food != (0, 0)
                and food not in self.walls
            ):
                self.food_positions.add(food)


        # Toxic trap generation
        self.toxic_traps = set()

        while len(self.toxic_traps) < 5:

            trap = (
                random.randint(0, self.width - 1),
                random.randint(0, self.height - 1)
            )

            if (
                trap != (0, 0)
                and trap not in self.walls
                and trap not in self.food_positions
            ):
                self.toxic_traps.add(trap)


        # Opponent generation (Multi-Agent)
        self.opponents = []

        while len(self.opponents) < num_opponents:

            opponent = [
                random.randint(0, self.width - 1),
                random.randint(0, self.height - 1)
            ]

            opponent_tuple = tuple(opponent)

            if (
                opponent_tuple != (0, 0)
                and opponent_tuple not in self.walls
                and opponent_tuple not in self.food_positions
                and opponent_tuple not in self.toxic_traps
                and opponent not in self.opponents
            ):
                self.opponents.append(opponent)


        # Performance measure
        self.score = 0
        self.steps = 0
        self.collision = False



    # Perception subsystem
    def get_percept(self):

        return {

            "agent_pos": list(self.agent_pos),

            "opponent_positions":
                [list(op) for op in self.opponents],

            "smells_food":
                tuple(self.agent_pos) in self.food_positions,

            "hit_wall":
                tuple(self.agent_pos) in self.walls,

            "smells_toxin":
                tuple(self.agent_pos) in self.toxic_traps,

            "collision":
                self.collision,

            "score":
                self.score,

            "remaining_food":
                len(self.food_positions)
        }



    # Action execution
    def execute_action(self, action):

        self.steps += 1

        new_pos = list(self.agent_pos)


        if action == "Up":
            new_pos[1] = min(
                self.height - 1,
                new_pos[1] + 1
            )

        elif action == "Down":
            new_pos[1] = max(
                0,
                new_pos[1] - 1
            )

        elif action == "Left":
            new_pos[0] = max(
                0,
                new_pos[0] - 1
            )

        elif action == "Right":
            new_pos[0] = min(
                self.width - 1,
                new_pos[0] + 1
            )


        # Wall collision
        if tuple(new_pos) in self.walls:

            self.score -= 5

        else:

            self.agent_pos = new_pos



        current_position = tuple(self.agent_pos)


        # Food reward
        if current_position in self.food_positions:

            self.food_positions.remove(current_position)
            self.score += 20



        # Toxic trap penalty
        if current_position in self.toxic_traps:

            self.score -= 15



        # Check collision with opponents
        for opponent in self.opponents:

            if opponent == self.agent_pos:

                self.score -= 50
                self.collision = True
                return



        # Move opponents randomly
        for opponent in self.opponents:

            move = random.choice(
                [
                    "Up",
                    "Down",
                    "Left",
                    "Right",
                    "Stay"
                ]
            )


            new_opponent = list(opponent)


            if move == "Up":
                new_opponent[1] = min(
                    self.height - 1,
                    new_opponent[1] + 1
                )

            elif move == "Down":
                new_opponent[1] = max(
                    0,
                    new_opponent[1] - 1
                )

            elif move == "Left":
                new_opponent[0] = max(
                    0,
                    new_opponent[0] - 1
                )

            elif move == "Right":
                new_opponent[0] = min(
                    self.width - 1,
                    new_opponent[0] + 1
                )


            # Opponents cannot pass walls
            if tuple(new_opponent) not in self.walls:

                opponent[0], opponent[1] = new_opponent


            # Collision after movement
            if opponent == self.agent_pos:

                self.score -= 50
                self.collision = True



    def is_done(self):

        return (
            len(self.food_positions) == 0
            or self.steps >= 60
            or self.collision
        )





class GridGameGUI:


    def __init__(
            self,
            root,
            width=12,
            height=12,
            num_food=15,
            num_opponents=2
    ):


        self.root = root

        self.root.title(
            "IT3012 - Multi Agent Grid Hunt"
        )


        self.env = VisualGridHuntGame(
            width,
            height,
            num_food,
            num_opponents
        )


        max_size = 600

        self.cell_size = max(
            20,
            min(
                max_size // width,
                max_size // height
            )
        )


        self.canvas = tk.Canvas(
            root,
            width=width*self.cell_size,
            height=height*self.cell_size,
            bg="white"
        )

        self.canvas.pack()



        self.label = tk.Label(
            root,
            text="Score: 0 | Steps: 0",
            font=("Arial",14)
        )

        self.label.pack()



        self.button = tk.Button(
            root,
            text="Start Simulation",
            command=self.run_loop
        )

        self.button.pack()



        self.draw_grid()




    def draw_grid(self):

        self.canvas.delete("all")


        # Draw grid and walls
        for x in range(self.env.width):

            for y in range(self.env.height):

                x1 = x*self.cell_size
                y1 = (self.env.height-1-y)*self.cell_size

                x2 = x1+self.cell_size
                y2 = y1+self.cell_size


                self.canvas.create_rectangle(
                    x1,y1,x2,y2,
                    fill="gray" if (x,y) in self.env.walls else "white"
                )



        # Food
        for x,y in self.env.food_positions:

            self.canvas.create_oval(
                x*self.cell_size+10,
                (self.env.height-1-y)*self.cell_size+10,
                x*self.cell_size+30,
                (self.env.height-1-y)*self.cell_size+30,
                fill="orange"
            )


        # Traps
        for x,y in self.env.toxic_traps:

            self.canvas.create_oval(
                x*self.cell_size+8,
                (self.env.height-1-y)*self.cell_size+8,
                x*self.cell_size+35,
                (self.env.height-1-y)*self.cell_size+35,
                fill="purple"
            )


        # Opponents
        for x,y in self.env.opponents:

            self.canvas.create_rectangle(
                x*self.cell_size+8,
                (self.env.height-1-y)*self.cell_size+8,
                x*self.cell_size+35,
                (self.env.height-1-y)*self.cell_size+35,
                fill="red"
            )


        # Agent
        x,y = self.env.agent_pos

        self.canvas.create_oval(
            x*self.cell_size+5,
            (self.env.height-1-y)*self.cell_size+5,
            x*self.cell_size+35,
            (self.env.height-1-y)*self.cell_size+35,
            fill="blue"
        )

    def run_loop(self):

        self.button.config(state="disabled")


        def step():

            if not self.env.is_done():

                action=random.choice(
                    [
                        "Up",
                        "Down",
                        "Left",
                        "Right"
                    ]
                )


                self.env.execute_action(action)


                self.draw_grid()


                self.label.config(
                    text=f"Score: {self.env.score} | Steps: {self.env.steps}"
                )


                self.root.after(
                    300,
                    step
                )


            else:

                self.label.config(
                    text=f"Game Over! Final Score: {self.env.score}"
                )


        step()





if __name__ == "__main__":

    root=tk.Tk()

    app=GridGameGUI(
        root,
        width=12,
        height=12,
        num_food=15,
        num_opponents=2
    )

    root.mainloop()