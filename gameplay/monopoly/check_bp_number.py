def check_bp_number(screenshot):
    if screenshot is None:
        return 0
    bp3 = [865, 456]
    bp2 = [848, 456]
    bp1 = [832, 456]
    pt_bp1 = screenshot[bp1[1], bp1[0]]
    pt_bp2 = screenshot[bp2[1], bp2[0]]
    pt_bp3 = screenshot[bp3[1], bp3[0]]
    b_bp1 = pt_bp1[0]
    b_bp2 = pt_bp2[0]
    b_bp3 = pt_bp3[0]
    g_bp1 = pt_bp1[1]
    g_bp2 = pt_bp2[1]
    g_bp3 = pt_bp3[1]
    r_bp1 = pt_bp1[2]
    r_bp2 = pt_bp2[2]
    r_bp3 = pt_bp3[2]
    limit = 100
    result = 0
    if r_bp1 > limit and g_bp1 > limit and b_bp1 > limit:
        result = 1
    if r_bp2 > limit and g_bp2 > limit and b_bp2 > limit:
        result = 2
    if r_bp3 > limit and g_bp3 > limit and b_bp3 > limit:
        result = 3

    print(f"r_bp1:{r_bp1},r_bp2:{r_bp2},r_bp3:{r_bp3}")
    del pt_bp1
    del pt_bp2
    del pt_bp3
    return result
