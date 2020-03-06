import networkx as nx
import math
import csv
import numpy as np
import argparse
import os.path
BIG_NUM = 10 ** 9
DELAY = 4.83
R = 6373.0

class Node():
    def __init__(self, id_=None, label=None, latitude=None, longitude=None):
        self.id = int(id_) if (id_ is not None) else None
        self.label = label
        self.latitude = float(latitude) if (latitude is not None) else None
        self.longitude = float(longitude) if (longitude is not None) else None
    def __str__(self):
        return f'{self.id} {self.label} : ({self.longitude}, {self.latitude})'
    def __hash__(self):
        return hash(self.id)
    def __eq__(self, node):
        return (node == self.id)
    def dist(self, other):
        lat1 = math.radians(self.latitude)
        lon1 = math.radians(self.longitude)
        
        lat2 = math.radians(other.latitude)
        lon2 = math.radians(other.longitude)
        a = math.sin((lat2 - lat1) / 2) ** 2 \
            + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return (R * c)
    def __cmp__(self, node):
        return cmp(self.id, node)
    def getId(self):
        return int(self.id)
    def setId(self, id_):
        self.id = int(id_)
    def setLabel(self, label):
        self.label = label
    def setLatitude(self, latitude):
        self.latitude = float(latitude)
    def setLongitude(self, longitude):
        self.longitude = float(longitude)

        
class Path():
    def __init__(self, filename, create_reserved_paths=True, start_poit=None, dist_point=None):
        self.nodes = {}
        self.graph = {}
        self.directed = False
        self.parse(filename, lib=False)
        if start_poit and self.nodes.get(start_poit) is None:
            raise Exception('No such starting point :(')
        if dist_point and self.nodes.get(dist_point) is None:
            raise Exception('No such destination point :(')
        self.create_CSV1(filename.split('.')[0] + '_topo.csv')
        self.Floyd(create_reserved_paths=create_reserved_paths, start_poit=start_poit, dist_point=dist_point)
        self.create_CSV2(filename.split('.')[0] + '_routes.csv')
    
    def parse(self, filename, lib=True):
        if filename[-4:] != '.gml':
            raise Exception('Needed *.gml')
        if not os.path.isfile(filename):
            raise Exception('No file')
        if lib:
            graph = nx.read_gml(filename, label='id')
            for node in graph.node:
                new_vertex = Node(
                                    node, 
                                    graph.node[node]['label'], 
                                    graph.node[node]['Latitude'], 
                                    graph.node[node]['Longitude']
                                )
                self.nodes[node] = new_vertex
            for edge in graph.edges:
                if self.graph.get(self.nodes[edge[0]]) == None:
                    self.graph[self.nodes[edge[0]]] = []
                self.graph[self.nodes[edge[0]]].append(self.nodes[edge[1]])
        else:
            def parseNode(st):
                new_node = Node()
                for line in st.split('\n'):
                    line = line.strip()
                    sp = line.find(" ")
                    if line[:sp] == 'id':
                        new_node.setId(int(line[sp + 1:]))
                    elif line[:sp] == 'label':
                        new_node.setLabel(line[sp + 1:].replace("\"", ""))
                    elif line[:sp] == 'Longitude':
                        new_node.setLongitude(line[sp + 1:])
                    elif line[:sp] == 'Latitude':
                        new_node.setLatitude(line[sp + 1:])
                return new_node
            def parseEdge(st):
                edge = {}
                for line in st.split('\n'):
                    line = line.strip()
                    sp = line.find(" ")
                    if line[:sp] == 'source':
                        edge['source'] = int(line[sp + 1:])
                    elif line[:sp] == 'target':
                        edge['target'] = int(line[sp + 1:])
                return (edge['source'], edge['target'])
            with open(filename, 'r') as inputfile:
                for line in inputfile:
                    concat = ""
                    if line.lower().find("directed 1") != -1:
                        self.directed = True
                    if line.find("node [") != -1:
                        s = inputfile.readline()
                        while s.find(']') == -1:
                            concat += s
                            s = inputfile.readline()
                        new_vertex = parseNode(concat)
                        self.nodes[new_vertex.getId()] = new_vertex
                    if line.find("edge [") != -1:
                        s = inputfile.readline()
                        while s.find(']') == -1:
                            concat += s
                            s = inputfile.readline()
                        edge = parseEdge(concat)
                        if self.graph.get(self.nodes[edge[0]]) == None:
                            self.graph[self.nodes[edge[0]]] = []
                        self.graph[self.nodes[edge[0]]].append(self.nodes[edge[1]])
                        if not self.directed:
                            if self.graph.get(self.nodes[edge[1]]) == None:
                                self.graph[self.nodes[edge[1]]] = []
                            self.graph[self.nodes[edge[1]]].append(self.nodes[edge[0]])
    
    def create_CSV1(self, filename, newline='', delimiter='\t'):
        with open(filename, 'w', newline=newline) as csvfile:
            writer = csv.DictWriter(csvfile, delimiter=delimiter, fieldnames=\
                         ['Node 1 (id)', 'Node 1 (label)', 'Node 1 (longitude)', 'Node 1 (latitude)', 
                          'Node 2 (id)', 'Node 2 (label)', 'Node 2 (longitude)', 'Node 2 (latitude)',
                          'Distance (km)', 'Delay (mks)'])
            writer.writeheader()
            for node in sorted(self.graph.keys(), key = lambda x: int(x.getId())):
                self.graph[node].sort(key = lambda x: int(x.getId()))
                for edge in self.graph[node]:
                    writer.writerow({
                        'Node 1 (id)': node.id, 'Node 1 (label)': node.label,
                        'Node 1 (longitude)' : node.longitude, 'Node 1 (latitude)' : node.latitude,
                        'Node 2 (id)' : edge.id, 'Node 2 (label)' : edge.label, 
                        'Node 2 (longitude)': edge.longitude, 'Node 2 (latitude)' : edge.latitude,
                        'Distance (km)' : node.dist(edge) , 'Delay (mks)' : node.dist(edge) * DELAY })
    
    def create_CSV2(self, filename, newline='', delimiter='\t'):
        with open(filename, 'w', newline=newline) as csvfile:
            writer = csv.DictWriter(csvfile, delimiter=delimiter, fieldnames=\
                         ['Node 1 (id)', 'Node 2 (id)', 'Path type', 'Path', 'Delay (mks)'])
            writer.writeheader()
            
            for path in self.paths:
                writer.writerow({
                        'Node 1 (id)': path['Node 1'], 'Node 2 (id)' : path['Node 2'],
                        'Path type' : path['Path type'], 'Path' : path['Path'],
                        'Delay (mks)' : path['Delay'],
                        })
    def Floyd(self, create_reserved_paths, start_poit, dist_point):
        '''for k = 1 to n
              for i = 1 to n
                for j = 1 to n
                  W[i][j] = min(W[i][j], W[i][k] + W[k][j])
        '''

        n = len(self.nodes)
        #id in graph -> id in file
        self.ids = dict(enumerate(sorted([self.nodes[x].getId() for x in self.nodes])))
        #id in file -> id in graph
        self.ids_reversed = dict(zip(self.ids.values(), self.ids.keys()))
        def get_orig(x):
            return self.ids[x]
        W = np.zeros((n, n)) + np.inf
        paths = []
        for i in range(n):
            paths.append([])
            for j in range(n):
                paths[i].append([i])
        
        for node in self.graph:
            for edge in self.graph[node]:
                W[self.ids_reversed[node.id]][self.ids_reversed[edge.id]] = node.dist(edge) * DELAY
                paths[self.ids_reversed[node.id]][self.ids_reversed[edge.id]] = [self.ids_reversed[node.id], self.ids_reversed[edge.id]]
