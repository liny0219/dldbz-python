def extract_value_credential_from_result(result):
    cred = []
    vals = []
    res = result[0]
    for line in res:
        #line[0] = 该行内识别范围的四个坐标
        #line[1] = (识别内容, 置信度)
        vals.append(line[1][0])
        cred.append(line[1][1])
    return vals, cred

def my_str2int(str):
    return int(str.replace(',',''))