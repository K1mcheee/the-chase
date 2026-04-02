import random
""""
Attributes as String
Set of Attributes as Set
Functional Dependency as Pair/ Tuple

R {"A", "B", "C", "D"}
FDs [({"A"} , {"B"}), ({"C"} , {"A"})]

Set of FDs to test out:
fd1 = [({"A"}, {"B"}), ({"B"}, {"C"}), ({"C"}, {"D"})] 
      {A -> B, B -> C, C -> D}
fd2 = [({"A"}, {"B"}), ({"A", "B"}, {"C", "D"}), ({"C", "D"}, {"E"})] 
      {A -> B, AB -> CD, CD -> E}
fd3 = [({"A", "B"}, {"C", "D", "E"}), ({"A", "C"}, {"B", "D", "E"}), ({"B"}, {"C"}), ({"C"}, {"B"}), ({"C"}, {"D"}), ({"B"}, {"E"}), ({"C"}, {"E"})]
      {AB -> CDE, AC -> BDE, B -> C, C -> B, C -> D, B -> E, C -> E}
fd4 = [({"A", "C"}, {"B", "D"}), ({"A", "D"}, {"C"}), ({"C"}, {"D"}), ({"C", "D"}, {"E"}), ({"E"}, {"D"})]      
      {A,C} → {B,D}, {A,D} → {C}, {C} → {D}, {C,D} → {E}, {E} → {D} 
fd5 = [({"F"},{"D"}), ({"B", "F"}, {"C"}), ({"B", "C", "D", "F"}, {"E"}), ({"D"}, {"B"}), ({"C", "D"}, {"A"}), ({"B", "D"}, {"C"}), ({"A", "D"}, {"C"}), ({"B"}, {"A"})]
      {{F } → {D}, {B, F } → {C}, {B, C, D, F } → {E}, {D} → {B},
        {C, D} → {A}, {B, D} → {C}, {A, D} → {C}, {B} → {A}}
fd6 = [({"A", "B"}, {"C"}), ({"B", "C"}, {"C", "D"}), ({"C", "D"}, {"C", "D"}), ({"D"}, {"A"})]
    {{A, B} → {C}, {B, C} → {C, D}, {C, D} → {C, D}, {D} → {A}}
"""


"""
Attribute closure algorithm
"""
def algo1(R, FDs):
    # Attribute implies itself
    res = set(R)
    # make copy of FDs
    unused = FDs.copy()
    update = True
    # when there are new attributes added, check through again
    while update:
        update = False
        for lhs, rhs in FDs:
            if (lhs, rhs) not in unused:
                continue
            if lhs <= res:  # (lhs, rhs) is in unused
                unused.remove((lhs, rhs))
                # add attribute to closure
                res.update(rhs)
                update = True
    return res

"""
minimal cover algorithm
"""
def algo2(FD):
    tmp = []
    # step 1: simplify RHS
    # this basically splits A -> BC into A -> B and A -> C
    for lhs, rhs in FD:
        # split RHS if > 1 attribute
        if len(rhs) > 1:
            for x in rhs:
                tmp.append((lhs, set(x)))
        else:
            tmp.append((lhs, rhs))

    # step 2 simplify LHS
    # if we have AB -> C, remove A and see if we can still get C from B alone
    # if so, update FD to just B -> C
    for i, (lhs, rhs) in enumerate(tmp):
        curr2 = tmp.copy()
        tset = set(lhs)
        # if LHS > 1 attribute
        if len(lhs) > 1:
            llhs = list(lhs)
            random.shuffle(llhs) # random removal of attribute
            for x in llhs:
                # remove curr attribute
                cls = algo1(tset - {x}, curr2)
                # if logically entail from rest of attribute, remove from FD
                if rhs <= cls:
                    # update set to remove attribute
                    tset = tset - {x}
        tmp[i] = (tset, rhs)

    # step 3 simplify set
    # this removes duplicate FDs and those implied transitively
    # e.g. A -> B, B -> C, A -> C we remove A -> C
    randomtmp = tmp.copy()
    random.shuffle(randomtmp)
    for lhs, rhs in randomtmp:  
        curr = tmp.copy()
        # remove current FD from set
        curr.remove((lhs, rhs))
        # check if can logically entail FD from rest of the set
        cls = algo1(lhs, curr)
        if rhs <= cls:
            # remove FD as it is already logically entailed
            tmp = curr.copy()
    return tmp


def make_table(attrs):
    row1 = {attr : f"a{j+1}" for j,attr in enumerate(attrs)} #create mapping A : a1 B: a2 etc.
    row2 = {attr: f"b{j+1}" for j,attr in enumerate(attrs)} # mapping A: b1 B: b2 etc.
    return [row1, row2]

def chase(attrs, FD, c):
    tbl = make_table(sorted(attrs))
    l,r = c
    for a in l:
        tbl[1][a] = tbl[0][a] # make attr on LHS match the constant row
    changed = True
    while changed:
        # fixpoint iteration, continue when there is change
        changed = False
        for lhs, rhs in FD:
            match = True
            # first, go thru each FD in lhs and check if it matches constant row
            # only if all of LHS match, we can update the RHS values in the 2nd row
            for atr in lhs:
                if (tbl[1][atr] != tbl[0][atr]):
                    match = False # any that don't match, we cannot update
            if match:
                for atr in rhs:
                    # Update only if its not the same value, avoid infinite loop
                    if (tbl[1][atr] != tbl[0][atr]):
                        tbl[1][atr] = tbl[0][atr]
                        changed = True
    res = True
    for a in r:
        # check if any attribute on RHS does not match
        if (tbl[0][a] != tbl[1][a]):
            res = False

    print(tbl)
    return res, tbl

