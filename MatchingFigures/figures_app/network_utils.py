# create a new network of n people

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import datetime
import random
random.seed(4242)

'''
Contains functions for creating networks and (potentially) matchmaking algorithms. 
'''

# RANDOM NETWORK
N_NEIGHBORS = 4
N_NODES = 6

# PLANTED PARTITION NETWORK (remove)
N_NODES_PER_COMMUNITY = 4
N_COMMUNITY = int(N_NODES/N_NODES_PER_COMMUNITY)

# WATTS-STROGATZ NETWORK
P_REWIRE = 0.2

# GAME
MAX_ROUNDS = 20

def to_ring(n):

    # Calculate polar coordinates for nodes for a ring layout
    theta = np.linspace(0, 2*np.pi, n, endpoint=False)
    pos = {i: (np.cos(theta[i]), np.sin(theta[i])) for i in range(n)}

    return pos


# graphs


# Draw the graph
def draw(G, pos=None, with_labels=True, node_color='skyblue'):
    if pos:
        nx.draw(G, pos, with_labels=with_labels, node_size=100, node_color=node_color)
    else:
        nx.draw(G, with_labels=with_labels, node_size=20, node_shape='8')

    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

def pairs_this_round(am, active_nodes, executed_pairs):

    '''
    Picks out all possible pairs if at least one of the nodes are active.
    
    Inputs:
        am: 2d-ndarray, 
            the adjacency matrix of the graph in np.array format, must be squared;
        active_nodes: 1D ndarray, 
            the array of of if the active nodes, 
        '''

    
    pairs = []
    participants = set() # is already paired up this round
    
    for r in range(len(am)):
        for c in range(len(am[0])):
            if (r,c) not in executed_pairs and (c,r) not in executed_pairs:
                if am[r][c] and (active_nodes[r] or active_nodes[c]):
                    if r not in participants and c not in participants:
                        pairs.append((r, c))
                        participants.add(r)
                        participants.add(c)
                        executed_pairs.append((r, c))
                

    return pairs, participants


def activate(active_nodes, participants):

    '''
    Updates the nodes activation array INPLACE which takes boolean values depending on 
    if the diffusion process has reached the given node.
    
    inputs:
        active_nodes: ndarray, the nodes activation array,
        participants: set, the set of participants which were active this round
    '''
    new_active_nodes = active_nodes
    for part in participants:
        new_active_nodes[part] = 1
    
    # print(new_active_nodes)
    return new_active_nodes



def watts_strogatz(N=12,k=4,p=0.4):

    # Generate the graph
    G = nx.watts_strogatz_graph(N, k, p)

    pos = to_ring(N)

    # Draw the graph using the polar coordinates
    draw(G, pos)

def fill_blanks(participants):

    all_set = set(np.arange(N_NODES))

    non_participants = list(all_set - participants)
    non_pairs = [(non_participants[i], non_participants[i+1]) for i in range(0, len(non_participants)-1, 2)]
    
    return non_pairs

def schedule_network(G, starting_time=8, tpg=5, seeds=[0], path = 'MatchingFigures/figures_app/', filename ='Network-schedule.csv'):

    executed_pairs = []
    filename = path + filename
    am = nx.adjacency_matrix(G).toarray()
    active_nodes = np.zeros(N_NODES)

    for seed in seeds:
        active_nodes[seed] = 1

    time = datetime.timedelta(hours=starting_time)

    file = open(filename, 'w')

    round_count = 1
    max_game_per_round = 0
    for _ in range(MAX_ROUNDS):
        node_colors = ['red' if active_nodes[node-1] else 'skyblue' for node in G.nodes()]
        # draw(G, pos, node_color=node_colors)

        pairs, participants = pairs_this_round(am, active_nodes, executed_pairs)
        print(f'num of games this round: {len(pairs)}')
        active_nodes = activate(active_nodes, participants)
        print(active_nodes)
        if pairs:
            # for human readable output
            file.write(f'Round {round_count} starts at {str(time)} \n' )
            file.write(f'Participant IDs: {participants} \n')
            # file.write(str(pairs))

            # for machine readable
            # file.write(f'{str(participants)[1:-1]};')
            for pair in pairs:
                file.write(f'{pair[0],pair[1]}')
            # # file.write(';')
            non_pairs = fill_blanks(participants)
            for pair in non_pairs:
                file.write(f'{pair[0],pair[1]}')
            file.write('\n\n')


            time += datetime.timedelta(minutes=tpg)
            round_count += 1
    
    file.close()
    
    return round_count


def process_txt(file_name):
    all_participants = []
    all_pairs = []

    with open(file_name, 'r') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("Round"):
            # Skip the time info
            i += 1
            # print(line)
            continue

        # print('here', line[18:-1].split(", "))
        participants = set(map(int, (line[18:-1].split(", "))))
        # print('here', participants)
        all_participants.append(participants)

        i += 1

        pairs_line = lines[i].strip()
        # print('aa,',pairs_line)
        pairs = []
        for j in range(1, len(pairs_line), 6):
            # print(pairs_line[j])
            pairs.append((int(pairs_line[j]), int(pairs_line[j+3])))
        all_pairs.append(pairs)

        i += 2

    return all_participants, all_pairs


if __name__ == '__main__':

    random_G = nx.random_regular_graph(N_NEIGHBORS, N_NODES)
    ws_G = nx.watts_strogatz_graph(N_NODES,N_NEIGHBORS,P_REWIRE)
    pos = to_ring(N_NODES)
    
    # draw(random_G, pos)
    # draw(ws_G, pos)

    # watts_strogatz(N_NODES, N_NEIGHBORS, P_REWIRE)


    round_count = schedule_network(random_G, filename='random4242.txt')
    round_count = schedule_network(ws_G, filename='ws4242.txt')
    print(round_count)

    # # Use the function
    # all_participants, all_pairs = process_txt('MatchingFigures/figures_app/random4242.txt')
    # print(all_participants)
    # print(all_pairs)

    # part, pairs, nonp = schedule_otree()
    # print(part[0])
    