import pygame
import math
from queue import PriorityQueue

WIDTH = 600
WIN = pygame.display.set_mode((WIDTH,WIDTH))
pygame.display.set_caption("A* Pathfinding Algorithm")

RED = (225,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
WHITE = (255,255,255)
BLACK = (0,0,0)
PURPLE = (128,0,128)
ORANGE = (255,165,0)
GREY = (128,128,128)
TURQOISE = (64,224,208)

#Elements in the grid
class Spot:
    def __init__(self,row,col,width,total_rows):
        #width is thewide of the spot
        self.row = row
        self.col = col
        self.x = row*width
        self.y = col*width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col
    
    #states of the spot
    def is_closed(self):
        return self.color == RED
    
    def is_open(self):
        return self.color == GREEN
    
    def is_barrier(self):
        return self.color == BLACK
    
    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQOISE
    
    def reset(self):
        self.color = WHITE
    
    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self,win):
        pygame.draw.rect(win,self.color,(self.x,self.y,self.width,self.width))

    def update_neighbors(self, grid):
        #Check around the node if they are not barriers and them to the list
        self.neighbors = []

        #check the availability of moving DOWN
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row+1][self.col])
        #**********************
        # Ensure that the spot is not on the bottom row.
        #Verify that the spot below is not a barrier.
        #**********************

        if self.row and self.col < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row+1][self.col])

        if self.row and self.col > 0 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row+1][self.col])

        #check the availability of moving UP
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row-1][self.col])

        #check the availability of moving RIGHT
        if self.col < self.total_rows - 1 and not grid[self.row][self.col +1].is_barrier():
            self.neighbors.append(grid[self.row][self.col +1])

        #check the availability of moving LEFT
        if self.col > 0 and not grid[self.row][self.col -1].is_barrier():
            self.neighbors.append(grid[self.row][self.col -1])    

    #Less than function(comparing 2 spots)
    #spots are not ordered or comparable based on this criteria.
    def __lt__(self,other):
        return False
        
#heristic function: define the distance between p1 & p2 (manhatten distance)  
def h(p1,p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

def algorithm(draw,grid,start,end):
    count = 0 #used for tie-breaking in the priority queue
    open_set = PriorityQueue() #a priority queue to store nodes to be explored
    open_set.put((0,count,start))
    came_from = {} #a dictionary to keep track of the path
    #the cost from the start node to each node
    g_score = {spot: float("inf") for row in grid for spot in row }
    g_score[start] = 0
    #the estimated total cost from the start to the end node
    f_score = {spot: float("inf") for row in grid for spot in row }
    #it is a heuristic beacause we want to estimate how far is the end node from the start one
    f_score[start] = h(start.get_pos(),end.get_pos())

    #check if something in the PQ (keep tracks all items in the PQ) WE CAN REMOVE ITEMS BUT NOT CHECK
    open_Set_hash = {start}
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  
                pygame.quit()
        #START AT THE START NODE
        current = open_set.get()[2]
        open_Set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True
        
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1 

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_Set_hash:
                    count +1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_Set_hash.add(neighbor)
                    neighbor.make_open()

        draw() #used to visualize the progress
        if current != start:
            current.make_closed()

    #if not finding the path
    return False

#create a two-dimensional grid
def make_grid(rows, width):
    grid = [] #empty list to store the rows of the grid
    gap = width // rows #width of each spot in the grid
    for i in range(rows): #create each row in the grid.
        grid.append([]) # appends an empty list to grid, representing a new row in the grid.
        for j in range(rows): #create each spot within the current row.
            spot = Spot(i, j, gap, rows) #creates a new Spot object with the given parameters 
            grid[i].append(spot) #appends the newly created spot to the current row in the grid.
    return grid

def draw_grid(win,rows,width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win,GREY,(0,i * gap),(width,i * gap))
        for j in range(rows):
            pygame.draw.line(win,GREY,(j * gap, 0),(j * gap, width))

def draw(win,grid,rows,width):
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win) #draw a spot on the window
    
    draw_grid(win,rows,width) # draw the grid lines on the window
    pygame.display.update()

def get_clicked_pos(pos,rows,width):
    gap = width // rows
    y , x = pos
    row = y // gap
    col = x // gap
    return row, col

def main(win,width):
    ROWS = 40
    grid = make_grid(ROWS,width) #generate the grid

    start = None
    end = None
    run = True
    started = False

    #main loop (Display the screen)
    while run:
        draw(win,grid,ROWS,width)
        #looping through pygame module events
        for event in pygame.event.get():

            if event.type == pygame.QUIT:  
                run = False  # Set run to False when the window is closed
                 
            #once algorithm started user can not be able to click anything except exit button
            if started:
                continue
            
            #if mouse pressed using left mouse button
            if pygame.mouse.get_pressed()[0]: #left
                pos = pygame.mouse.get_pos()
                row,col = get_clicked_pos(pos,ROWS,width) #return row and col we clicked on
                spot = grid[row][col]

                #before we sign a start make sure that spot!=end
                #if we have not placed the start position
                if not start and spot != end:
                    start = spot
                    start.make_start()

                #before we sign a start make sure that spot!=end
                #so that they can not overwrite each other
                elif not end and spot != start:
                    end = spot
                    end.make_end() 

                elif spot != end and spot != start:
                    spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]: #right
                pos = pygame.mouse.get_pos()
                row,col = get_clicked_pos(pos,ROWS,width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    #RUN THE A* ALGORITHM
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid) #updates the neighbors for each spot

                    #call the A* algorithm
                    algorithm(lambda: draw(win,grid,ROWS,width),grid,start,end)
    # Quit Pygame when the game loop exits
    pygame.quit()


main(WIN,WIDTH)