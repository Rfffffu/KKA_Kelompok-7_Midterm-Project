import heapq
import time
import tracemalloc # Untuk menghitung penggunaan memori

# PARAMETER MAKSIMAL NODE (bisa diubah-ubah di sini)
MAX_NODES_EXPANDED = 150000

# Pergerakan kuda catur
MOVES = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), 
         (1, -2), (1, 2), (2, -1), (2, 1)]

RED = "\033[91m"
RESET = "\033[0m"

def clear_screen():
    print("\033[2J\033[H", end="")

def is_threatened(nr, nc, alive_enemies):
    for (er, ec), etype in alive_enemies.items():
        dr, dc = nr - er, nc - ec
        if dr == 0 and dc == 0: 
            continue

        if etype == 'k':
            if abs(dr) <= 1 and abs(dc) <= 1: return True
        elif etype == 'p':
            if dr == 1 and abs(dc) == 1: return True
        elif etype in ['r', 'b', 'q']:
            is_diag = (abs(dr) == abs(dc) and dr != 0)
            is_straight = ((dr == 0 and dc != 0) or (dc == 0 and dr != 0))
            
            valid = False
            if etype == 'r' and is_straight: valid = True
            if etype == 'b' and is_diag: valid = True
            if etype == 'q' and (is_straight or is_diag): valid = True
            
            if valid:
                sr = 0 if dr == 0 else (1 if dr > 0 else -1)
                sc = 0 if dc == 0 else (1 if dc > 0 else -1)
                
                curr_r, curr_c = er + sr, ec + sc
                blocked = False
                while (curr_r, curr_c) != (nr, nc):
                    if (curr_r, curr_c) in alive_enemies:
                        blocked = True
                        break
                    curr_r += sr
                    curr_c += sc
                
                if not blocked: 
                    return True
    return False

def get_warnsdorff_degree(r, c, N, visited, alive_enemies):
    degree = 0
    for dr, dc in MOVES:
        nr, nc = r + dr, c + dc
        if 0 <= nr < N and 0 <= nc < N and (nr, nc) not in visited:
            new_alive = alive_enemies.copy()
            if (nr, nc) in new_alive:
                del new_alive[(nr, nc)]
            
            if not is_threatened(nr, nc, new_alive):
                degree += 1
    return degree

def knight_tour_astar(N, start_r, start_c, initial_enemies):
    total_target = N * N
    pq = []
    counter = 0 
    nodes_expanded = 0 # TRACKER NODE
    
    start_path = [(start_r, start_c)]
    start_visited = frozenset(start_path)
    
    alive_enemies = initial_enemies.copy()
    if (start_r, start_c) in alive_enemies:
        del alive_enemies[(start_r, start_c)]
        
    deg = get_warnsdorff_degree(start_r, start_c, N, start_visited, alive_enemies)
    heapq.heappush(pq, (total_target - 1, deg, -counter, start_r, start_c, start_path, start_visited, alive_enemies))
    
    while pq:
        # Hentikan jika melebihi limit
        if nodes_expanded >= MAX_NODES_EXPANDED:
            break
            
        rem, deg, _, r, c, path, visited, alive = heapq.heappop(pq)
        nodes_expanded += 1
        
        if rem == 0:
            return path, nodes_expanded
            
        for dr, dc in MOVES:
            nr, nc = r + dr, c + dc
            if 0 <= nr < N and 0 <= nc < N and (nr, nc) not in visited:
                next_alive = alive.copy()
                if (nr, nc) in next_alive:
                    del next_alive[(nr, nc)]
                    
                if not is_threatened(nr, nc, next_alive):
                    next_path = path + [(nr, nc)]
                    next_visited = visited | frozenset([(nr, nc)])
                    next_deg = get_warnsdorff_degree(nr, nc, N, next_visited, next_alive)
                    
                    counter += 1
                    heapq.heappush(pq, (rem - 1, next_deg, -counter, nr, nc, next_path, next_visited, next_alive))
                    
    return None, nodes_expanded

