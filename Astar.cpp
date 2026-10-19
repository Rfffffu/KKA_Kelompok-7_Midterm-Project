#include <iostream>
#include <vector>
#include <queue>
#include <cmath>
#include <thread>
#include <chrono>

using namespace std;

int dr[] = {-2, -2, -1, -1, 1, 1, 2, 2};
int dc[] = {-1, 1, -2, 2, -2, 2, -1, 1};

struct Enemy {
    int r, c;
    char type;
};

struct State {
    int rem;
    int deg;
    int counter;
    int r, c;
    vector<pair<int, int>> path;
    vector<vector<bool>> visited;
    uint32_t aliveMask; // Bitmask musuh yang masih hidup (max 32 musuh)

    bool operator>(const State& other) const {
        if (rem != other.rem) return rem > other.rem;
        if (deg != other.deg) return deg > other.deg;
        return counter < other.counter; // LIFO Tie-breaker
    }
};

void clearScreen() {
    cout << "\033[2J\033[H";
}

bool isThreatened(int nr, int nc, const vector<Enemy>& enemies, uint32_t aliveMask) {
    for (int i = 0; i < enemies.size(); i++) {
        if (!(aliveMask & (1 << i))) continue; // Musuh sudah mati
        
        int er = enemies[i].r;
        int ec = enemies[i].c;
        char type = enemies[i].type;
        
        int rowDiff = nr - er;
        int colDiff = nc - ec;
        
        if (rowDiff == 0 && colDiff == 0) continue; // Kita memakan dia, tidak diserang dirinya sendiri
        
        if (type == 'k') {
            if (abs(rowDiff) <= 1 && abs(colDiff) <= 1) return true;
        } else if (type == 'n') {
            if ((abs(rowDiff) == 2 && abs(colDiff) == 1) || (abs(rowDiff) == 1 && abs(colDiff) == 2)) return true;
        } else if (type == 'p') {
            if (rowDiff == 1 && abs(colDiff) == 1) return true; // Pion serang ke bawah
        } else if (type == 'r' || type == 'b' || type == 'q') {
            bool isDiag = (abs(rowDiff) == abs(colDiff) && rowDiff != 0);
            bool isStraight = ((rowDiff == 0 && colDiff != 0) || (colDiff == 0 && rowDiff != 0));
            
            bool valid = false;
            if (type == 'r' && isStraight) valid = true;
            if (type == 'b' && isDiag) valid = true;
            if (type == 'q' && (isStraight || isDiag)) valid = true;
            
            if (valid) {
                int sr = (rowDiff == 0) ? 0 : (rowDiff > 0 ? 1 : -1);
                int sc = (colDiff == 0) ? 0 : (colDiff > 0 ? 1 : -1);
                
                int currR = er + sr;
                int currC = ec + sc;
                bool blocked = false;
                
                // Cek apakah serangan terhalang musuh lain
                while (currR != nr || currC != nc) {
                    for(int j = 0; j < enemies.size(); j++) {
                        if ((aliveMask & (1 << j)) && enemies[j].r == currR && enemies[j].c == currC) {
                            blocked = true;
                            break;
                        }
                    }
                    if (blocked) break;
                    currR += sr;
                    currC += sc;
                }
                if (!blocked) return true;
            }
        }
    }
    return false;
}

int getWarnsdorffDegree(int r, int c, int N, const vector<vector<bool>>& visited, const vector<Enemy>& enemies, uint32_t aliveMask) {
    int degree = 0;
    for (int i = 0; i < 8; i++) {
        int nr = r + dr[i];
        int nc = c + dc[i];
        
        if (nr >= 0 && nr < N && nc >= 0 && nc < N && !visited[nr][nc]) {
            uint32_t nextMask = aliveMask;
            for (int j = 0; j < enemies.size(); j++) {
                if (enemies[j].r == nr && enemies[j].c == nc) {
                    nextMask &= ~(1 << j); // Hapus musuh jika dimakan
                }
            }
            if (!isThreatened(nr, nc, enemies, nextMask)) {
                degree++;
            }
        }
    }
    return degree;
}

