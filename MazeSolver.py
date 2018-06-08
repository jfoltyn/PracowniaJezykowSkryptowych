#!/usr/bin/env python

import getopt
import re
import sys
import time


# #########################################################################
class Maze:
    def __init__(self, width, height):
        if width < 1 and height < 1:
            raise ValueError('Invalid size')
        self.width = width
        self.height = height
        self.nodes = [[None] * height for x in range(width)]

    def get_node(self, vector):
        return self.nodes[vector[0]][vector[1]]

    def get_neighbors(self, node):
        neighbours = []
        x_pos = node.position[0]
        y_pos = node.position[1]

        if y_pos - 1 >= 0:
            neighbours.append(self.nodes[x_pos][y_pos - 1])
        if y_pos + 1 < self.height:
            neighbours.append(self.nodes[x_pos][y_pos + 1])
        if x_pos - 1 >= 0:
            neighbours.append(self.nodes[x_pos - 1][y_pos])
        if x_pos + 1 < self.width:
            neighbours.append(self.nodes[x_pos + 1][y_pos])

        return neighbours

    def get_node_with_lowest_total_cost(self):
        flat_nodes = [item for sublist in self.nodes for item in sublist]
        flat_nodes.sort()
        return self.nodes[0]

    def reset_nodes_costs(self):
        for row in self.nodes:
            for node in row:
                node.distance_from_start = 0
                node.heuristic = sys.maxint
                node.parent = None


# #########################################################################
class CharConstants:
    SPACE = ' '
    WALL = '#'
    PATH_START = 'S'
    PATH_TARGET = 'X'
    PATH = 'O'

    ANSI_RESET = '\033[0m'
    ANSI_BOLD = '\033[1m'
    ANSI_RED = '\033[91m'
    ANSI_GREEN = '\033[92m'


def get_bold_string(char):
    return CharConstants.ANSI_BOLD + char + CharConstants.ANSI_RESET


def get_red_string(char):
    return CharConstants.ANSI_RED + char + CharConstants.ANSI_RESET


def get_green_char(char):
    return CharConstants.ANSI_GREEN + char + CharConstants.ANSI_RESET


# #########################################################################
class Node:
    def __init__(self, walkable, vector):
        self.walkable = walkable
        self.position = vector
        self.parent = None

        self.distance_from_start = 0  # usually named g
        self.heuristic = sys.maxint  # usually named h
        self.total_cost = sys.maxint  # usually named f

    def __eq__(self, other):
        return self.position == other.position

    def __cmp__(self, other):
        if self.total_cost < other.total_cost:
            return -1
        if self.total_cost == other.total_cost:
            return 0
        else:
            return 1

    def __hash__(self):
        return hash(self.position)


def is_walkable(character):
    return character == CharConstants.SPACE


def remove_new_line(string):
    return string.split('\n')[0]


# #########################################################################
class MazeLoader:
    def __init__(self, maze_file_name):
        self.mazeData = []
        maze_file = open(maze_file_name, 'r')
        maze_data_raw = maze_file.readlines()
        for row in maze_data_raw:
            self.mazeData.append(remove_new_line(row))
        maze_file.close()

    def generate_maze(self):
        height = len(self.mazeData)
        width = len(self.mazeData[0])

        maze = Maze(width, height)
        for y, row in enumerate(self.mazeData):
            for x, character in enumerate(row):
                maze.nodes[x][y] = Node(is_walkable(character), (x, y))

        return maze


# #########################################################################
def draw(maze):
    output = ''
    for y in range(0, len(maze.nodes[0])):
        row_string = ''
        for x in range(0, len(maze.nodes)):
            if maze.nodes[x][y].walkable:
                row_string += CharConstants.SPACE
            else:
                row_string += CharConstants.WALL

        output += row_string + '\n'

    print output


def draw_with_path(maze, path):
    output = ''
    for y in range(0, len(maze.nodes[0])):
        row_string = ''
        for x in range(0, len(maze.nodes)):
            row_string += get_char_for(x, y, maze, path)

        output += row_string + '\n'

    print output


