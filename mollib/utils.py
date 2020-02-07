import numpy as np
import bitarray


class DistanceMatrix:

    """Class for efficient computation of distance matrix"""

    def __init__(self, coord1, coord2=None):
        l1 = len(coord1)
        csq1 = np.sum(coord1 * coord1, axis=1).reshape(1, -1)

        if coord2 is not None:
            l2 = len(coord2)
            csq2 = np.sum(coord2 * coord2, axis=1).reshape(1, -1)
            mat_a = np.repeat(csq1, l2, axis=0).transpose()
            mat_b = np.repeat(csq2, l1, axis=0)
            mat_c = np.dot(coord1, coord2.transpose())
        else:
            mat_a = np.repeat(csq1, l1, axis=0)
            mat_b = mat_a.transpose()
            mat_c = np.dot(coord1, coord1.transpose())

        self.data = mat_a + mat_b - 2 * mat_c

    @property
    def d2(self):
        return self.data

    @property
    def distance_map(self):
        return np.sqrt(np.where(self.data < 1e-6, 0.0, self.data))

    def contact_map(self, distance):
        d2 = distance * distance
        contact_map = np.where(self.data < d2, True, False)
        return bitarray.bitarray(list(contact_map.flatten()))

    def get_contacts(self, distance):
        d2 = distance * distance
        contact_map = np.where(self.data < d2, True, False)
        return np.argwhere(contact_map)


def kabsch(target, query, weights=None, concentric=False):
    """
    Function for the calculation of the best fit rotation.

    target     - a N x 3 np.array with coordinates of the reference structure
    query      - a N x 3 np.array with coordinates of the fitted structure
    weights    - a N-length list with weights - floats from [0:1]
    concentric - True/False specifying if target and query are centered at origin

    IMPORTANT: If weights are not None centering at origin should account for them.
    proper procedure: A -= np.average(A, 0, WEIGHTS)

    returns rotation matrix as 3 x 3 np.array
    """

    if not concentric:
        t = target - np.average(target, axis=0, weights=weights)
        q = query - np.average(query, axis=0, weights=weights)
    else:
        t = target
        q = query

    c = np.dot(weights * t.T, q) if weights else np.dot(t.T, q)
    v, s, w = np.linalg.svd(c)
    d = np.identity(3)
    if np.linalg.det(c) < 0:
        d[2, 2] = -1

    return np.dot(np.dot(w.T, d), v.T)


def rmsd(target, query=None, weights=None):
    _diff = target if query is None else query - target
    _rmsd = np.sqrt(np.average(np.sum(_diff ** 2, axis=1), axis=0, weights=weights))
    return _rmsd if _rmsd > 0.0001 else 0.


def kmedoids(distances, k, tmax=100):
    # determine dimensions of distance matrix
    m, n = distances.shape

    if k > n:
        raise Exception('too many medoids')

    # find a set of valid initial cluster medoid indices since we
    # can't seed different clusters with two points at the same location
    valid_medoid_inds = set(range(n))
    invalid_medoid_inds = set([])
    rs, cs = np.where(distances == 0)
    # the rows, cols must be shuffled because we will keep the first duplicate below
    index_shuf = list(range(len(rs)))
    np.random.shuffle(index_shuf)
    rs = rs[index_shuf]
    cs = cs[index_shuf]
    for r, c in zip(rs, cs):
        # if there are two points with a distance of 0...
        # keep the first one for cluster init
        if r < c and r not in invalid_medoid_inds:
            invalid_medoid_inds.add(c)
    valid_medoid_inds = list(valid_medoid_inds - invalid_medoid_inds)

    if k > len(valid_medoid_inds):
        raise Exception('too many medoids (after removing {} duplicate points)'.format(
            len(invalid_medoid_inds)))

    # randomly initialize an array of k medoid indices
    medoids = np.array(valid_medoid_inds)
    np.random.shuffle(medoids)
    medoids = np.sort(medoids[:k])

    # create a copy of the array of medoid indices
    medoids_new = np.copy(medoids)

    # initialize a dictionary to represent clusters
    clusters = {}
    for t in range(tmax):
        # determine clusters, i. e. arrays of data indices
        means = np.argmin(distances[:, medoids], axis=1)
        for kappa in range(k):
            clusters[kappa] = np.where(means == kappa)[0]
        # update cluster medoids
        for kappa in range(k):
            means = np.mean(distances[np.ix_(clusters[kappa], clusters[kappa])], axis=1)
            j = np.argmin(means)
            medoids_new[kappa] = clusters[kappa][j]
        np.sort(medoids_new)
        # check for convergence
        if np.array_equal(medoids, medoids_new):
            break
        medoids = np.copy(medoids_new)
    else:
        # final update of cluster memberships
        means = np.argmin(distances[:, medoids], axis=1)
        for kappa in range(k):
            clusters[kappa] = np.where(means == kappa)[0]

    # return results
    return medoids, clusters
