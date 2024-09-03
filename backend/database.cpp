#include <sqlite3.h>
#include <iostream>
#include <string>

class Database {
public:
    Database(const std::string& dbPath) {
        if (sqlite3_open(dbPath.c_str(), &db) != SQLITE_OK) {
            std::cerr << "Error opening database: " << sqlite3_errmsg(db) << std::endl;
            db = nullptr;  // Убедитесь, что db указывает на nullptr при ошибке
        }
    }

    ~Database() {
        sqlite3_close(db);
    }

    void updatePlayer(int64_t steamid, const std::string& name, int newScore, int score) {
        std::string query = "SELECT COUNT(*) FROM players WHERE id = ?;";
        sqlite3_stmt* stmt;
        sqlite3_prepare_v2(db, query.c_str(), -1, &stmt, nullptr);
        sqlite3_bind_int64(stmt, 1, steamid);
        sqlite3_step(stmt);

        int exists = sqlite3_column_int(stmt, 0);
        sqlite3_finalize(stmt);

        if (exists) {
            std::string updateQuery = "UPDATE players SET name = ?, score = score + ?, killcount = killcount + ? WHERE id = ?;";
            
            int rc = sqlite3_prepare_v2(db, updateQuery.c_str(), -1, &stmt, nullptr);
if (rc != SQLITE_OK) {
    std::cerr << "Error preparing statement: " << sqlite3_errmsg(db) << std::endl;
    return; // или обработать ошибку иным способом
}
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
        if (sqlite3_step(stmt) != SQLITE_DONE) {  // Этот вызов выполняет запрос
            std::cerr << "Error updating player: " << sqlite3_errmsg(db) << std::endl;
        }
        sqlite3_finalize(stmt);
    }

private:
    sqlite3* db;
};
