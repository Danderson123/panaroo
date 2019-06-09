import numpy as np

def read_presence_absence(filename):

    # load matrix into binary array
    matrix_txt = np.loadtxt(filename, dtype=str, delimiter=",")
    sample_names = matrix_txt[0,15:]
    gene_names = matrix_txt[0,1:]
    pa_matrix = matrix_txt[1:,15:]==""

    return(pa_matrix, gene_names, sample_names)

def get_curve_w_ci(q, m, pa_matrix, n_boot=100, method="chao2"):

    n_samples = np.size(pa_matrix, 1)

    stat_ci = []

    for n in range(1, n_samples+1):

        qm_boot = [get_q_m(pa_matrix[np.random.randint(0,n_samples,n),:]) for i in range(1,n_boot+1)]

        if method=="chao2":
            stat_boot = [chao2(qm[0], qm[1], n_samples) for qm in qm_boot]
        elif method=="ICE":
            stat_boot = [ICE(qm[0], qm[1], n_samples) for qm in qm_boot]
        elif method=="jack1":
            stat_boot = [jackknife(qm[0], qm[1], n_samples, 1) for qm in qm_boot]
        else:
            stat_boot = [jackknife(qm[0], qm[1], n_samples, 2) for qm in qm_boot]

        stat_ci.append(np.quantile(stat_boot, c(0.025,0.5,0.975)))

    return stat_ci

def get_q_m(pa_matrix):
    # q_k be the number of genes present in exactly k genomes
    q = np.bincount(np.sum(pa_matrix, axis=1))
    m = 0.0
    for i in range(1, np.size(q)):
        m += q[i] 
    return q, m

def chao2(q, m, n_samples):
    # calculates the Chao 2 statistic (for replicated incidence data)
    c2 = n_samples + ((m-1)/m) * (q[1]*(q[1]-1))/(2*(q[2]+1))
    return c2

def ICE(q, m, n_samples):
    # ICE estimator of species richness 
    S_infr = np.sum(q[1:11])
    S_freq = np.sum(q[11:n_samples])
    n_infr = sum([i*q[i] for i in range(1,11)])
    C_ice = 1-q[1]/n_infr
    lambda_ice = max((S_infr/C_ice) * (n_infr/(n_infr-1))*sum([i*(i-1)*q[i] for i in range(1,11)])/(n_infr^2), 0)

    return S_freq + S_infr/C_ice + q[1]/C_ice * lambda_ice


def jackknife(q, m, n_samples, order=1):
    # first and second-order jackknife richness estimator
    if order==1:
        S = n_samples + q[1]*((m-1)/m)
    else:
        S = n_samples + ((q[1]*(2*m-3))/m - ((q[2]*np.power(m-2,2))/(m*(m-1))))

    return S