def get_char_for(x, y, maze, path):
    node_at_current_position = Node(True, (x, y))
    if node_at_current_position in path:
        if path.index(node_at_current_position) == 0:
            return_value = get_red_string(CharConstants.PATH_START)
        elif path.index(node_at_current_position) == len(path) - 1:
            return_value = get_red_string(CharConstants.PATH_TARGET)
        else:
            return_value = get_green_char(CharConstants.PATH)
    else:
        if maze.nodes[x][y].walkable:
            return_value = CharConstants.SPACE
        else:
            return_value = CharConstants.WALL

    return return_value


# #########################################################################
def get_taxi_heuristic(node, target_node):
    return (abs(node.position[0] - target_node.position[0]) +
            abs(node.position[1] - target_node.position[1]))


def retrace_path(start_node, target_node):
    reversed_path = []
    current_node = target_node

    while not current_node == start_node:
        reversed_path.append(current_node)
        current_node = current_node.parent

    reversed_path.append(start_node)
    return list(reversed(reversed_path))


class AStar:
    def __init__(self, maze):
        self.maze = maze

    def find_path(self, start_vector, target_vector):
        start_node = self.maze.get_node(start_vector)
        target_node = self.maze.get_node(target_vector)
        open_set = [start_node]
        closed_set = set()

        while open_set:
            open_set.sort()
            current_node = open_set.pop(0)
            closed_set.add(current_node)

            if current_node == target_node:
                return retrace_path(start_node, target_node)  # success

            neighbours = self.maze.get_neighbors(current_node)
            for neighbour in neighbours:
                if not neighbour.walkable or neighbour in closed_set:
                    continue

                distance_from_start_to_neighbour = neighbour.distance_from_start + 1
                if distance_from_start_to_neighbour < current_node.distance_from_start or neighbour not in open_set:
                    neighbour.distance_from_start = distance_from_start_to_neighbour
                    neighbour.heuristic = get_taxi_heuristic(neighbour, target_node)
                    neighbour.total_cost = neighbour.distance_from_start + neighbour.heuristic
                    neighbour.parent = current_node

                    if neighbour not in open_set:
                        open_set.append(neighbour)

        return


class Dijkstra:
    def __init__(self, maze):
        self.maze = maze

    def find_path(self, start_vector, target_vector):
        start_node = self.maze.get_node(start_vector)
        target_node = self.maze.get_node(target_vector)
        open_set = [start_node]
        closed_set = set()

        while open_set:
            open_set.sort()
            current_node = open_set.pop(0)
            closed_set.add(current_node)

            if current_node == target_node:
                return retrace_path(start_node, target_node)  # success

            neighbours = self.maze.get_neighbors(current_node)
            for neighbour in neighbours:
                if not neighbour.walkable or neighbour in closed_set:
                    continue

                distance_from_start_to_neighbour = neighbour.distance_from_start + 1
                if distance_from_start_to_neighbour < current_node.distance_from_start or neighbour not in open_set:
                    neighbour.distance_from_start = distance_from_start_to_neighbour
                    neighbour.heuristic = get_taxi_heuristic(neighbour, target_node)
                    neighbour.total_cost = neighbour.distance_from_start
                    neighbour.parent = current_node

                    if neighbour not in open_set:
                        open_set.append(neighbour)

        return


