from math import sqrt
import cv2
from action_executor import *
from bots.bot import Bot

from models.field import Field, Character


class Node:

    def __init__(self, id: int, x: int, y: int):
        self.id = id
        self.x = x
        self.y = y
        self.edges = []

    def xy(self):
        return self.x, self.y

    def __repr__(self):
        return 'n({}: {}, {})'.format(self.id, self.x, self.y)


class ScaredBot(Bot):

    def get_action(self, field: Field):
        graph = self._read_graph('bots/graph.txt')
        for node in graph:
            for edge in node.edges:
                field.image = cv2.line(field.image, node.xy(), edge.xy(), (0, 255, 0))
        current = self._find_node(graph, *field.pacman.xy())
        threat = self._closest(field.pacman, field.ghosts.values())
        field.image = cv2.line(field.image, threat.xy(), field.pacman.xy(), (0, 0, 255), 3)
        furthest = self._furthest_node(self._find_node(graph, *threat.xy()), current.edges, field)
        field.image = cv2.line(field.image, field.pacman.xy(), furthest.xy(), (255, 0, 0), 2)
        return self._move(current, furthest)

    def _find_node(self, graph: list, x: int, y: int):
        return min(graph, key=lambda n: sqrt((n.x - x) ** 2 + (n.y - y) ** 2))

    def _read_graph(self, file: str):
        graph = []
        with open(file) as f:
            lines = f.readlines()
            for line in lines:
                graph.append(Node(*map(int, line.split()[:3])))
            for i, line in enumerate(lines):
                graph[i].edges.extend(map(lambda n: graph[int(n)], line.split()[3:]))
        return graph

    def _closest(self, center: Character, points: list):
        return min(points, key=lambda g: sqrt((center.x - g.x) ** 2 + (center.y - g.y) ** 2))

    def _furthest_node(self, start: Node, finishes: list, field):
        visited = {start}
        queue = {node: 1 for node in start.edges}
        finishes = set(finishes)
        found = set()
        while (len(found) < len(finishes) and len(queue) > 0):
            current = queue.popitem()
            visited.add(current[0])
            if current[0] in finishes:
                found.add(current)
            for node in current[0].edges:
                if node not in visited:
                    queue[node] = current[1] + 1
        target = max(found, key=lambda n: n[1])
        return target[0]

    def _move(self, start, finish):
        dx = start.x - finish.x
        dy = start.y - finish.y
        y = go_up if dy > 0 else go_down
        x = go_left if dx > 0 else go_right
        return (x, y) if dy > dx else (y, x)