#                 print(node, edge)
        
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if W[i][j] > W[i][k] + W[k][j]:
                        W[i][j] = W[i][k] + W[k][j]
                        paths[i][j] = paths[i][k][:-1] + paths[k][j]
        self.paths = []
        
        for i in range(n):
            for j in range(n):
                if W[i][j] < np.inf:
                    self.paths.append({})
                    self.paths[-1]['Node 1'] = self.ids[i]
                    self.paths[-1]['Node 2'] = self.ids[j]
                    self.paths[-1]['Path type'] = 'main'
                    self.paths[-1]['Path'] = str(list(map(get_orig, paths[i][j])))
                    self.paths[-1]['Delay'] = W[i][j]
                    if start_poit is not None and dist_point is not None and start_poit == self.ids[i] and dist_point == self.ids[j]:
                        print(self.paths[-1]['Path'])
                    if create_reserved_paths:
                        self.paths.append({})
                        self.paths[-1]['Node 1'] = self.ids[i]
                        self.paths[-1]['Node 2'] = self.ids[j]
                        self.paths[-1]['Path type'] = 'reserve'
                        res_paths = []
                        for i1 in range(n):
                            res_paths.append([])
                            for j1 in range(n):
                                res_paths[i1].append([i1])
                        W_res = np.zeros((n, n)) + np.inf
                        for node in self.graph:
                            for edge in self.graph[node]:
                                W_res[self.ids_reversed[node.id]][self.ids_reversed[edge.id]] = node.dist(edge) * DELAY
                                res_paths[self.ids_reversed[node.id]][self.ids_reversed[edge.id]] = [self.ids_reversed[node.id], self.ids_reversed[edge.id]]
                        for k in range(len(paths[i][j])):
                            v = paths[i][j][k]
                            if v != i and v != j:
                                W_res[v, :] += BIG_NUM
                                W_res[:, v] += BIG_NUM
                            if v != j:
                                W_res[v, paths[i][j][k + 1]] = np.inf

                        for k in range(n):
                            for i1 in range(n):
                                for j1 in range(n):
                                    if W_res[i1][j1] > W_res[i1][k] + W_res[k][j1]:
                                        W_res[i1][j1] = W_res[i1][k] + W_res[k][j1]
                                        res_paths[i1][j1] = res_paths[i1][k][:-1] + res_paths[k][j1]

                        if W_res[i][j] < BIG_NUM * 3:
#                             print(i, j, W_res[i][j], paths[i][j], res_paths[i][j])
                            self.paths[-1]['Path'] = str(list(map(get_orig, res_paths[i][j])))
                            self.paths[-1]['Delay'] = W_res[i][j] % BIG_NUM                            
                        else:
                            self.paths[-1]['Path'] = 'no'
                            self.paths[-1]['Delay'] = ""
                        if start_poit is not None and dist_point is not None and start_poit == self.ids[i] and dist_point == self.ids[j] :
                            print(self.paths[-1]['Path'])
                elif start_poit is not None and dist_point is not None and start_poit == self.ids[i] and dist_point == self.ids[j]:
                        print("no")        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--top_file", help="network file", type=str, required=True)
    parser.add_argument("-r", "--reserve", help="Reserve", action='store_true', default=False)
    parser.add_argument("-s", "--start", help="STart point", default=None, type=int)
    parser.add_argument("-d", "--destination", help="Destination point", default=None, type=int)
    args = parser.parse_args()
    Path(args.top_file, create_reserved_paths=args.reserve, start_poit=args.start, dist_point=args.destination)