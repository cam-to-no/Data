import numpy as np
import numpy.typing as npt

from collections import deque

# pyngspice
def interpolation(y, a, b):
    x_pre = x_post = y_pre = y_post = 0
    for i in range(len(a)):
        if b[1] < y < b[i] or b[i] < y < b[1]:
            x_post, y_post = a[i], b[i]
            x_pre, y_pre = a[i-1], b[i-1]
            dX = x_post - x_pre
            dY = y_post - y_pre
            tan = dY / dX
            # y = y_pre + (tan * (x - x_pre))
            x = x_pre + ((1/tan) * (y - y_pre))
            break
    return x

def get_slope(y, a, b):
    x_pre = x_post = y_pre = y_post = 0
    for i in range(len(a)):
        if b[1] < y < b[i] or b[i] < y < b[1]:
            x_post, y_post = a[i], b[i]
            x_pre, y_pre = a[i-1], b[i-1]
            dX = x_post - x_pre
            dY = y_post - y_pre
            tan = dY / dX
            break
    return tan

def find_delay(data, start_position: str = 'n0', end_position: str = 'n1', vdd: float = 1.0):
    """
    Calculate a delay from start_position to end_position.
    """
    tpd = interpolation(vdd/2, data['time'], data[end_position]) - interpolation(vdd/2, data['time'], data[start_position])
    return tpd

class Node: # 추후에 제일 앞 노드에 저항을 빼도록 바꿔야 될 듯. (driver)

    def __init__(self, r: float = None, c: float = None):
        self.r = r
        self.c = c

        self.ceff = None
        self.ctot = None
        self.s = None
        self.d = None

        self.fanin_node = None
        self.fanout_nodes = []

    def add_fanout_node(self, fanout_node):
        fanout_node.fanin_node = self
        self.fanout_nodes.append(fanout_node)

#Elmore delay from node 0 to node i
# from collections import deque

def bfs(root, reverse=False):
    q = deque()
    q.append(root)
    ans = []

    while q:
        node = q.popleft()
        if node is None:
            continue

        ans.append(node)

        for fanout_node in node.fanout_nodes:
            q.append(fanout_node)

    while ans:
        yield ans.pop(-1 if reverse else 0)

def elmore_delay(node: Node):
    '''
    elmore delay at the node
    '''
    delay = 0
    while node.fanin_node != None:
        delay = delay +(node.r * node.ceff)
        node = node.fanin_node
    return delay

def find_source_slew(ceff_0, slew_data):
    slew_0 = interpolation(ceff_0, slew_data[:, 1], slew_data[:, 0])
    return slew_0

def calculate_propagation_slew(node: Node):
    # segment_delay = node.d - node.fanin_node.d
    segment_delay = node.r * node.ceff
    tr = node.fanin_node.s
    x = segment_delay/tr
    # tr_prime = tr/ (1-x*(1-np.exp(-1/x)))
    tr_prime = tr/ (1-x*(1-np.exp(-1/x))) + segment_delay
    return tr_prime

def calculate_shielding_factor(node: Node):
    k = 1 - (2*node.r*node.ceff/node.fanin_node.s)*(1-np.exp(-node.fanin_node.s/(2*node.r*node.ceff)))
    return k

#iterative algorithm
def estimate_delay(i: int, tree: list[Node], slew_data: npt.NDArray = np.array([None])):
    """
    node0부터 nodei까지의 delay 계산
    """
    iter = 0
    # 1.initialize (ceff = ctot, find source slew s_0)
    for node in bfs(tree[0], reverse=True):
        node.ctot = node.c
        for fanout_node in node.fanout_nodes:
            node.ctot = node.ctot + fanout_node.ctot
        node.ceff = node.ctot

    if(slew_data.any() == None):
        tree[0].s = find_source_slew_sim(tree[0].ceff)
    else:
        tree[0].s = find_source_slew(tree[0].ceff, slew_data)

    while True:
        # 2.forward
        for node in bfs(tree[0]):
            node.d = elmore_delay(node) # delay 계산
            if node.fanin_node != None: # s_0제외, s_1부터 계산
              node.s = calculate_propagation_slew(node)

        # 3.backward
        for node in bfs(tree[0], reverse=True):
            node.ceff = node.c
            for fanout_node in node.fanout_nodes:
              k = calculate_shielding_factor(fanout_node)
              node.ceff = node.ceff + k*fanout_node.ctot
        if(slew_data.any() == None):
            new_source_slew = find_source_slew_sim(tree[0].ceff)
        else:
            new_source_slew = find_source_slew(tree[0].ceff, slew_data)
        iter += 1

        # print(tree[0].s, tree[i].s)
        # print(tree[0].ceff)

        # 4.check
        if (tree[0].s - new_source_slew)/tree[0].s < 0.01:
            break
        else:
            tree[0].s = new_source_slew
    # print(f'iter = {iter}')
    # return elmore_delay_i(i, tree)
    # print(tree[0].s, tree[i].s)
    # for _i in range(i+1):
    #     print(tree[_i].s, end=' ')
    # print()

    # return tree[i].d
    return tree[0].ceff, tree[0].s, tree[i].d, tree[i].s