"""
Testcases
"""

fd = [({"A", "C"}, {"B", "D"}), ({"A", "D"}, {"C"}), ({"C"}, {"D"}), ({"C", "D"}, {"E"}), ({"E"}, {"D"})]      

# Minimal Cover
# print("Minimal cover")
# print(algo2(fd))

def parse_and_validate_fds(input):
    # Limit input size
    if len(input) > 1000:  # Arbitrary limit to prevent very large inputs
        raise ValueError("Input is too long.")

    fds = []
    splt = input.strip().split(",")  # Split by commas
    if len(splt) < 2:
        raise ValueError("Attributes must be followed by at least 1 FD.")

    attrs = splt[0].strip().upper()
    attrSet = set(attrs)

    if not all(attr.isalnum() for attr in attrSet):
        raise ValueError("Invalid attributes")

    for line in splt[1:]:
        # Ensure FD format "LHS -> RHS"
        if "->" not in line:
            raise ValueError(f"Invalid format in line: {line.strip()}")

        lhs, rhs = line.split("->")
        lhs = set(lhs.strip().upper())  # Convert LHS to set of characters
        rhs = set(rhs.strip().upper())  # Convert RHS to set of characters

        # Ensure attributes are valid (e.g., only alphanumeric characters)
        if not all(attr.isalnum() for attr in lhs.union(rhs)):
            raise ValueError(f"Invalid attributes in FD: {line.strip()}")

        # Append the FD as a tuple
        fds.append((lhs, rhs))
    return attrSet, fds
attrs, fds = parse_and_validate_fds("Abcde, ac->bd, ad->c, c->d, cd->e, e->d")


# Chase
# print("\nChase")
chaseR14 = {"A", "B", "C", "D", "E", "F", "G", "H", "I", "J"}
chaseFD14 = [
    ({"A"}, {"B"}), ({"B"}, {"A"}), # Cycle
    ({"A", "C"}, {"D"}),
    ({"D"}, {"E", "F"}),
    ({"F", "G"}, {"H"}),
    ({"H"}, {"I"}),
    ({"I", "J"}, {"A"}),
    ({"B", "C"}, {"I"})
]
# print(chase(chaseR14, chaseFD14, ({"A", "C", "G", "J"}, {"I"})))


decom1 = [["A", "B", "C"], ["B", "C", "D"], ["C", "D", "E"]]
decom2 = [["A", "B", "C"], ["B", "C", "D"], ["A", "E"]]


def lossless_table(attrs, decom):
    res = []
    for i, d in enumerate(decom, start=1):
        row = {attr: "X" if attr in d else f"{attr}{i}" for attr in attrs}
        res.append(row)
    return res


chaseR15 = {"A", "B", "C", "D", "E"}
chaseFD15 = [
    ({"A", "B"}, {"C"}), ({"A", "C"}, {"B", "D"}),
    ({"C"}, {"A", "B"}), ({"D"}, {"A", "E"}),
    ({"B", "D"}, {"A", "C"})
    ]
# AB -> C
# AC -> BD
# C -> AB
# D -> AE
# BD -> AC   
    
print("\nLossless Table")
print(lossless_table(sorted(chaseR15), decom1))
    

def lossless_chase(attrs, FD, decom):

    tbl = lossless_table(sorted(attrs), decom)
    changed = True

    while changed:
        changed = False
        for lhs, rhs in FD:
            for i, row_i in enumerate(tbl):
                for j, row_j in enumerate(tbl):
                    if i >= j:
                        continue

                    lhs_match = all(row_i[attr] == row_j[attr] for attr in lhs)
                
                    if not lhs_match:
                        continue
                    
                    for attr in rhs:
                        if row_i[attr] == "X" and row_j[attr] != "X":
                            row_j[attr] = "X"
                            changed = True
                        elif row_j[attr] == "X" and row_i[attr] != "X":
                            row_i[attr] = "X"
                            changed = True

        if any(all(v == "X" for v in row.values()) for row in tbl):
            return (True, tbl)
    
    return (False, tbl)

def format_table(tbl):
    if not tbl:
        return "No data"
    
    columns = tbl[0].keys()

    col_widths = {col: max(len(str(col)), max(len(str(row[col])) for row in tbl)) for col in columns}

    header = " | ".join(f"{col:{col_widths[col]}}" for col in columns)
    separator = "-+-".join("-" * col_widths[col] for col in columns)

    rows = []
    for row in tbl:
        rows.append(" | ".join(f"{str(row[col]):{col_widths[col]}}" for col in columns))

    return "\n".join([header, separator] + rows)

# tbl = [{'A': 'X', 'B': 'X', 'C': 'X', 'D': 'D1', 'E': 'E1'}, {'A': 'A2', 'B': 'X', 'C': 'X', 'D': 'X', 'E': 'E2'}, {'A': 'A3', 'B': 'B3', 'C': 'X', 'D': 'X', 'E': 'X'}]


# print("\nLossless Chase")
# decom1 is True, decom2 is False (based on L08)
# print("\ndecom1:", lossless_chase(chaseR15, chaseFD15, decom1))
# print("\ndecom2:", lossless_chase(chaseR15, chaseFD15, decom2))
