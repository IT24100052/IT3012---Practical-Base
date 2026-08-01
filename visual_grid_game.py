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
        self.facing = "Up"

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


    # ------------------------------------------------------------------
    # Helper: coordinates of the cell directly in front of the agent,
    # based on self.facing. Returns None if that cell is off the grid
    # (treated as blocked, just like a wall).
    # ------------------------------------------------------------------
    def _cell_in_front(self):

        x, y = self.agent_pos

        if self.facing == "Up":
            y += 1
        elif self.facing == "Down":
            y -= 1
        elif self.facing == "Left":
            x -= 1
        elif self.facing == "Right":
            x += 1

        if 0 <= x < self.width and 0 <= y < self.height:
            return (x, y)

        return None


    # Perception subsystem
    def get_percept(self):

        front_cell = self._cell_in_front()
        opponent_cells = [tuple(op) for op in self.opponents]

        return {

            "facing":
                self.facing,

            "wall_ahead":
                front_cell is None or front_cell in self.walls,

            "food_here":
                tuple(self.agent_pos) in self.food_positions,

            "toxin_here":
                tuple(self.agent_pos) in self.toxic_traps,

            "opponent_ahead":
                front_cell is not None and front_cell in opponent_cells,

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

        # Translate the agent's abstract actions into concrete moves.
        if action == "turn_left":

            turn_map = {
                "Up": "Left",
                "Left": "Down",
                "Down": "Right",
                "Right": "Up"
            }
            self.facing = turn_map[self.facing]

            # Turning doesn't move the agent, so we stop here.
            return

        if action == "turn_right":

            turn_map = {
                "Up": "Right",
                "Right": "Down",
                "Down": "Left",
                "Left": "Up"
            }
            self.facing = turn_map[self.facing]

            return

        if action == "move_forward":
            action = self.facing

        if action in ("Up", "Down", "Left", "Right"):
            self.facing = action

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


class SimpleReflexAgent:
    """
    A Simple Reflex Agent: chooses an action using ONLY the current
    percept, via strict IF-THEN condition-action rules. It has no
    memory of past percepts or actions.
    """

    def sense_and_act(self, percept):

        # Rule 1: food under my feet -> eat it by stepping onto it again
        # (in this game, "eating" just means moving onto the food cell,
        # so we treat this the same as moving forward)
        if percept["food_here"]:
            return "move_forward"

        # Rule 2: wall directly ahead -> turn left instead of walking into it
        if percept["wall_ahead"]:
            return "turn_left"

        # Rule 3 (default): nothing blocking me -> just keep moving forward
        return "move_forward"


class ModelBasedAgent:
    """
    A Model-Based Agent: keeps an internal model of the world (its
    believed position and which cells it has already visited) and
    uses that memory, together with the current percept, to decide
    what to do. This lets it recognize when it's repeating itself.
    """

    # Direction you end up facing after a left turn, starting from
    # each possible current facing. (Same rotation as the environment's
    # turn_left logic.)
    LEFT_OF = {
        "Up": "Left",
        "Left": "Down",
        "Down": "Right",
        "Right": "Up"
    }

    def __init__(self):

        # Believed position, starting arbitrarily at (0, 0).
        # This does NOT need to match the agent's real position on
        # the map -- it's a relative internal model built purely by
        # counting the agent's own moves.
        self.believed_pos = (0, 0)

        # Every cell (relative to believed_pos) the agent thinks
        # it has already stood on.
        self.visited_cells = {(0, 0)}

        # What the agent did last turn, and which way it was facing
        # when it did it -- needed to update believed_pos correctly.
        self.last_action = None
        self.last_facing = None

    def _cell_in_direction(self, direction):

        x, y = self.believed_pos

        if direction == "Up":
            y += 1
        elif direction == "Down":
            y -= 1
        elif direction == "Left":
            x -= 1
        elif direction == "Right":
            x += 1

        return (x, y)

    def sense_and_act(self, percept):

        # --- Update internal model based on what happened last turn ---
        if self.last_action == "move_forward":
            self.believed_pos = self._cell_in_direction(self.last_facing)
            self.visited_cells.add(self.believed_pos)

        # --- Decide next action using percept + memory ---
        if percept["food_here"]:
            action = "move_forward"

        elif percept["wall_ahead"]:

            left_direction = self.LEFT_OF[percept["facing"]]
            left_cell = self._cell_in_direction(left_direction)

            if left_cell in self.visited_cells:
                # I've already tried going left from here before --
                # that's the loop. Break it by going right instead.
                action = "turn_right"
            else:
                action = "turn_left"

        else:
            action = "move_forward"

        # --- Remember what we're about to do, for next turn's update ---
        self.last_action = action
        self.last_facing = percept["facing"]

        return action


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

        self.agent = ModelBasedAgent()

        def step():

            if not self.env.is_done():

                percept = self.env.get_percept()
                action = self.agent.sense_and_act(percept)

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