def print_initial_board(N, start_r, start_c, enemies):
    print("\nBoard Awal:")
    for i in range(N):
        row = ""
        for j in range(N):
            if i == start_r and j == start_c:
                row += " K "
            elif (i, j) in enemies:
                row += f"{RED} {enemies[(i, j)].upper()} {RESET}"
            else:
                row += " . "
        print(row)

def print_final_board(N, path):
    print("\nUrutan Langkah:")
    board = [[" . " for _ in range(N)] for _ in range(N)]
    for step, (r, c) in enumerate(path):
        board[r][c] = f"{step + 1:3}"
    for row in board:
        print("".join(row))

def animate_tour(N, path, initial_enemies, delay=0.6):
    alive_enemies = initial_enemies.copy()
    board = [[" . " for _ in range(N)] for _ in range(N)]
    
    for step, (r, c) in enumerate(path):
        clear_screen()
        print(f"Langkah ke-{step + 1}/{len(path)}")
        print("=" * 20)
        
        if (r, c) in alive_enemies:
            del alive_enemies[(r, c)]
            
        for i in range(N):
            for j in range(N):
                if " K " in board[i][j]:
                    board[i][j] = " . "
                elif board[i][j].strip().isdigit():
                    pass
                elif (i, j) in alive_enemies:
                    board[i][j] = f"{RED} {alive_enemies[(i, j)].upper()} {RESET}"
                else:
                    board[i][j] = " . "
                    
        board[r][c] = " K "
        
        for row in board:
            print("".join(row))
            
        board[r][c] = f"{step + 1:3}"
        time.sleep(delay)

if __name__ == "__main__":
    clear_screen()
    print("=== A* Knight's Tour: Chess Battle ===")
    N = int(input("Masukkan ukuran board (N): "))
    r, c = map(int, input("Posisi awal Kuda (baris kolom): ").split())
    
    num_enemies = int(input("Jumlah bidak musuh: "))
    enemies = {}
    if num_enemies > 0:
        print("Tipe bidak: k (King), q (Queen), r (Rook), b (Bishop), p (Pawn)")
        for i in range(num_enemies):
            tipe, er, ec = input(f"Bidak musuh ke-{i+1} (tipe baris kolom): ").split()
            if tipe.lower() == 'n':
                print("Error: Musuh tidak boleh berjenis Knight/Kuda!")
                exit()
            enemies[(int(er), int(ec))] = tipe.lower()
            
    pilih_animasi = input("Gunakan animasi? (y/n): ").strip().lower()
    
    if pilih_animasi != 'y':
        print_initial_board(N, r, c, enemies)
        
    print(f"\nMencari jalur... (Maks Node: {MAX_NODES_EXPANDED})")
    
    # MULAI TRACKING PERFORMA
    tracemalloc.start()
    start_time = time.perf_counter()
    
    path, nodes_expanded = knight_tour_astar(N, r, c, enemies)
    
    end_time = time.perf_counter()
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    # SELESAI TRACKING PERFORMA
    
    runtime_ms = (end_time - start_time) * 1000
    peak_mem_mb = peak_mem / (1024 * 1024)

    # Cetak Metrik
    print("\n" + "="*30)
    print("HASIL ANALISIS PERFORMA:")
    print(f"Nodes Expanded : {nodes_expanded} nodes")
    print(f"Runtime        : {runtime_ms:.2f} ms")
    print(f"Peak Memory    : {peak_mem_mb:.4f} MB")
    print("="*30)
    
    if path:
        if pilih_animasi == 'y':
            print("\nMemulai animasi dalam 3 detik...")
            time.sleep(3)
            animate_tour(N, path, enemies)
        else:
            print_final_board(N, path)
    else:
        if nodes_expanded >= MAX_NODES_EXPANDED:
            print(f"\nPencarian dihentikan! Melebihi batas maksimal node ({MAX_NODES_EXPANDED}).")
        else:
            print("\nKuda terjebak! Tidak ada jalur yang aman untuk melewati seluruh papan.")