# ####################---------MAIN---------##############################
def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def show_help(status = 0):
    print get_bold_string("Description:")
    print "  Script can find path in maze. It is only available to move on straight directions. Diagonals are turned off."
    print "  Tiles are numbered starting with 0. Upper left corner is (0,0). By default script will try to find path"
    print "  between upper left and lower right corners."
    print
    print get_bold_string("Usage:")
    print "  {0} path_to_maze [OPTIONS]".format(sys.argv[0])
    print
    print get_bold_string("Options:")
    print get_bold_string("  -h")
    print "    Showing this message"
    print
    print get_bold_string("  -q")
    print "    Runs in quiet mode. It overrides \033[1m -v \033[0m"
    print
    print get_bold_string("  -v")
    print "    Verbose mode"
    print
    print get_bold_string("  -i iterations")
    print "    Path will be calculated i times and avg time will be calculated."
    print "    Default: 1"
    print
    print get_bold_string("  -s starting_point")
    print "    Starting point in x:y format. Eg. -s 3:1."
    print "    Default: 1:1"
    print
    print get_bold_string("  -t targe_point")
    print "    Target point in x:y format. Eg. -s 3:2."
    print "    Default: size-1:size-1"
    print
    print get_bold_string("  -a algorythm")
    print "    Algorithm to be used. 'astar' or 'dijkstra'"
    print "    Default: 'astar'"
    print

    sys.exit(status)


def show_incorrect_args():
    print get_bold_string(get_red_string('Wrong options'))
    print get_red_string('Showing help:')
    print
    show_help(1)


ALGORITHMS = ['astar', 'dijkstra']
POINT_PATTERN = re.compile('(\d+):(\d+)')

try:
    options, reminder = getopt.gnu_getopt(sys.argv[1:], 'hqvi:s:t:a:')
except getopt.GetoptError:
    show_incorrect_args()

quiet = False
verbose = False

start_x = -1
start_y = -1
target_x = -1
target_y = -1

iterations = 1
algorithm = 'astar'

for opt, arg in options:
    if opt == '-h':
        show_help()
    elif opt == '-q':
        quiet = True
    elif opt == '-v':
        verbose = True
    elif opt == '-i':
        if not arg or not represents_int(arg):
            show_incorrect_args()
        iterations = int(arg)
    elif opt == '-a':
        if not (arg and arg in ALGORITHMS):
            show_incorrect_args()
        algorithm = arg
    elif opt == '-s':
        if not arg or not POINT_PATTERN.match(arg):
            show_incorrect_args()
        start_x = int(POINT_PATTERN.match(arg).groups()[0])
        start_y = int(POINT_PATTERN.match(arg).groups()[1])
    elif opt == '-t':
        if not arg or not POINT_PATTERN.match(arg):
            show_incorrect_args()
        target_x = int(POINT_PATTERN.match(arg).groups()[0])
        target_y = int(POINT_PATTERN.match(arg).groups()[1])

if len(reminder) != 1:
    print get_bold_string(get_red_string('You have not provided path to maze'))
    print get_red_string('Showing help:')
    print
    show_help()

maze_file_path = reminder[0]

maze_loader = MazeLoader(maze_file_path)
maze = maze_loader.generate_maze()

# default start and target positions
if start_x == -1:
    start_x = 1
    start_y = 1
if target_x == -1:
    target_x = maze.width - 2
    target_y = maze.height - 2

# check if points makes sense considering maze size
if start_x < 0 or start_x > maze.width - 1 or start_y < 0 or start_y > maze.height - 1 or target_x < 0 or target_x > maze.width - 1 or target_y < 0 or target_y > maze.height - 1:
    show_incorrect_args()


def fail_output():
    if not quiet:
        print 'It is impossible to solve this maze with this config'

    sys.exit(1)


def success_output():
    if verbose and not quiet:
        draw(maze)
        print
        print
        draw_with_path(maze, path)

        print 'Script needed {0} s to find path {1} times.'.format(total_time, iterations)
        print 'Avg time: {0} s'.format(avg_time)
        print
    elif not quiet:
        print avg_time


total_time = 0
path = []
for i in range(0, iterations):
    maze.reset_nodes_costs()

    if algorithm == 'astar':
        mazeSolver = AStar(maze)
    elif algorithm == 'dijkstra':
        mazeSolver = Dijkstra(maze)

    single_iteration_time = time.clock()
    path = mazeSolver.find_path((start_x, start_y), (target_x, target_y))
    single_iteration_time = time.clock() - single_iteration_time
    total_time += single_iteration_time
    if not path:
        fail_output()


avg_time = (total_time / (1.0 * iterations))
success_output()
