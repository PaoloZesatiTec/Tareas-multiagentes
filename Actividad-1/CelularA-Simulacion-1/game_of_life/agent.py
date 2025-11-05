from mesa.discrete_space import FixedAgent

class Cell(FixedAgent):
    """Represents a single ALIVE or DEAD cell in the simulation."""

    DEAD = 0
    ALIVE = 1

    @property
    def x(self):
        return self.cell.coordinate[0]

    @property
    def y(self):
        return self.cell.coordinate[1]

    @property
    def is_alive(self):
        return self.state == self.ALIVE

    def __init__(self, model, cell, init_state=DEAD):
        super().__init__(model)
        self.cell = cell
        self.pos = cell.coordinate
        self.state = init_state
        self._next_state = None

    def determine_state(self):
        """Compute if the cell will be dead or alive at the next tick"""

        if self.y == self.model.height - 1:
            self._next_state = self.state
            return

        top_y = (self.y + 1) % self.model.height
        left_x = (self.x - 1) % self.model.width
        right_x = (self.x + 1) % self.model.width

        top_left_agent   = self.model.grid[left_x, top_y].agents[0]
        top_center_agent = self.model.grid[self.x, top_y].agents[0]
        top_right_agent  = self.model.grid[right_x, top_y].agents[0]

        pattern = (
            ("1" if top_left_agent.is_alive else "0") +
            ("1" if top_center_agent.is_alive else "0") +
            ("1" if top_right_agent.is_alive else "0")
        )

        self._next_state = self.state
        if   pattern == "111": self._next_state = self.DEAD
        elif pattern == "110": self._next_state = self.ALIVE
        elif pattern == "101": self._next_state = self.DEAD
        elif pattern == "100": self._next_state = self.ALIVE
        elif pattern == "011": self._next_state = self.ALIVE
        elif pattern == "010": self._next_state = self.DEAD
        elif pattern == "001": self._next_state = self.ALIVE
        elif pattern == "000": self._next_state = self.DEAD

    def assume_state(self):
        """Set the state to the new computed state."""
        self.state = self._next_state
