import pandas as pd
from datetime import datetime
from pyecharts import Pie
from pyecharts import Style
from pyecharts import WordCloud
from pyecharts import Line
from pyecharts import Bar3D
data = pd.read_csv('/home/miracle/文档/斗鱼分时段在线人数汇总3.1.csv',index_col=0)
data['总在线人数'] = data['平均在线人数']*data['直播次数']/10000
#平均在线人数单位为 人/30min
#总在线人数单位为 万人/30min
data['在线人数×直播时长'] = data['总在线人数']*data['平均直播时长']*2
#在线人数×直播时长单位为万人
data['在线人数×直播时长'] = data['在线人数×直播时长'].astype('int')
#平均鱼丸增量单位为：kg/次
data['鱼丸增量'] = data['平均鱼丸增量']*data['直播次数']
#鱼丸增量单位为:kg
#平均粉丝增量单位为:人/次
data['粉丝增量'] = data['平均粉丝增量']*data['直播次数']
#粉丝增量单位为:人
data.to_csv('/home/miracle/文档/斗鱼.csv')

g1 = data.groupby([data['cateid'],data['cate_name']])
d1 = pd.DataFrame()
d1['总人数'] = g1['在线人数×直播时长'].sum()
d1.sort_values(by='总人数',inplace=True,ascending=False)
d1.reset_index(inplace=True)
#折线图、斗鱼熊猫在线人数对比
#斗鱼每日在线人数
douyu_num = pd.Series()
for i in range(3,16):
    filename=''
    if i<10:
        filename = '/home/miracle/文档/douyudailydata/100'+str(i)+'.csv'
    elif i>=10:
        filename = '/home/miracle/文档/douyudailydata/10'+str(i)+'.csv'
    try:
        data = pd.read_csv(filename,sep='|',index_col=0)
    except FileNotFoundError:
        print('文档丢失')
        pass
    group = data.drop_duplicates()['online'].groupby(data.drop_duplicates()['selecttime'])
    dailynum = group.sum()
    douyu_num = pd.concat([douyu_num,dailynum])
douyu_num = douyu_num.reset_index()
douyu_num.columns = ['时间','人数']
delta = datetime(2017,1,1)-datetime(1900,1,1)
douyu_num['时间'] = pd.to_datetime(douyu_num['时间'],format='%m%d%H %M')+delta
douyu_num['人数'] = douyu_num['人数'].astype('int')
#熊猫每日在线人数
panda_num = pd.Series()
for i in range(3,16):
    filename=''
    if i<10:
        filename = '/home/miracle/文档/pandatvdailydata/100'+str(i)+'.csv'
    elif i>=10:
        filename = '/home/miracle/文档/pandatvdailydata/10'+str(i)+'.csv'
    try:
        data = pd.read_csv(filename,sep='|',index_col=0)
    except FileNotFoundError:
        print('文档丢失')
        pass
    group = data.drop_duplicates()['watcher'].groupby(data.drop_duplicates()['selecttime'])
    dailynum = group.sum()
    panda_num = pd.concat([panda_num,dailynum])
panda_num = panda_num.reset_index()
panda_num.columns = ['时间','人数']
delta = datetime(2017,1,1)-datetime(1900,1,1)
panda_num['时间'] = pd.to_datetime(panda_num['时间'],format='%m%d%H %M')+delta
panda_num['人数'] = panda_num['人数'].astype('int')
#人数对比
match = pd.merge(douyu_num,panda_num,on='时间')
match.columns = ['时间','斗鱼人数','熊猫人数']
t = match['时间'].iloc[-1]
ts = pd.date_range('2017-10-03',t,freq='1800s')
ts = pd.DataFrame(ts,columns=['时间'])
match = pd.merge(match,ts,on='时间',sort=True,how='right')
match = match.set_index('时间')
match['熊猫人数'][311] = None

def fillna(s,n,k=48):
    z = s[[n-48,n+48]]
    return z.mean()

for i in match.columns:
    for j in range(len(match)):
        if (match[i].isnull())[j]:
            match[i][j] = fillna(match[i],j)
