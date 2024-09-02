#include <sqlite3.h>
#include <string>

class Database {
public:
    Database(const std::string& dbPath) {
        sqlite3_open(dbPath.c_str(), &db);
    }

    ~Database() {
        sqlite3_close(db);
    }

    void updatePlayer(int64_t steamid, const std::string& name, int newScore, int score) {
        // Check if player exists
        std::string query = "SELECT COUNT(*) FROM players WHERE id = ?;";
        sqlite3_stmt* stmt;
        sqlite3_prepare_v2(db, query.c_str(), -1, &stmt, nullptr);
        sqlite3_bind_int64(stmt, 1, steamid);
        sqlite3_step(stmt);

        int exists = sqlite3_column_int(stmt, 0);
        sqlite3_finalize(stmt);

        if (exists) {
            std::string updateQuery = "UPDATE players SET name = ?, score = score + ?, killcount = killcount + ? WHERE id = ?;";
            sqlite3_prepare_v2(db, updateQuery.c_str(), -1, &stmt, nullptr);
            sqlite3_bind_text(stmt, 1, name.c_str(), -1, SQLITE_STATIC);
            sqlite3_bind_int(stmt, 2, newScore);
            sqlite3_bind_int(stmt, 3, score);
            sqlite3_bind_int64(stmt, 4, steamid);
        } else {
            std::string insertQuery = "INSERT INTO players (id, name, score, killcount) VALUES (?, ?, ?, ?);";
            sqlite3_prepare_v2(db, insertQuery.c_str(), -1, &stmt, nullptr);
            sqlite3_bind_int64(stmt, 1, steamid);
            sqlite3_bind_text(stmt, 2, name.c_str(), -1, SQLITE_STATIC);
            sqlite3_bind_int(stmt, 3, newScore);
            sqlite3_bind_int(stmt, 4, score);
        }

        sqlite3_step(stmt);
        sqlite3_finalize(stmt);
    }

private:
    sqlite3* db;
};