void animateTour(int N, const vector<pair<int, int>>& path, vector<Enemy> enemies) {
    vector<vector<string>> board(N, vector<string>(N, " . "));
    uint32_t aliveMask = (1 << enemies.size()) - 1;

    for (int step = 0; step < path.size(); step++) {
        clearScreen();
        int r = path[step].first;
        int c = path[step].second;

        // Cek jika Kuda memakan musuh
        for (int i = 0; i < enemies.size(); i++) {
            if ((aliveMask & (1 << i)) && enemies[i].r == r && enemies[i].c == c) {
                aliveMask &= ~(1 << i);
            }
        }

        cout << "Langkah ke-" << step + 1 << "/" << path.size() << "\n";
        cout << "====================\n";
        
        // Render papan
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                if (i == r && j == c) {
                    cout << " K "; // Kuda
                } else if (board[i][j] != " . ") {
                    cout << board[i][j]; // Jejak langkah angka
                } else {
                    bool hasEnemy = false;
                    for (int k = 0; k < enemies.size(); k++) {
                        if ((aliveMask & (1 << k)) && enemies[k].r == i && enemies[k].c == j) {
                            cout << " " << (char)toupper(enemies[k].type) << " ";
                            hasEnemy = true;
                            break;
                        }
                    }
                    if (!hasEnemy) cout << " . ";
                }
            }
            cout << "\n";
        }
        
        string s = to_string(step + 1);
        while(s.length() < 3) s = " " + s;
        board[r][c] = s;
        
        this_thread::sleep_for(chrono::milliseconds(600));
    }
}

int main() {
    int N, r, c, numEnemies;
    clearScreen();
    cout << "=== A* Knight's Tour: Chess Battle ===\n";
    cout << "Masukkan ukuran board (N): ";
    cin >> N;
    cout << "Posisi awal Kuda (baris kolom, 0-indexed): ";
    cin >> r >> c;

    cout << "Jumlah bidak musuh (maks 32): ";
    cin >> numEnemies;

    vector<Enemy> enemies(numEnemies);
    uint32_t aliveMask = (1 << numEnemies) - 1;

    cout << "Tipe bidak: k (King), q (Queen), r (Rook), b (Bishop), n (Knight), p (Pawn)\n";
    for (int i = 0; i < numEnemies; i++) {
        cout << "Bidak musuh ke-" << (i + 1) << " (tipe baris kolom): ";
        cin >> enemies[i].type >> enemies[i].r >> enemies[i].c;
        enemies[i].type = tolower(enemies[i].type);
        
        // Hapus jika Kuda awal mendarat di atasnya
        if (enemies[i].r == r && enemies[i].c == c) {
            aliveMask &= ~(1 << i);
        }
    }

    priority_queue<State, vector<State>, greater<State>> pq;
    vector<vector<bool>> visited(N, vector<bool>(N, false));
    visited[r][c] = true;
    vector<pair<int, int>> path = {{r, c}};
    
    int counter = 0;
    int deg = getWarnsdorffDegree(r, c, N, visited, enemies, aliveMask);
    pq.push({N * N - 1, deg, counter++, r, c, path, visited, aliveMask});

    cout << "\nMencari jalur... (Bisa memakan waktu jika N besar)\n";

    bool found = false;
    while (!pq.empty()) {
        State curr = pq.top();
        pq.pop();

        if (curr.rem == 0) {
            cout << "\nSolusi ditemukan! Memulai animasi...\n";
            this_thread::sleep_for(chrono::seconds(2));
            animateTour(N, curr.path, enemies);
            found = true;
            break;
        }

        for (int i = 0; i < 8; i++) {
            int nr = curr.r + dr[i];
            int nc = curr.c + dc[i];

            if (nr >= 0 && nr < N && nc >= 0 && nc < N && !curr.visited[nr][nc]) {
                uint32_t nextMask = curr.aliveMask;
                for (int j = 0; j < enemies.size(); j++) {
                    if (enemies[j].r == nr && enemies[j].c == nc) {
                        nextMask &= ~(1 << j);
                    }
                }
                
                if (!isThreatened(nr, nc, enemies, nextMask)) {
                    vector<vector<bool>> nextVisited = curr.visited;
                    nextVisited[nr][nc] = true;
                    
                    vector<pair<int, int>> nextPath = curr.path;
                    nextPath.push_back({nr, nc});
                    
                    int nextDeg = getWarnsdorffDegree(nr, nc, N, nextVisited, enemies, nextMask);
                    pq.push({curr.rem - 1, nextDeg, counter++, nr, nc, nextPath, nextVisited, nextMask});
                }
            }
        }
    }

    if (!found) cout << "\nKuda terjebak! Tidak ada jalur aman.\n";
    return 0;
}