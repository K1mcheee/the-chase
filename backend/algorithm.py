import random
""""
Attributes as String
Set of Attributes as Set
Functional Dependency as Pair/ Tuple

R {"A", "B", "C", "D"}
FDs [({"A"} , {"B"}), ({"C"} , {"A"})]
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

    return res, tbl

def lossless_table(attrs, decom):
    res = []
    for i, d in enumerate(decom, start=1):
        row = {attr: "X" if attr in d else f"{attr}{i}" for attr in attrs}
        res.append(row)
    return res
    

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
