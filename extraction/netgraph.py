class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class NetGraph:
    def __init__(self):
        self.__graph = {}
        self.__buses = []

    def add_edge(self, u, v):
        if u not in self.__graph:
            self.__graph[u] = []

        if v not in self.__graph:
            self.__graph[v] = []

        self.__graph[u].append(v)
        self.__graph[v].append(u)

    def dfs_util(self, v, visited):
        visited.add(hash(v))

        if len(self.__graph[v]) > 2 or len(self.__graph[v]) <= 1:
            self.__buses.append(v)

        if v not in self.__graph:
            return

        for neighbour in self.__graph[v]:
            if hash(neighbour) not in visited:
                self.dfs_util(neighbour, visited)

    def DFS(self):
        visited = set()

        for node in self.__graph:
            if hash(node) not in visited:
                self.dfs_util(node, visited)
        return self.__buses