match['熊猫人数'] = match['熊猫人数']*1.3
match = match.resample('8H',how='mean')
attr = match.index
line = Line('斗鱼tv/熊猫tv在线人数对比')
line.add('斗鱼tv',attr,data1['斗鱼人数'])
line.add('熊猫tv',attr,data1['熊猫人数'])
line

#饼图、时段重要性分析
style = Style()
pie_style=style.add(is_random=True,
                    is_label_show=True,
                    radius=[30,50],
                    label_text_color=None,
                    rosetype='radius',
                    label_formatter='{a}:{d}%')
data = pd.read_csv('/home/miracle/文档/斗鱼.csv',index_col=0)
pie = Pie('斗鱼TV时段信息',subtitle='数据爬取自斗鱼TV公共api',title_pos='center',width=1200)
attr = ['午夜档(00:00-07:59)','白天档(08:00-15:59)','夜间档(16:00-23:59)']
g = data.groupby(data['时段'])
a1 = g['在线人数×直播时长'].sum()
a2 = g['鱼丸增量'].sum()
a3 = g['粉丝增量'].sum()
pie.add('在线人数',attr,a1,center=[10,60],**pie_style,legend_pos='left',legend_top='20%',legend_orient='vertical')
pie.add('鱼丸增量',attr,a2,center=[50,60],**pie_style,legend_pos='left',legend_top='20%',legend_orient='vertical')
pie.add('粉丝增量',attr,a3,center=[90,60],**pie_style,legend_pos='left',legend_top='20%',legend_orient='vertical')
pie
#词云图、栏目火爆程度
name = d1['cate_name']
value = d1['总人数']
wc = WordCloud(width=1000,height=600)
wc.add('',name,value,word_size_range=[10,150],shape='triangle-forward')
wc
#折线图、栏目与人数2/8原则
d1['人数'] = None
d1['人数'][d1['总人数']>50000]='50000万人以上'
d1['人数'][(d1['总人数']<=50000)&(d1['总人数']>10000)]='10000万人以上50000万人以下'
d1['人数'][(d1['总人数']<=10000)&(d1['总人数']>1000)]='1000万人以上10000万人以下'
d1['人数'][(d1['总人数']<=1000)&(d1['总人数']>0)]='1000万人以下'
d1['人数'][d1['总人数']==0]='0人'
line = Line('2/8原则',width=1000)
attr = d1.index
y = d1['总人数'].sum()
d1['sum'] = y
line.add('总人数',attr,d1['sum'])
line.add('80%总人数',attr,d1['sum']*0.8,mark_line=['max'],mark_point=[{'coord':['6','817374']}])
line.add('栏目累加人数',attr,d1['总人数'].cumsum(),is_smooth=True,yaxis_formatter="万人")
line

#为不同时段栏目属性进行排序，筛选出排名前十的栏目
l1 = g1['在线人数×直播时长'].sum().sort_values(ascending=False)[:10]
l2 = g1['鱼丸增量'].sum().sort_values(ascending=False)[:10]
l3 = g1['粉丝增量'].sum().sort_values(ascending=False)[:10]
l1 = l1.reset_index()['cateid']
l2 = l2.reset_index()['cateid']
l3 = l3.reset_index()['cateid']
data['时段'][data['时段']==0] = '午夜档'
data['时段'][data['时段']==1] = '白天档'
data['时段'][data['时段']==2] = '夜间档'
cateid = list(data['cateid'].drop_duplicates())
data1 = data[data['cateid'].isin(l1)]
d1 = data1['在线人数×直播时长'].groupby([data1['cate_name'],data1['时段']]).sum().reset_index()
for i in range(len(l1)):
    cateid.remove(list(l1)[i])
data1l =  data[data['cateid'].isin(cateid)]
d1l = data1l['在线人数×直播时长'].groupby(data1l['时段']).sum()
d1l = d1l.reset_index()
d1l['cate_name'] = '其他'
d1 = d1.append(d1l,ignore_index=True)
data2 = data[data['cateid'].isin(l2)]
d2 = data2['鱼丸增量'].groupby([data2['cate_name'],data2['时段']]).sum().reset_index()
cateid = list(data['cateid'].drop_duplicates())
for i in range(len(l2)):
    cateid.remove(list(l2)[i])
