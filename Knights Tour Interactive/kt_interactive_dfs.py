"""
Interactive Knight's Tour using Greedy Best-First Search (GBFS).

Search Logic:
  - Evaluation: h(n) = Warnsdorff onward degree (fewest onward moves first).
  - Tie-breaking:
      1. Deeper partial tours first (-depth / LIFO).
      2. Static move order (index in KNIGHT_MOVES).
      3. Insertion order (counter).
"""

import heapq
import itertools
import time
import tracemalloc

KNIGHT_MOVES = [(1, 2), (2, 1), (-1, 2), (-2, 1),
                (1, -2), (2, -1), (-1, -2), (-2, -1)]

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


def onward_degree(q, visited, captured, n, zone, piece):
    """Warnsdorff score: number of onward moves available from q if visited."""
    c = captured or q == piece
    return sum(1 for _ in legal_moves(q, visited | {q}, c, n, zone))


def gbfs_tour(n, start, piece=None, kind=None,
              node_cap=NODE_CAP, queue_cap=QUEUE_CAP):
    """Returns (solved, path, nodes_expanded, peak_queue, max_depth)."""
    zone = attack_zone(n, piece, kind)
    total = n * n

    if start in zone or start == piece:
        raise ValueError("Start square must be outside the piece's square and attack zone.")

    counter = itertools.count()          # breaks ties so states are never compared directly
    start_captured = piece is None
    start_state = (start, (start,), frozenset([start]), start_captured)

    # Heuristic evaluation: Warnsdorff onward degree only
    h_start = onward_degree(start, start_state[2], start_captured, n, zone, piece)

    # Priority queue tuple: (h, -depth, move_idx, counter, state)
    queue = [(h_start, -1, 0, next(counter), start_state)]

    expanded = 0
    peak_queue = 1
    max_depth = 1

    while queue:
        h, neg_depth, move_idx, _, (pos, path, visited, captured) = heapq.heappop(queue)
        expanded += 1

        current_depth = len(visited)
        if current_depth > max_depth:
            max_depth = current_depth

        if expanded > node_cap:
            return False, list(path), expanded, peak_queue, max_depth
        if current_depth == total:
            return True, list(path), expanded, peak_queue, max_depth     # goal reached

        # Generate candidates in static KNIGHT_MOVES order
        for idx, (dx, dy) in enumerate(KNIGHT_MOVES):
            q = (pos[0] + dx, pos[1] + dy)
            if 0 <= q[0] < n and 0 <= q[1] < n and q not in visited \
                    and (captured or q not in zone):
                v2 = visited | {q}
                c2 = captured or q == piece
                h2 = onward_degree(q, visited, captured, n, zone, piece)
                d2 = len(path) + 1

                heapq.heappush(queue, (h2, -d2, idx, next(counter),
                                       (q, path + (q,), v2, c2)))

        peak_queue = max(peak_queue, len(queue))
        if len(queue) > queue_cap:
            return False, list(path), expanded, peak_queue, max_depth

    return False, [], expanded, peak_queue, max_depth


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
    print("=== Interactive Knight's Tour (GBFS - Pure Warnsdorff) ===")

    try:
        n = int(input("Input board size (n): ").strip())
    except ValueError:
        n = 8
        print(f"Invalid input, using default n = {n}")

    try:
        start_input = input("Input initial knight tile (x y): ").strip()
        sx, sy = map(int, start_input.split())
        start = (sx, sy)
    except Exception:
        start = (0, 0)
        print(f"Invalid input, using default start = {start}")

    enemy_choice = input("enemy type [k (king), r (rook), none]: ").strip().lower()

    piece = None
    kind = None

    if enemy_choice in ["k", "king"]:
        kind = "king"
    elif enemy_choice in ["r", "rook"]:
        kind = "rook"

    if kind is not None:
        try:
            ex, ey = map(int, input("input enemy tile (x y): ").strip().split())
            piece = (ex, ey)
        except Exception:
            piece = (n // 2, n // 2)
            print(f"Invalid input, using default piece = {piece}")
    else:
        print("No enemy piece placed.")

    print(f"\nConfiguration: {n}x{n}, start {start}, piece {piece} ({kind})")
    print_initial_board(n, start, piece, kind)

    tracemalloc.start()
    t = time.time()

    try:
        ok, path, nodes, peak, max_depth = gbfs_tour(n, start, piece, kind)
    except ValueError as e:
        print(f"\nError: {e}")
        tracemalloc.stop()
        exit()

    ms = (time.time() - t) * 1000

    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_mem_kb = peak_mem / 1024

    if ok:
        print()
        print_board(n, path, piece)

    status = "SOLVED" if ok else "NOT SOLVED (hit a cap or exhausted search)"
    print(f"\n-> {status}")
    print(f"nodes={nodes:,}  max depth={max_depth}  peak queue={peak:,}  time={ms:.1f} ms  peak memory={peak_mem_kb:.2f} KB")