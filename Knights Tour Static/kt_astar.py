"""
A* Knight's Tour for Levels 1-3.

Informed search: a priority queue holds partial tours, and the one with the
lowest f(n) = g(n) + h(n) is expanded next.

  g(n) = squares visited so far - 1  (moves made)
  h(n) = squares still unvisited
         + knight-move distance to the piece (only before it is captured)
  Ties in f are broken by Warnsdorff degree (fewer onward moves first).

Coordinates: (x, y), 0-indexed, x = column, y = row, (0,0) = top-left.

Levels:
  1: 5x5, no extra piece
  2: 6x6, king at (3,3)  -> attacks its 8 neighbours until captured
  3: 7x7, rook at (3,3)  -> attacks its row and column until captured
"""

import heapq
import itertools
import time
import tracemalloc
from collections import deque

KNIGHT_MOVES = [(1, 2), (2, 1), (-1, 2), (-2, 1),
                (1, -2), (2, -1), (-1, -2), (-2, -1)]

LEVELS = {
    1: {"n": 5, "start": (0, 0), "piece": None,   "kind": None},
    2: {"n": 6, "start": (0, 0), "piece": (3, 3), "kind": "king"},
    3: {"n": 7, "start": (0, 0), "piece": (3, 3), "kind": "rook"},
}

NODE_CAP = 5_000_000        # max states expanded
QUEUE_CAP = 2_000_000       # max partial tours stored at once


def attack_zone(n, piece, kind):
    """Squares the piece attacks (forbidden to the knight until capture)."""
    if piece is None:
        return set()
    px, py = piece
    zone = set()
    for x in range(n):
        for y in range(n):
            if (x, y) == piece:
                continue
            if kind == "king" and max(abs(x - px), abs(y - py)) == 1:
                zone.add((x, y))
            elif kind == "rook" and (x == px or y == py):
                zone.add((x, y))
    return zone


def legal_moves(pos, visited, captured, n, zone):
    """Knight moves to unvisited, on-board squares (avoiding the zone before capture)."""
    for dx, dy in KNIGHT_MOVES:
        q = (pos[0] + dx, pos[1] + dy)
        if 0 <= q[0] < n and 0 <= q[1] < n and q not in visited \
                and (captured or q not in zone):
            yield q


def distance_to_piece(n, piece, zone):
    """BFS from the piece over squares outside its zone: knight-move distances."""
    dist = {piece: 0}
    queue = deque([piece])
    while queue:
        p = queue.popleft()
        for dx, dy in KNIGHT_MOVES:
            q = (p[0] + dx, p[1] + dy)
            if 0 <= q[0] < n and 0 <= q[1] < n and q not in dist and q not in zone:
                dist[q] = dist[p] + 1
                queue.append(q)
    return dist


def astar_tour(n, start, piece=None, kind=None,
               node_cap=NODE_CAP, queue_cap=QUEUE_CAP):
    """Returns (solved, path, nodes_expanded, peak_depth)."""
    zone = attack_zone(n, piece, kind)
    total = n * n

    if start in zone or start == piece:
        raise ValueError("Start square must be outside the piece's square and zone.")

    dist = distance_to_piece(n, piece, zone) if piece else {}

    def h(pos, visited, captured):
        remaining = total - len(visited)
        return remaining + (0 if captured else dist.get(pos, 99))

    def warnsdorff(q, visited, captured):
        c = captured or q == piece
        return sum(1 for _ in legal_moves(q, visited | {q}, c, n, zone))

    counter = itertools.count()          # breaks ties so states are never compared
    start_captured = piece is None
    start_state = (start, (start,), frozenset([start]), start_captured)
    queue = [(h(start, start_state[2], start_captured), 0, 0,
              next(counter), start_state)]

    expanded = 0
    peak_depth = 1

    while queue:
        f, _, g, _, (pos, path, visited, captured) = heapq.heappop(queue)
        expanded += 1
        peak_depth = max(peak_depth, len(path))

        if expanded > node_cap:
            return False, [], expanded, peak_depth
        if len(visited) == total:
            return True, list(path), expanded, peak_depth     # goal reached

        for q in legal_moves(pos, visited, captured, n, zone):
            v2 = visited | {q}
            c2 = captured or q == piece
            f2 = (g + 1) + h(q, v2, c2)
            heapq.heappush(queue, (f2, warnsdorff(q, visited, captured), g + 1,
                                   next(counter), (q, path + (q,), v2, c2)))

        if len(queue) > queue_cap:
            return False, [], expanded, peak_depth

    return False, [], expanded, peak_depth


def print_initial_board(n, start, piece=None, kind=None):
    zone = attack_zone(n, piece, kind)
    symbol = {"king": "K", "rook": "R"}.get(kind, "P")
    for y in range(n):
        row = []
        for x in range(n):
            if (x, y) == start:
                label = "N"
            elif (x, y) == piece:
                label = symbol
            elif (x, y) in zone:
                label = "x"
            else:
                label = "."
            row.append(label.rjust(4))
        print("".join(row))
    legend = "(N = knight"
    if piece:
        legend += f", {symbol} = {kind}, x = attack square ({len(zone)} squares)"
    print(legend + ")")


def print_board(n, path, piece=None):
    """Show the order in which squares were visited (1 = start)."""
    order = {sq: i + 1 for i, sq in enumerate(path)}
    for y in range(n):
        row = []
        for x in range(n):
            label = str(order[(x, y)]) if (x, y) in order else "."
            if (x, y) == piece:
                label += "*"
            row.append(label.rjust(4))
        print("".join(row))
    if piece:
        print("(* = piece square)")


if __name__ == "__main__":
    for level, cfg in LEVELS.items():
        print("================================================================")
        print(f"================== A* Level {level}: initial board ===================")
        print("================================================================")
        print_initial_board(cfg["n"], cfg["start"], cfg["piece"], cfg["kind"])

        tracemalloc.start()
        t = time.time()
        ok, path, nodes, peak = astar_tour(cfg["n"], cfg["start"],
                                           cfg["piece"], cfg["kind"])
        ms = (time.time() - t) * 1000
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        status = "SOLVED" if ok else "NOT SOLVED (hit a cap)"
        print(f"\nLevel {level}: {cfg['n']}x{cfg['n']}, start {cfg['start']}, "
              f"piece {cfg['kind']} {cfg['piece']} -> {status}")
        print(f"  nodes={nodes:,}  peak depth={peak}  peak memory={peak_bytes / 1024:.2f} KB  time={ms:.1f} ms")
        if ok:
            print_board(cfg["n"], path, cfg["piece"])
        print()