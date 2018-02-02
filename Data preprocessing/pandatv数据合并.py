#pandatv数据按日合并
import pandas as pd
for d in range(3,16):
    df = pd.DataFrame()
    filename = ''
    if d<10:
        filename = '/home/miracle/文档/panda/10 0'+str(d)+' 17 '
    elif d>=10:
        filename = '/home/miracle/文档/panda/10 '+str(d)+' 17 '
    print('开始'+str(d)+'日数据合并')
    for h in range(24):
        filename1 = filename
        if h<10:
            filename1 = filename1+'0'+str(h)
        elif h>=10:
            filename1 = filename1+str(h)
        try:
            tmpA = pd.read_json(filename1+'Apandadata.json')
            tmpA['selecttime'] = filename1.replace('17 ','').replace(' ','')[-6:]+' 00'
            tmpB = pd.read_json(filename1+'Bpandadata.json')
            tmpB['selecttime'] = filename1.replace('17 ','').replace(' ','')[-6:]+' 30'
        except ValueError:
            print(filename1+'停电数据缺失')
            pass
        df = pd.concat([df,tmpA,tmpB])
    df.to_csv('/home/miracle/文档/pandatvdailydata/'+filename.replace('17 ','').replace(' ','')[-4:]+'.csv',sep='|')
    print(str(d)+'日数据合并完成')