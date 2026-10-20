"""
Plain DFS (backtracking) Knight's Tour for Custom Board & Enemy Configurations.

Uninformed search: moves are tried in a fixed order, the search goes as deep
as it can, and backs up one step at a time when stuck. No heuristic is used.

Coordinates: (x, y), 0-indexed, x = column, y = row, (0,0) = top-left.

Supported enemy types:
  - King ('k'): attacks its 8 immediate neighbors
  - Rook ('r'): attacks its row and column
  - Bishop ('b'): attacks its diagonals
  - Queen ('q'): attacks its row, column, and diagonals

The tour must visit every square, including the piece's square.
Landing on the piece captures it and removes its attack zone.

"Node" = one call of the recursive search (one state entered), including
states later backed out of. A node cap stops runs that take too long.
"""

import time

KNIGHT_MOVES = [(1, 2), (2, 1), (-1, 2), (-2, 1),
                (1, -2), (2, -1), (-1, -2), (-2, -1)]

NODE_CAP = 5_000_000   # raise this to let DFS run longer (30M takes minutes)


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
            elif kind == "bishop" and abs(x - px) == abs(y - py):
                zone.add((x, y))
            elif kind == "queen" and (x == px or y == py or abs(x - px) == abs(y - py)):
                zone.add((x, y))
    return zone


def legal_moves(pos, visited, captured, n, zone):
    """Knight moves to unvisited, on-board squares (avoiding the zone before capture)."""
    for dx, dy in KNIGHT_MOVES:
        q = (pos[0] + dx, pos[1] + dy)
        if 0 <= q[0] < n and 0 <= q[1] < n and q not in visited \
                and (captured or q not in zone):
            yield q


def dfs_tour(n, start, piece=None, kind=None, node_cap=NODE_CAP):
    """Returns (solved, path, nodes, peak_depth)."""
    zone = attack_zone(n, piece, kind)
    total = n * n

    if start in zone or start == piece:
        raise ValueError("Start square must be outside the piece's square and attack zone.")

    visited = {start}
    path = [start]
    stats = {"nodes": 0, "peak": 1}

    def search(pos, captured):
        stats["nodes"] += 1
        if stats["nodes"] > node_cap:
            return False
        if len(path) == total:
            return True                     # goal: every square visited

        for q in legal_moves(pos, visited, captured, n, zone):
            visited.add(q)
            path.append(q)
            stats["peak"] = max(stats["peak"], len(path))

            if search(q, captured or q == piece):
                return True

            visited.discard(q)              # backtrack
            path.pop()
            if stats["nodes"] > node_cap:
                return False
        return False

    solved = search(start, piece is None)
    return solved, list(path), stats["nodes"], stats["peak"]


def print_initial_board(n, start, piece=None, kind=None):
    zone = attack_zone(n, piece, kind)
    symbol = {"king": "K", "rook": "R", "queen": "Q", "bishop": "B"}.get(kind, "P")
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
    print("=== Interactive Plain DFS (Backtracking) Knight's Tour ===")
    
    # 1. Input board size (n)
    try:
        n = int(input("Input board size (n): ").strip())
    except ValueError:
        n = 5  # Default
        print(f"Invalid input, using default n = {n}")

    # 2. Input initial knight tile (x y)
    try:
        start_input = input("Input initial knight tile (x y): ").strip()
        sx, sy = map(int, start_input.split())
        start = (sx, sy)
    except Exception:
        start = (0, 0)
        print(f"Invalid input, using default start = {start}")

    # 3. Input enemy type (k / r / q / b / none)
    enemy_choice = input("enemy type [k (king), r (rook), q (queen), b (bishop), none]: ").strip().lower()
    
    piece = None
    kind = None

    if enemy_choice in ["k", "king"]:
        kind = "king"
    elif enemy_choice in ["r", "rook"]:
        kind = "rook"
    elif enemy_choice in ["q", "queen"]:
        kind = "queen"
    elif enemy_choice in ["b", "bishop"]:
        kind = "bishop"

    if kind is not None:
        try:
            ex, ey = map(int, input("input enemy tile (x y): ").strip().split())
            piece = (ex, ey)
        except Exception:
            piece = (n // 2, n // 2)
            print(f"Invalid input, using default piece = {piece}")
    else:
        print("No enemy piece placed.")

    # Show Initial Board Layout
    print(f"\nConfiguration: {n}x{n}, start {start}, piece {piece} ({kind})")
    print_initial_board(n, start, piece, kind)

    # Run Plain DFS Search
    t = time.time()
    try:
        ok, path, nodes, peak = dfs_tour(n, start, piece, kind)
    except ValueError as e:
        print(f"\nError: {e}")
        exit()
        
    ms = (time.time() - t) * 1000

    if ok:
        print()
        print_board(n, path, piece)

    status = "SOLVED" if ok else f"NOT SOLVED (hit {NODE_CAP:,} node cap)"
    print(f"-> {status}")
    print(f"nodes={nodes:,}  peak depth={peak}  time={ms:.1f} ms")