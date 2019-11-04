#include <fstream>
#include <iostream>
#include <vector>
#include <tuple>
#include <sstream>
#include <algorithm>
#include <cmath>
#include <ctime>
#include <cstdlib>
#include <cstring>

using namespace std;

vector<tuple<float, float>> load_tsp(char * filename){

    vector<tuple<float, float>> ret;
    string filepath = string(filename);
    
    ifstream ifs;
    ifs.open(filepath);
    char line[100];
    char temp[3][100];
    char * del = " ";

    for(int i=0;;i++){
        ifs.getline(line, 100);
        if(line[0] == '1' || line[0] == ' '){
            stringstream ss(line);
            for(int i=0;i<3;i++){
            ss.getline(temp[i], 90, *del);
        }
            ret.push_back(make_tuple(atof(temp[1]), atof(temp[2])));
            break;
        }
    }
    
    while(ifs.getline(line, 100)){
        if(line[0] == 'E') break;
        stringstream ss(line);
        for(int i=0;i<3;i++){
            ss.getline(temp[i], 90, *del);
        }
        ret.push_back(make_tuple(atof(temp[1]), atof(temp[2])));
    }

    return ret;
}

double dist(tuple<float, float>& from, tuple<float, float>& to){
    float x0 = get<0>(from);
    float y0 = get<1>(from);
    float x1 = get<0>(to);
    float y1 = get<1>(to);
    return sqrt(pow(x1 - x0, 2) + pow(y1 - y0, 2));
}

double dist_sum(vector<tuple<float, float>> &cities, vector<int>& route){
    double ret = 0;

    int len = route.size();
    for(int i=0;i<len;i++){
        ret += dist(cities[route[i]], cities[route[(i+1)%len]]);
    }
    
    return ret;

}

vector<int> readRoute(){
    string filepath = "./solution.csv";
    vector<int> ret;
    ifstream ifs;
    ifs.open(filepath);
    char line[10];

    while(ifs.getline(line, 100)){
        ret.push_back(atoi(line)-1);
    }
    return ret;
}

vector<int> randomRoute(int len){
    vector<int> ret(len, 0);
    for(int i=0;i<len;i++)
        ret[i] = i;
    random_shuffle(ret.begin(), ret.end());
    return ret;

}

vector<int> greedy(vector<tuple<float, float>>& cities, int start){
    
    int len = cities.size();
    vector<int> ret(len, 0);
    vector<int> idx(len, 0);

    for(int i=0;i<len;i++)
        idx[i] = i;
    idx.erase(idx.begin()+start);
    ret[0] = start;

    for(int i=1; i<len;i++){

        tuple<float, float> from = cities[ret[i-1]];

        double min_dist = 900000000;
        auto min_iter = idx.begin();
        for(auto iter=idx.begin();iter!=idx.end();iter++){

            int city_idx = *iter;
            tuple<float, float> to = cities[city_idx];

            double s = dist(from, to);
            if (s < min_dist){
                min_dist = s;
                min_iter = iter;
            }
        }

        ret[i] = *min_iter;
        idx.erase(min_iter);
    }

    return ret;

}

void writeRoute(vector<int> & route){
    string filepath = "./solution.csv";
    ofstream ofs;
    ofs.open(filepath);
    int len = route.size();

    for(int i=0;i<len;i++){
        ofs << route[i] +1 << endl;
    }
}


vector<int> simulatedAnnealing(vector<tuple<float, float>>& cities, vector<int>&route, int fit_evaluations){
    vector<int> s, s_new, s_min;
    s.assign(route.begin(), route.end());
    int len = s.size();
    int c = 100, d = 10, T0 = 10;
    int t = 0;
    double T = c / log(t + d);
    double fs = dist_sum(cities, s);
    double fnews, p, fmin;
    s_min = s;
    fmin = fs;

   
    while(T>T0){
        // get random neighbour
        int i = rand() % len;
        int j;
        do{j = rand() % len;
        }while(i == j);
        s_new.assign(route.begin(), route.end());
        reverse(s_new.begin()+i+1, s_new.begin()+j+1);

        fnews = dist_sum(cities, s_new);
        if(fnews < fs) p = 1.0;
        else p = exp((1/fnews-1/fs)/T);
        if(p >= ((double) rand() / RAND_MAX) ){
            s = s_new;
            fs = fnews;
        }

        T = c / log(t + d);
        t++;
        //printf("[%d] [%f]\n", t, fs);
        if(t+1 > fit_evaluations) break;

        if(fmin > fnews){
            fmin = fnews;
            s_min = s_new;
        }
    }
    return s_min;
}

int main(int argc, char ** argv){


    int fit_evaluations = 3000;
    if(argc > 2 && strcmp(argv[2], "-f") == 0){
        fit_evaluations = atoi(argv[3]);
    }

    vector<tuple<float, float>> cities;
    cities = load_tsp(argv[1]);
    
    int len = cities.size();
    vector<int> route;

    double min_dist = INT32_MAX;
    vector<int> min_route;

    route = greedy(cities, rand()%len);
    min_route = simulatedAnnealing(cities, route, fit_evaluations);
    printf("%f\n", dist_sum(cities, min_route));
    writeRoute(min_route);
    return 0;
}