import pandas as pd
from datetime import datetime
#douyu_data数据合并
data = pd.DataFrame()
cate = pd.DataFrame()
zhubo = pd.DataFrame()
data1 = pd.DataFrame()
for d in range(3,16):
    print('开始'+str(d)+'日数据整合')
    df = pd.DataFrame()
    filename = ''
    if d<10:
        filename = '/home/miracle/文档/douyu/100'+str(d)
    elif d>=10:
        filename = '/home/miracle/文档/douyu/10'+str(d)
    print('开始'+str(d)+'日数据合并')
    for h in range(24):
        filename1 = filename
        if h<10:
            filename1 = filename1+'0'+str(h)
        elif h>=10:
            filename1 = filename1+str(h)
        try:
            tmpA = pd.read_json(filename1+'Adouyudata.json')
            tmpA['selecttime'] = filename1[-6:]+' 00'
            tmpB = pd.read_json(filename1+'Bdouyudata.json')
            tmpB['selecttime'] = filename1[-6:]+' 30'
        except ValueError:
            print(filename1+'停电数据缺失')
            pass
        df = pd.concat([df,tmpA,tmpB])
    df['hour'] = df['selecttime'].str[4:6]
    df['hour'] = df['hour'].astype('int')
    df['时段'] = None
    df['时段'][(df['hour'] < 8) & (df['hour'] >= 0)] = 0
    df['时段'][(df['hour'] < 16) & (df['hour'] >= 8)] = 1
    df['时段'][(df['hour'] < 24) & (df['hour'] >= 16)] = 2
    cate_tmp = df[['cate_id','cate_name']].drop_duplicates()
    zhubo_tmp = df[['roomid','zhubo']].drop_duplicates()
    g = df.groupby([df['roomid'],df['cate_id'],df['时段']])
    df_tmp = pd.DataFrame()
    df_tmp['online'] = g['online'].mean()
    df_tmp.reset_index(inplace=True)
    data = pd.concat([data,df_tmp])
    cate = pd.concat([cate,cate_tmp]).drop_duplicates()
    zhubo = pd.concat([zhubo,zhubo_tmp]).drop_duplicates()
    print(str(d)+'日数据合并完成')
data.index = range(len(data))
data_g = data.groupby([data['roomid'],data['cate_id'],data['时段']])
data1['平均在线人数'] = data_g['online'].mean()
data1.reset_index(inplace=True)
data1 = pd.merge(data1, cate, how='left', on='cate_id')
data1 = pd.merge(data1, zhubo, how='left', on='roomid')
douyu_data = data1['平均在线人数'].groupby([data1['roomid'],data1['cate_id'],data1['时段']]).mean()
douyu_data = douyu_data.reset_index()
douyu_data['roomid'] = douyu_data['roomid'].astype('int')
douyu_data['cate_id'] = douyu_data['cate_id'].astype('int')
douyu_data['平均在线人数'] = douyu_data['平均在线人数'].astype('int')
#douyuroom_data数据合并
df = pd.DataFrame()
data = pd.DataFrame()
for d in range(3,16):
    filename = ''
    print('10月'+str(d)+'日数据开始合并')
    if d<10:
        filename = '/home/miracle/文档/douyuroom/100'+str(d)
    elif d>=10:
        filename = '/home/miracle/文档/douyuroom/10'+str(d)
    print('开始'+str(d)+'日数据合并')
    for h in range(24):
        filename1 = filename
        if h<10:
            filename1 = filename1+'0'+str(h)+'Bdouyuroomdata.json'
        elif h>=10:
            filename1 = filename1+str(h)+'Bdouyuroomdata.json'
        try:
            tmp = pd.read_json(filename1)
        except ValueError:
            print(filename1+'停电,数据丢失')
            pass
        tmp['weight'] = None
        tmp['weight'][tmp['owner_weight'].str.endswith('t')] = tmp['owner_weight'][
                                                                 tmp['owner_weight'].str.endswith('t')].str[:-1].astype('float') * 1000
        tmp['weight'][tmp['owner_weight'].str.contains('\dg')] = tmp['owner_weight'][
                                                                 tmp['owner_weight'].str.contains('\dg')].str.extract('(\d*?)\D+?').astype('float')/1000
        tmp['weight'][tmp['owner_weight'].str.endswith('kg')] = tmp['owner_weight'][
                                                                  tmp['owner_weight'].str.endswith('kg')].str[:-2].astype('float')
        df = pd.concat([df,tmp])
df['weight'].astype('int',inplace=True)
df.to_csv('/home/miracle/文档/dailyroomdata.csv')
print('数据合并完成\n构造新属性开始')
df['start_time'] = pd.to_datetime(df['start_time'])
df['selecttime'] = pd.to_datetime(df['selecttime'])
g = df.groupby([df['roomid'],df['start_time']])
data['粉丝初值'] = g['fans_num'].min()
data['粉丝终值'] = g['fans_num'].max()
data['鱼丸初值'] = g['weight'].min()
data['鱼丸终值'] = g['weight'].max()
data['下播时间'] = g['selecttime'].max()
data.reset_index(inplace=True)
data['鱼丸增量'] = data['鱼丸终值']-data['鱼丸初值']
data['粉丝增量'] = data['粉丝终值']-data['粉丝初值']
data['直播时长'] = data['下播时间']-data['start_time']
data['hour'] = None
data['时段'] = None
data['hour'] = [i.hour for i in data['start_time']]
#将开播时间分为3个时段7~16,16~23,23~07
data['时段'][(data['hour']<8)&(data['hour']>=0)] = 0
data['时段'][(data['hour']<16)&(data['hour']>=8)] = 1
data['时段'][(data['hour']<24)&(data['hour']>=16)] = 2
l1 = []
l2 = []
l3 = []
l4 = []
l5 = []
for i in data['start_time']:
    l1.append(i.timestamp())

for i in data['直播时长']:
    l2.append(i.seconds)

for i in l1:
    l3.append(datetime.fromtimestamp(i).time().strftime('%H:%S'))

l3 = pd.to_datetime(l3)

for i in l3:
    l4.append(i.timestamp())

data['start_time'] = l4
data['直播时长'] = l2
data1 = pd.DataFrame()
g_data = data.groupby([data['roomid'],data['时段']])
data1['平均开播时间'] = g_data['start_time'].mean()
data1['平均直播时长'] = g_data['直播时长'].mean()
data1['粉丝初始值'] = g_data['粉丝初值'].min()
data1['平均粉丝增量'] = g_data['粉丝增量'].mean()
data1['直播次数'] = g_data['start_time'].count()
data1['鱼丸初始值'] = g_data['鱼丸初值'].min()
data1['平均鱼丸增量'] = g_data['鱼丸增量'].mean()
for i in data1['平均开播时间']:
    l5.append(datetime.fromtimestamp(i).time())

data1['平均开播时间'] = l5
douyuroom_data = data1
#douyu整体数据合并
douyu = pd.merge(douyu_data,douyuroom_data,how='left',on=['roomid','时段'])
douyu.to_csv('/home/miracle/文档/斗鱼数据集.csv')