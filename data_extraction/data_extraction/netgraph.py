from helper import *
class Point:
    def __init__(self, x, y, capacity):
        self.x = x
        self.y = y
        self.c = capacity

class NetGraph:
    def __init__(self):
        self.__graph = {}
        self.__buses = []
        self.__branches = []

    def add_edge(self, u, v):
        if u not in self.__graph:
            self.__graph[u] = []

        if v not in self.__graph:
            self.__graph[v] = []

        if v not in self.__graph[u]:
            self.__graph[u].append(v)
        if u not in self.__graph[v]:
            self.__graph[v].append(u)

    def dfs_recur(self, v, visited, parent_bus):
        visited.add(hash(v))

        if len(self.__graph[v]) > 2 or len(self.__graph[v]) <= 1 and v not in self.__buses:
            self.__buses.append(v)
            if parent_bus is not None:
                self.__branches.append((v, parent_bus))
            parent_bus = v

        if v not in self.__graph:
            return

        for neighbour in self.__graph[v]:
            if hash(neighbour) not in visited:
                self.dfs_recur(neighbour, visited, parent_bus)

    def DFS(self, feeders):
        visited = set()

        for node in feeders:
            if node not in self.__graph:
                print(bcolors.FAIL + 'Feeder node not in netgraph.' + bcolors.ENDC)
                continue
            if hash(node) not in visited and (len(self.__graph[node]) <= 1 or len(self.__graph[node]) > 2):
                self.dfs_recur(node, visited, None)

        return self.__buses, self.__branches, visited

    def check_for_unmapped_buses(self, visited):
        out = []
        for node in self.__graph:
            if hash(node) not in visited and (len(self.__graph[node]) <= 1 or len(self.__graph[node]) > 2):
                out.append(node)
        return out

