import heapq
import time

# Pergerakan kuda catur
MOVES = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), 
         (1, -2), (1, 2), (2, -1), (2, 1)]

def clear_screen():
    print("\033[2J\033[H", end="")

def is_threatened(nr, nc, alive_enemies):
    """Mengecek apakah petak (nr, nc) sedang diserang oleh musuh yang masih hidup"""
    for (er, ec), etype in alive_enemies.items():
        dr, dc = nr - er, nc - ec
        if dr == 0 and dc == 0: 
            continue # Kita bisa memakan musuh ini, jadi petak ini aman dari dirinya sendiri

        if etype == 'k': # King
            if abs(dr) <= 1 and abs(dc) <= 1: return True
        elif etype == 'n': # Knight
            if (abs(dr) == 2 and abs(dc) == 1) or (abs(dr) == 1 and abs(dc) == 2): return True
        elif etype == 'p': # Pawn (Asumsi jalan ke bawah / row bertambah)
            if dr == 1 and abs(dc) == 1: return True
        elif etype in ['r', 'b', 'q']: # Rook, Bishop, Queen
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
                # Cek apakah ada bidak musuh lain yang menghalangi jalur serangan
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
            # Prediksi state jika kita melangkah ke sana
            new_alive = alive_enemies.copy()
            if (nr, nc) in new_alive:
                del new_alive[(nr, nc)] # Musuh dimakan
            
            if not is_threatened(nr, nc, new_alive):
                degree += 1
    return degree

def knight_tour_astar(N, start_r, start_c, initial_enemies):
    total_target = N * N
    pq = []
    counter = 0 
    
    start_path = [(start_r, start_c)]
    start_visited = frozenset(start_path)
    
    # Kuda memakan musuh di posisi awal (jika ada)
    alive_enemies = initial_enemies.copy()
    if (start_r, start_c) in alive_enemies:
        del alive_enemies[(start_r, start_c)]
        
    if is_threatened(start_r, start_c, alive_enemies):
        print("Peringatan: Posisi awal Anda sedang diserang musuh!")

    deg = get_warnsdorff_degree(start_r, start_c, N, start_visited, alive_enemies)
    # Gunakan minus counter agar LIFO (DFS-like) saat tie-breaker
    heapq.heappush(pq, (total_target - 1, deg, -counter, start_r, start_c, start_path, start_visited, alive_enemies))
    
    while pq:
        rem, deg, _, r, c, path, visited, alive = heapq.heappop(pq)
        
        if rem == 0:
            return path
            
        for dr, dc in MOVES:
            nr, nc = r + dr, c + dc
            if 0 <= nr < N and 0 <= nc < N and (nr, nc) not in visited:
                next_alive = alive.copy()
                if (nr, nc) in next_alive:
                    del next_alive[(nr, nc)] # Kuda memakan musuh!
                    
                if not is_threatened(nr, nc, next_alive):
                    next_path = path + [(nr, nc)]
                    next_visited = visited | frozenset([(nr, nc)])
                    next_deg = get_warnsdorff_degree(nr, nc, N, next_visited, next_alive)
                    
                    counter += 1
                    heapq.heappush(pq, (rem - 1, next_deg, -counter, nr, nc, next_path, next_visited, next_alive))
                    
    return None

def animate_tour(N, path, initial_enemies, delay=0.6):
    alive_enemies = initial_enemies.copy()
    board = [[" . " for _ in range(N)] for _ in range(N)]
    
    for step, (r, c) in enumerate(path):
        clear_screen()
        print(f"Langkah ke-{step + 1}/{len(path)}")
        print("=" * 20)
        
        # Hapus musuh jika dimakan
        if (r, c) in alive_enemies:
            del alive_enemies[(r, c)]
            
        # Gambar ulang papan dengan musuh yang MASIH HIDUP
        for i in range(N):
            for j in range(N):
                if board[i][j] not in [" . ", " K "]:
                    pass # Biarkan angka jejak langkah sebelumnya
                elif (i, j) in alive_enemies:
                    board[i][j] = f" {alive_enemies[(i, j)].upper()} "
                else:
                    if board[i][j] == " K ": board[i][j] = " . "
                    
        # Tandai kuda
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
    print("Tipe bidak: k (King), q (Queen), r (Rook), b (Bishop), n (Knight), p (Pawn)")
    for i in range(num_enemies):
        tipe, er, ec = input(f"Bidak musuh ke-{i+1} (tipe baris kolom): ").split()
        enemies[(int(er), int(ec))] = tipe.lower()
        
    print("\nMencari jalur... (bisa memakan waktu jika N besar)")
    path = knight_tour_astar(N, r, c, enemies)
    
    if path:
        print("\nSolusi ditemukan! Memulai animasi...")
        time.sleep(1.5)
        animate_tour(N, path, enemies)
    else:
        print("\nKuda terjebak! Tidak ada jalur yang aman untuk melewati seluruh papan.")