data2l =  data[data['cateid'].isin(cateid)]
d2l = data2l['鱼丸增量'].groupby(data2l['时段']).sum()
d2l = d2l.reset_index()
d2l['cate_name'] = '其他'
d2 = d2.append(d2l,ignore_index=True)
data3 = data[data['cateid'].isin(l3)]
d3 = data3['粉丝增量'].groupby([data3['cate_name'],data3['时段']]).sum().reset_index()
cateid = list(data['cateid'].drop_duplicates())
for i in range(len(l3)):
    cateid.remove(list(l3)[i])
data3l =  data[data['cateid'].isin(cateid)]
d3l = data3l['粉丝增量'].groupby(data3l['时段']).sum()
d3l = d3l.reset_index()
d3l['cate_name'] = '其他'
d3 = d3.append(d3l,ignore_index=True)

#3D柱状图
#10大人气栏目分析
bar3d = Bar3D('10大人气栏目时段分析',subtitle='数据爬取自斗鱼api,采用总观众数进行分析',title_pos='center',width=1200,height=800)
a = pd.DataFrame(d1.groupby(d1['cate_name']).sum()).reset_index()
d1 = pd.merge(left=d1,right=a,how='left',on=['cate_name']).sort_values(by='在线人数×直播时长_y',ascending=False)
del(d1['在线人数×直播时长_y'])
x_axis = list(d1['cate_name'].drop_duplicates())
x_axis.remove('其他')
x_axis.append('其他')
y_axis = ['午夜档','白天档','夜间档']
data3d = d1.values
range_color = ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf',
               '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
x_axis
bar3d.add('在线人数×直播时长',x_axis,y_axis,[[d[0],d[2],d[1]]for d in data3d],is_visualmap=True, visual_range=[0, 200000],
          visual_range_color=range_color, grid3d_width=200, grid3d_depth=80,xaxis3d_interval=0,grid3d_shading='lambert',legend_pos='left',legend_top='20%')
bar3d
#10大吸鱼丸栏目分析
bar3d1 = Bar3D('10大最吸鱼丸栏目分析',subtitle='数据爬取自斗鱼api,采用时段鱼丸收入数进行分析',title_pos='center',width=1200,height=800)
b = pd.DataFrame(d2.groupby(d2['cate_name']).sum()).reset_index()
d2 = pd.merge(left=d2,right=b,how='left',on=['cate_name']).sort_values(by='鱼丸增量_y',ascending=False)
x_axis = list(d2['cate_name'].drop_duplicates())
x_axis.remove('其他')
x_axis.append('其他')
y_axis = ['午夜档','白天档','夜间档']
data3d = d2.values
range_color = ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf',
               '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
bar3d1.add('鱼丸时段增量',x_axis,y_axis,[[d[0],d[1],d[2]]for d in data3d],is_visualmap=True, visual_range=[0,60000],
          visual_range_color=range_color, grid3d_width=200, grid3d_depth=80,xaxis3d_interval=0,grid3d_shading='lambert',legend_pos='left',legend_top='20%')
bar3d1
#10大吸粉丝栏目分析
bar3d2 = Bar3D('10大最吸粉丝栏目分析',subtitle='数据爬取自斗鱼api,采用时段粉丝增加总数进行分析',title_pos='center',width=1200,height=800)
c = pd.DataFrame(d3.groupby(d3['cate_name']).sum()).reset_index()
d3 = pd.merge(left=d3,right=c,how='left',on=['cate_name']).sort_values(by='粉丝增量_y',ascending=False)
x_axis = list(d3['cate_name'].drop_duplicates())
x_axis.remove('其他')
x_axis.append('其他')
y_axis = ['午夜档','白天档','夜间档']
data3d = d3.values
range_color = ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf',
               '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
bar3d2.add('粉丝时段增量',x_axis,y_axis,[[d[0],d[1],d[2]]for d in data3d],is_visualmap=True, visual_range=[0,2500000],
          visual_range_color=range_color, grid3d_width=200, grid3d_depth=80,xaxis3d_interval=0,grid3d_shading='lambert',legend_pos='left',legend_top='20%')
bar3d2

