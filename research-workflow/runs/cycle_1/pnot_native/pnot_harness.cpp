
#include <Eigen/Dense>
#include <iostream>
#include <iomanip>
#include <map>
#include <set>
#include <vector>
#include "header_dist.h"
Eigen::MatrixXd path2adaptedpath(const Eigen::MatrixXd&, double);
void v_set_add(const Eigen::MatrixXd&, std::set<double>&);
Eigen::MatrixXi quantize_path(Eigen::MatrixXd&, std::map<double,int>&);
Eigen::MatrixXi sort_qpath(const Eigen::MatrixXi&);
std::vector<std::map<std::vector<int>,std::map<int,int>>>
qpath2mu_x(Eigen::MatrixXi&, const bool&);
std::vector<ConditionalDistribution> mu_x2kernel_x(
    std::vector<std::map<std::vector<int>,std::map<int,int>>>&);
double Nested(Eigen::MatrixXd&, Eigen::MatrixXd&, double, const bool&, int, int, bool);

void dump(const char* label, Eigen::MatrixXd& paths, double delta,
          bool markov, std::map<double,int>& v2q, std::vector<double>& q2v) {
    Eigen::MatrixXd adapted = path2adaptedpath(paths, delta);
    for (int t=0; t<adapted.rows(); ++t)
        for (int i=0; i<adapted.cols(); ++i)
            std::cout << "QUANT " << label << " " << t << " " << i
                      << " " << adapted(t,i) << "\n";
    Eigen::MatrixXi qpath = sort_qpath(quantize_path(adapted,v2q).transpose());
    auto law = qpath2mu_x(qpath,markov);
    auto kernels = mu_x2kernel_x(law);
    for (int t=0; t<kernels.size(); ++t)
        for (int i=0; i<kernels[t].nc; ++i) {
            std::cout << "COND " << label << " " << t << " " << i;
            for (int code : kernels[t].conds[i]) std::cout << " " << q2v[code];
            std::cout << "\n";
            auto& dist = kernels[t].dists[i];
            for (int j=0; j<dist.values.size(); ++j)
                std::cout << "EDGE " << label << " " << t << " " << i
                          << " " << q2v[dist.values[j]] << " " << dist.weights[j]
                          << "\n";
        }
}

int main() {
    int times, nx, ny, markov_int, power;
    double delta;
    if (!(std::cin >> times >> nx >> ny >> delta >> markov_int >> power)) return 3;
    if (times<2 || nx<1 || ny<1 || !(delta>0) || (power!=1 && power!=2)) return 4;
    Eigen::MatrixXd X(times,nx),Y(times,ny);
    for (int t=0;t<times;++t) for(int i=0;i<nx;++i) if(!(std::cin>>X(t,i))) return 5;
    for (int t=0;t<times;++t) for(int i=0;i<ny;++i) if(!(std::cin>>Y(t,i))) return 6;
    std::cout << std::setprecision(17);
    bool markov = markov_int != 0;
    auto ax=path2adaptedpath(X,delta), ay=path2adaptedpath(Y,delta);
    std::set<double> values; v_set_add(ax,values); v_set_add(ay,values);
    std::map<double,int> v2q; std::vector<double> q2v;
    for(double v:values) { v2q[v]=q2v.size(); q2v.push_back(v); }
    dump("X",X,delta,markov,v2q,q2v); dump("Y",Y,delta,markov,v2q,q2v);
    double value = Nested(X,Y,delta,markov,1,power,false);
    std::cout << "VALUE " << value << "\n";
}
