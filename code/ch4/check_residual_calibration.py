"""第四章 sec:ch4-null 的补充核对：封闭人群中冻结模型的残差检验是否需要校准刻度。

1v1 人群（4000 人，实力 N(0,200²)，K=32，σ_q=100），预热 1500 轮；随后 2000 局为收敛阶段，
冻结 Ŝ = 收敛阶段平均评分，并在收敛阶段用合并的逻辑回归估计刻度 γ̂（y ~ F(γ(R - R_opp))）；
再用之后的 1000/2000/5000 局做“输后残差 − 赢后残差”的差异检验（双侧 5%）。
输出：未校准 p̂ = F(Ŝ − R_opp) 与校准 p̂ = F(γ̂(Ŝ − R_opp)) 的拒绝率、平均 z 与平均残差差（百分点）。
运行：python code/ch4/check_residual_calibration.py（约 1 分钟，内存 < 1 GB）
"""
import numpy as np
rng=np.random.default_rng(11)
N,K,sq=4000,32.0,100.0
burn,conv,test=1500,2000,5000
F=lambda x:1/(1+10**(-x/400))
s=rng.normal(0,200,N); R=np.zeros(N)
T=conv+test
Y=np.zeros((T,N),bool); RO=np.zeros((T,N),np.float32); RS=np.zeros((T,N),np.float32)
for r in range(burn+T):
    o=np.argsort(R+rng.normal(0,sq,N)); a,b=o[0::2],o[1::2]
    pa=F(s[a]-s[b]); w=rng.random(a.size)<pa; d=K*(w-F(R[a]-R[b]))
    if r>=burn:
        t=r-burn; Y[t,a]=w; Y[t,b]=~w; RO[t,a]=R[b]; RO[t,b]=R[a]; RS[t,a]=R[a]; RS[t,b]=R[b]
    R[a]+=d; R[b]-=d
c=np.log(10)/400
Shat=RS[:conv].mean(0)                    # frozen: mean rating over convergence phase
# global recalibration slope gamma from convergence phase: y ~ F(gamma*(R-Ropp))
x=(RS[:conv]-RO[:conv]).ravel().astype(float); yy=Y[:conv].ravel().astype(float)
g=1.0
for _ in range(25):
    f=F(g*x); grad=(c*x*(yy-f)).sum(); hess=-(c*c*x*x*f*(1-f)).sum(); g-=grad/hess
print("gamma_hat (convergence phase, pooled)", g)
def test(p, Tn):
    y=Y[conv:conv+Tn].astype(float); p=p[:Tn]; r=y-p; v=p*(1-p)
    prev=Y[conv-1:conv+Tn-1]                 # previous game result
    lost=~prev
    B1=(v*lost).sum(0); B0=(v*~lost).sum(0)
    th1=(r*lost).sum(0)/B1; th0=(r*~lost).sum(0)/B0
    z=(th1-th0)/np.sqrt(1/B1+1/B0)
    diff=100*((r*lost).sum(0)/lost.sum(0)-(r*~lost).sum(0)/(~lost).sum(0))
    return (np.abs(z)>1.96).mean(), z.mean(), diff.mean()
p0=F(Shat[None,:]-RO[conv:]); p1=F(g*(Shat[None,:]-RO[conv:]))
for Tn in (1000,2000,5000):
    print(Tn, "uncalibrated rej/meanz/diff(pp)", np.round(test(p0,Tn),4), " calibrated", np.round(test(p1,Tn),4))
