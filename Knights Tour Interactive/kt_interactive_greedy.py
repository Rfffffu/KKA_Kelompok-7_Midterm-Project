"""
Greedy (Warnsdorff) Knight's Tour for Custom Board & Enemy Configurations.

Informed search without backtracking: from the current square, move to the
legal square with the FEWEST onward moves (Warnsdorff's rule).

Coordinates: (x, y), 0-indexed, x = column, y = row, (0,0) = top-left.

Supported enemy types:
  - King ('k'): attacks its 8 immediate neighbors
  - Rook ('r'): attacks its row and column
"""

import time
import tracemalloc

KNIGHT_MOVES = [(1, 2), (2, 1), (-1, 2), (-2, 1),
                (1, -2), (2, -1), (-1, -2), (-2, -1)]


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
    """Warnsdorff score: number of moves available from q if we went there."""
    c = captured or q == piece
    return sum(1 for _ in legal_moves(q, visited | {q}, c, n, zone))


def greedy_tour(n, start, piece=None, kind=None):
    """Returns (solved, path, nodes, peak_depth)."""
    zone = attack_zone(n, piece, kind)
    total = n * n

    if start in zone or start == piece:
        raise ValueError("Start square must be outside the piece's square and attack zone.")

    visited = {start}
    path = [start]
    captured = piece is None      # no piece -> nothing to capture
    pos = start

    while len(path) < total:
        candidates = list(legal_moves(pos, visited, captured, n, zone))
        if not candidates:
            return False, path, len(path), len(path)     # stuck: cannot undo moves

        nxt = min(candidates,
                  key=lambda q: onward_degree(q, visited, captured, n, zone, piece))

        visited.add(nxt)
        path.append(nxt)
        if nxt == piece:
            captured = True
        pos = nxt

    return True, path, len(path), len(path)


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
    print("=== Interactive Greedy Warnsdorff Knight's Tour ===")
    
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
        ok, path, nodes, peak = greedy_tour(n, start, piece, kind)
    except ValueError as e:
        print(f"\nError: {e}")
        tracemalloc.stop()
        exit()
        
    ms = (time.time() - t) * 1000
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print()
    print_board(n, path, piece)

    status = "SOLVED" if ok else "STUCK (greedy cannot backtrack)"
    print(f"\n-> {status}")
    print(f"nodes={nodes:,}  peak depth={peak}  peak memory={peak_bytes / 1024:.2f} KB  time={ms:.1f} ms")