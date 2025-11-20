from mesa.discrete_space import CellAgent, FixedAgent

class RandomAgent(CellAgent):
    """
    Roomba agent that cleans floor tiles using a snake pattern.
    Battery management: 1% per action, recharges 5% per step at station.
    Returns to home station when battery < 30%.
    Discovers environment boundaries through exploration.
    """
    def __init__(self, model, cell, battery=100, home_station_pos=None):
        super().__init__(model)
        self.cell = cell
        self.battery = battery
        self.movements = 0
        self.home_station_pos = home_station_pos
        self.going_up = True  # For snake pattern movement
        self.visit_count = {}
        if cell:
            self.visit_count[cell.coordinate] = 1
        
    def is_on_charging_station(self):
        return any(isinstance(agent, StationAgent) for agent in self.cell.agents)
    
    def is_on_dirty_floor(self):
        for agent in self.cell.agents:
            if isinstance(agent, FloorAgent) and not agent.fully_clean:
                return True
        return False
    
    def get_floor_agent(self):
        for agent in self.cell.agents:
            if isinstance(agent, FloorAgent):
                return agent
        return None

    def clean_current_cell(self):
        if self.battery <= 0:
            return False
            
        floor_agent = self.get_floor_agent()
        if floor_agent and not floor_agent.fully_clean:
            floor_agent.fully_clean = True
            self.battery -= 1  
            return True
        return False

    def charge_battery(self):
        if self.is_on_charging_station():
            self.battery = min(100, self.battery + 5)
            return True
        return False

    def can_move_to(self, x, y):
        """Check if position exists, is unvisited, and has no obstacles."""
        try:
            target_cell = self.model.grid[(x, y)]
            has_obstacle = any(isinstance(a, ObstacleAgent) for a in target_cell.agents)
            return not has_obstacle and self.visit_count.get((x, y), 0) == 0
        except:
            return False
    
    def get_visit_count(self, pos):
        return self.visit_count.get(pos, 0)
    
    def visit_cell(self, pos):
        self.visit_count[pos] = self.visit_count.get(pos, 0) + 1
    
    def move_snake_pattern(self):
        """Lawnmower pattern: go up/down columns, switch direction at boundaries, avoid obstacles."""
        if self.battery <= 0:
            return False
        
        if self.move_to_dirty_neighbor():
            return True
        
        current_x, current_y = self.cell.coordinate
        
        if self.going_up:
            if self.can_move_to(current_x, current_y + 1):
                new_pos = (current_x, current_y + 1)
                self.cell = self.model.grid[new_pos]
                self.visit_cell(new_pos)
                self.battery -= 1
                self.movements += 1
                return True
            
            # Try to go around obstacles
            if self.can_move_to(current_x - 1, current_y):
                new_pos = (current_x - 1, current_y)
                self.cell = self.model.grid[new_pos]
                self.visit_cell(new_pos)
                self.battery -= 1
                self.movements += 1
                return True
            
            if self.can_move_to(current_x + 1, current_y):
                new_pos = (current_x + 1, current_y)
                self.cell = self.model.grid[new_pos]
                self.visit_cell(new_pos)
                self.battery -= 1
                self.movements += 1
                return True
            
            # Reached top or blocked, switch direction and move right
            self.going_up = False
            if self.can_move_to(current_x + 1, current_y):
                new_pos = (current_x + 1, current_y)
                self.cell = self.model.grid[new_pos]
                self.visit_cell(new_pos)
                self.battery -= 1
                self.movements += 1
                return True
            
        else:
            if self.can_move_to(current_x, current_y - 1):
                new_pos = (current_x, current_y - 1)
                self.cell = self.model.grid[new_pos]
                self.visit_cell(new_pos)
                self.battery -= 1
                self.movements += 1
                return True
            
            if self.can_move_to(current_x - 1, current_y):
                new_pos = (current_x - 1, current_y)
                self.cell = self.model.grid[new_pos]
                self.visit_cell(new_pos)
                self.battery -= 1
                self.movements += 1
                return True
            
            if self.can_move_to(current_x + 1, current_y):
                new_pos = (current_x + 1, current_y)
                self.cell = self.model.grid[new_pos]
                self.visit_cell(new_pos)
                self.battery -= 1
                self.movements += 1
                return True
            
            # Reached bottom or blocked, switch direction and move right
            self.going_up = True
            if self.can_move_to(current_x + 1, current_y):
                new_pos = (current_x + 1, current_y)
                self.cell = self.model.grid[new_pos]
                self.visit_cell(new_pos)
                self.battery -= 1
                self.movements += 1
                return True
        
        # If no dirty neighbor, move to unvisited neighbor
        return self.move_to_unvisited_neighbor()
    
    def has_dirty_floor(self, cell):
        for agent in cell.agents:
            if isinstance(agent, FloorAgent) and not agent.fully_clean:
                return True
        return False
    
    def move_to_dirty_neighbor(self):
        """Prioritize moving to dirty neighboring cells, preferring less-visited ones."""
        if self.battery <= 0:
            return False
        
        dirty_neighbors = []
        for neighbor_cell in self.cell.neighborhood:
            has_obstacle = any(isinstance(agent, ObstacleAgent) for agent in neighbor_cell.agents)
            if not has_obstacle and self.has_dirty_floor(neighbor_cell):
                visit_count = self.get_visit_count(neighbor_cell.coordinate)
                dirty_neighbors.append((neighbor_cell, visit_count))
        
        if dirty_neighbors:
            dirty_neighbors.sort(key=lambda x: x[1])
            best_dirty = dirty_neighbors[0][0]
            
            self.cell = best_dirty
            self.visit_cell(best_dirty.coordinate)
            self.battery -= 1
            self.movements += 1
            return True
        
        return False
    
    def move_to_unvisited_neighbor(self):
        """Move to least-visited neighbor, randomly choosing among ties."""
        if self.battery <= 0:
            return False
        
        available_neighbors = []
        
        for neighbor_cell in self.cell.neighborhood:
            neighbor_pos = neighbor_cell.coordinate
            has_obstacle = any(isinstance(agent, ObstacleAgent) for agent in neighbor_cell.agents)
            if not has_obstacle:
                visit_count = self.get_visit_count(neighbor_pos)
                available_neighbors.append((neighbor_cell, visit_count))
        
        if not available_neighbors:
            return False
        
        available_neighbors.sort(key=lambda x: x[1])
        min_visits = available_neighbors[0][1]
        best_neighbors = [cell for cell, count in available_neighbors if count == min_visits]
        
        next_cell = self.random.choice(best_neighbors)
        self.cell = next_cell
        self.visit_cell(next_cell.coordinate)
        self.battery -= 1
        self.movements += 1
        return True
    
    def move_to_random_neighbor(self):
        """Move to any valid neighbor, used when leaving charging station."""
        if self.battery <= 0:
            return False
            
        valid_neighbors = []
        
        for neighbor_cell in self.cell.neighborhood:
            has_obstacle = any(isinstance(agent, ObstacleAgent) for agent in neighbor_cell.agents)
            if not has_obstacle:
                valid_neighbors.append(neighbor_cell)
        
        if valid_neighbors:
            next_cell = self.random.choice(valid_neighbors)
            self.cell = next_cell
            self.visit_cell(next_cell.coordinate)
            self.battery -= 1
            self.movements += 1
            return True
        return False
    
    def needs_charging(self):
        return self.battery < 30
    
    def get_direction_to_home_station(self):
        if not self.home_station_pos:
            return None
        
        current_x, current_y = self.cell.coordinate
        target_x, target_y = self.home_station_pos
        dx = target_x - current_x
        dy = target_y - current_y
        
        return (dx, dy)
    
    def move_towards_home_station(self):
        """Navigate to home station using Manhattan distance, allows revisiting cells."""
        if self.battery <= 0:
            return False
        
        direction = self.get_direction_to_home_station()
        if not direction:
            return self.move_to_unvisited_neighbor()
        
        dx, dy = direction
        current_x, current_y = self.cell.coordinate
        
        valid_neighbors = []
        for neighbor_cell in self.cell.neighborhood:
            has_obstacle = any(isinstance(agent, ObstacleAgent) for agent in neighbor_cell.agents)
            if not has_obstacle:
                valid_neighbors.append(neighbor_cell)
        
        if not valid_neighbors:
            return False
        
        best_neighbor = None
        best_distance = float('inf')
        
        for neighbor in valid_neighbors:
            nx, ny = neighbor.coordinate
            distance = abs(self.home_station_pos[0] - nx) + abs(self.home_station_pos[1] - ny)
            if distance < best_distance:
                best_distance = distance
                best_neighbor = neighbor
        
        if best_neighbor:
            self.cell = best_neighbor
            self.visit_cell(best_neighbor.coordinate)
            self.battery -= 1
            self.movements += 1
            return True
        
        return False

    def step(self):
        """Behavior priority: charge if low battery → clean if dirty → explore via snake pattern."""
        if self.battery <= 0:
            return
        
        if self.is_on_charging_station():
            if self.battery < 100:
                self.charge_battery()
            elif self.is_on_dirty_floor():
                self.clean_current_cell()
            elif not self.move_to_dirty_neighbor():
                self.move_to_random_neighbor()
        
        elif self.needs_charging():
            self.move_towards_home_station()
        
        elif self.is_on_dirty_floor():
            self.clean_current_cell()
        
        else:
            self.move_snake_pattern()


class ObstacleAgent(FixedAgent):
    """Static obstacle that blocks movement."""
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell

    def step(self):
        pass

class StationAgent(FixedAgent):
    """Charging station for Roomba agents."""
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell

    def step(self):
        pass


class FloorAgent(FixedAgent):
    """Floor tile that can be dirty or clean."""

    @property
    def fully_clean(self):
        return self._fully_clean

    @fully_clean.setter
    def fully_clean(self, value: bool) -> None:
        self._fully_clean = value

    def __init__(self, model, cell, is_clean=False):
        super().__init__(model)
        self.cell = cell
        self._fully_clean = is_clean

    def step(self):
        pass