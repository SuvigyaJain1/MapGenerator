from collections import defaultdict


def def_val():
    return []


class Graph:
    def __init__(self):
        self.n_vertices = 0
        self.adj_list = defaultdict(def_val)


    def make_graph_from_multipolygon(self, multi):
                # use intersection and unions
        self.n_vertices = len(list(multi))
        for i in range(self.n_vertices):
            for j in range(i+1, self.n_vertices):
                if multi[i].intersects(multi[j]):
                    self.adj_list[i].append(j)
                    self.adj_list[j].append(i)

    def remove(self, index):
        if index in self.adj_list:
            for adj in  self.adj_list[index]:
                self.adj_list[adj].remove(index)
            del self.adj_list[index]
            self.n_vertices -= 1
