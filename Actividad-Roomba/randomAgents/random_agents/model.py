import mesa
from mesa.discrete_space import OrthogonalMooreGrid
from .agent import RandomAgent, ObstacleAgent, FloorAgent, StationAgent


class RandomModel(mesa.Model):
    """
    Roomba cleaning simulation with zones, obstacles, and charging stations.
    Multiple agents: grid divided into vertical zones, each with its own station.
    """

    def __init__(self, num_agents=1, num_obstacles=15, num_dirty_tiles=20,
                 width=28, height=28, seed=42, max_steps=1000):

        super().__init__(seed=seed)

        self.num_agents = num_agents
        self.num_obstacles = num_obstacles
        self.num_dirty_tiles = num_dirty_tiles
        self.width = width
        self.height = height
        self.steps_taken = 0
        self.max_steps = max_steps

        self.grid = OrthogonalMooreGrid([width, height], torus=False)
        self.datacollector = None

        # Create border obstacles
        border = [(x, y)
                  for y in range(height)
                  for x in range(width)
                  if y in [0, height - 1] or x in [0, width - 1]]

        for _, cell in enumerate(self.grid):
            if cell.coordinate in border:
                ObstacleAgent(self, cell)

        # Agent placement logic
        if num_agents == 1:
            charging_station_cell = self.grid[(1, 1)]
            StationAgent(self, charging_station_cell)
            zone = (1, width - 2, 1, height - 2)
            RandomAgent(self, charging_station_cell, home_station_pos=(1, 1), zone=zone)

        else:
            # Divide grid into vertical zones
            usable_width = width - 2
            section_width = usable_width // num_agents

            for i in range(num_agents):
                min_x = 1 + (i * section_width)
                max_x = 1 + ((i + 1) * section_width) - 1 if i < num_agents - 1 else width - 2
                min_y = 1
                max_y = height - 2
                zone = (min_x, max_x, min_y, max_y)

                available_zone_cells = []
                for x in range(min_x, max_x + 1):
                    for y in range(min_y, max_y + 1):
                        cell = self.grid[(x, y)]
                        if not any(isinstance(a, ObstacleAgent) for a in cell.agents):
                            available_zone_cells.append(cell)

                if available_zone_cells:
                    station_cell = self.random.choice(available_zone_cells)
                    station_pos = station_cell.coordinate
                    StationAgent(self, station_cell)
                    RandomAgent(self, station_cell, home_station_pos=station_pos, zone=zone)

        # Dirty tiles
        available_cells = [cell for cell in self.grid.all_cells
                           if not any(isinstance(a, (ObstacleAgent, StationAgent, RandomAgent))
                                      for a in cell.agents)]

        if len(available_cells) >= num_dirty_tiles:
            dirty_cells = self.random.sample(available_cells, num_dirty_tiles)
            for cell in dirty_cells:
                FloorAgent(self, cell, is_clean=False)

        # Additional obstacles
        available_cells = [cell for cell in self.grid.all_cells
                           if not any(isinstance(a, (ObstacleAgent, StationAgent, RandomAgent, FloorAgent))
                                      for a in cell.agents)]

        if len(available_cells) >= num_obstacles:
            obstacle_cells = self.random.sample(available_cells, num_obstacles)
            for cell in obstacle_cells:
                ObstacleAgent(self, cell)

        self.running = True

        # Track up to 10 Roombas
        roombas = [agent for agent in self.agents
                   if isinstance(agent, RandomAgent)]

        self.roomba_ids = {}
        for i, roomba in enumerate(roombas, 1):
            self.roomba_ids[i] = roomba.unique_id

        model_reporters = {
            "Percentage Clean Tiles": lambda m: m.percentage_clean_tiles(),
        }

        for i in range(1, 10 + 1):
            model_reporters[f"Roomba {i}"] = lambda m, idx=i: m.get_roomba_movements_by_index(idx)

        self.datacollector = mesa.DataCollector(model_reporters=model_reporters)

    # --- metrics ---
    def count_active_roombas(self):
        return sum(1 for agent in self.agents
                   if isinstance(agent, RandomAgent) and agent.battery > 0)

    def get_roomba_movements(self, agent_id):
        for agent in self.agents:
            if isinstance(agent, RandomAgent) and agent.unique_id == agent_id:
                return agent.movements
        return 0

    def get_roomba_movements_by_index(self, idx):
        if idx in self.roomba_ids:
            agent_id = self.roomba_ids[idx]
            return self.get_roomba_movements(agent_id)
        return 0

    def count_dirty_tiles(self):
        return sum(1 for agent in self.agents
                   if isinstance(agent, FloorAgent) and not agent.fully_clean)

    def count_clean_tiles(self):
        return sum(1 for agent in self.agents
                   if isinstance(agent, FloorAgent) and agent.fully_clean)

    def percentage_clean_tiles(self):
        return (self.count_clean_tiles() /
                (self.count_dirty_tiles() + self.count_clean_tiles())) * 100

    def step(self):
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)
        self.steps_taken += 1

        if self.count_dirty_tiles() == 0:
            self.running = False

        if self.steps_taken >= self.max_steps:
            self.running = False
