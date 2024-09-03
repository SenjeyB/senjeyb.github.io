#include <iostream>
#include <curl/curl.h>
#include <nlohmann/json.hpp>
#include <сmath>
#include <time.h>
#include "database.cpp"

static size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp) {
    ((std::string*)userp)->append((char*)contents, size * nmemb);
    return size * nmemb;
}

void fetchDataAndProcess() {
    CURL* curl;
    CURLcode res;
    std::string readBuffer;

    curl_global_init(CURL_GLOBAL_ALL);
    curl = curl_easy_init();
    if (curl) {
        time_t currentTime = time(NULL);
        long x = (long)(floor(currentTime / 60.0 / 60.0 / 24.0) - 1);
        char postData[50];
        snprintf(postData, sizeof(postData), "d=%ld", x);

        curl_easy_setopt(curl, CURLOPT_URL, "https://thronebutt.com/api/v0/get/daily");
        curl_easy_setopt(curl, CURLOPT_POST, 1L);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, postData);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);

        struct curl_slist* headers = NULL;
        headers = curl_slist_append(headers, "Content-Type: application/x-www-form-urlencoded");
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

        res = curl_easy_perform(curl);
        if (res != CURLE_OK) {
            std::cerr << "curl_easy_perform() failed: " << curl_easy_strerror(res) << std::endl;
        } else {
            try {
                nlohmann::json jsonData = nlohmann::json::parse(readBuffer);

                const auto& entries = jsonData["entries"];
                Database db("database/players.db");

                int totalPlayers = entries.size();
                for (const auto& entry : entries) {
                    int rank = entry["rank"].get<int>();
                    std::string name = entry["name"].get<std::string>();
                    int score = entry["score"].get<int>();
                    int64_t steamid = entry["steamid"].get<int64_t>();

                    int adjustedScore = ceil((double)((totalPlayers + 1 - rank) * 1000) / (double)totalPlayers);
                    db.updatePlayer(steamid, name, adjustedScore, score);
                }
            } catch (nlohmann::json::parse_error& e) {
                std::cerr << "Failed to parse JSON: " << e.what() << std::endl;
            }
        }
        curl_easy_cleanup(curl);
    }
    curl_global_cleanup();
}


