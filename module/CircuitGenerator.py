from DelayEstimation import Node

def create_RC_tree4(R: list, C: list): # RC tree4(FO1, short)
    """
    rcrcrc
    """
    RC_tree = []
    RC_tree.append(Node(R[0], C[0]))
    RC_tree.append(Node(R[1], C[1]))
    RC_tree.append(Node(R[2], C[2]))
    RC_tree[0].add_fanout_node(RC_tree[1])
    RC_tree[1].add_fanout_node(RC_tree[2])
    return RC_tree

# RC Tree4(FO1,short / RCRCRC) netlist
def create_RC_tree4_netlist(R, C, tr):
    circuit4 = f'''
.title RC_Tree4

R0 IN N0 {R[0]}
R1 N0 N1 {R[1]}
R2 N1 N2 {R[2]}
C0 N0 0 {C[0]}
C1 N1 0 {C[1]}
C2 N2 0 {C[2]}

VIN IN 0 DC 0 PULSE (0 1.0 0 {tr} {tr} 5u 10u)

.tran 1p .2n
.control
run
.endc
.end

'''
    return circuit4

def create_RC_tree2(R: list, C: list): # RC tree(FO1, long)
  RC_tree = []
  RC_tree.append(Node(R[0], C[0]))
  for i in range(len(R)-1):
    RC_tree.append(Node(R[i+1], C[i+1]))
    RC_tree[i].add_fanout_node(RC_tree[i+1])
  return RC_tree

# RC Tree2(FO1,long) netlist
def create_RC_tree2_netlist(R, C, tr):
    circuit2 = f'''
.title RC_Tree2

R0 IN N0 {R[0]}
R1 N0 N1 {R[1]}
R2 N1 N2 {R[2]}
R3 N2 N3 {R[3]}
R4 N3 N4 {R[4]}
R5 N4 N5 {R[5]}
R6 N5 N6 {R[6]}
R7 N6 N7 {R[7]}
C0 N0 0 {C[0]}
C1 N1 0 {C[1]}
C2 N2 0 {C[2]}
C3 N3 0 {C[3]}
C4 N4 0 {C[4]}
C5 N5 0 {C[5]}
C6 N6 0 {C[6]}
C7 N7 0 {C[7]}

VIN IN 0 DC 0 PULSE (0 1.0 0 {tr} {tr} 5u 10u)

.tran 1p 1n
.control
run
.endc
.end

'''
    return circuit2