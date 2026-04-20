"""
Seed data generator for Robotaxi Feedback Platform.

Two outputs:
1. social_signals.json — 20 real social media posts in social_signal table format
2. feedbacks.json — 200 feedback records (20 real-based + 180 synthetic) with ~20 features each
"""

import json
import random
import uuid
from datetime import datetime, timedelta

random.seed(42)

# ============================================================
# Part 1: Social Signal Records (20 real posts)
# ============================================================

SOCIAL_SIGNALS = [
    {
        "signal_id": "SS001",
        "platform": "douyin",
        "author": "一天八百个情绪的带刺...",
        "content_summary": "今天被困在萝卜车上将近二十分钟，客服电话一直呼叫无法接通，显示5分钟过来的结果等了很久",
        "sentiment": "negative",
        "heat_score": 148,
        "comment_count": 66,
        "share_count": 109,
        "original_url": None,
        "captured_at": "2026-03-31T20:00:00",
        "tags": ["困车内", "客服无法接通", "等待时间长"],
    },
    {
        "signal_id": "SS002",
        "platform": "xiaohongshu",
        "author": "Happy鱼520",
        "content_summary": "你个笨萝卜，1.1公里走了半天还剩9.1公里，问你为什么绕圈圈，你说是为了避开拥堵路段。我让你走最近路线你还不干。结果越绕越远，害得我浪费时间浪费钱，重新打车",
        "sentiment": "negative",
        "heat_score": 13,
        "comment_count": 4,
        "share_count": 1,
        "original_url": None,
        "captured_at": "2026-03-28T14:00:00",
        "tags": ["绕路", "路线不合理", "浪费时间", "费用"],
    },
    {
        "signal_id": "SS003",
        "platform": "douyin",
        "author": "大猫儿导一下",
        "content_summary": "萝卜快跑，有点气人。上下车点有规定，不能随意上车，就是在电商大楼的对面",
        "sentiment": "negative",
        "heat_score": 305,
        "comment_count": 398,
        "share_count": 288,
        "original_url": None,
        "captured_at": "2025-08-05T12:00:00",
        "tags": ["上下车点限制", "不方便"],
    },
    {
        "signal_id": "SS004",
        "platform": "xiaohongshu",
        "author": "武佩",
        "content_summary": "萝卜快跑体验：缺点：接单慢，等待时间长，上车地点受限必须先确定好！急刹体验感差。优点：安全性非常好，特别遵守交通规则，遇到斑马线直接减速，应对复杂车况比我好",
        "sentiment": "neutral",
        "heat_score": 30,
        "comment_count": 8,
        "share_count": 5,
        "original_url": None,
        "captured_at": "2025-11-21T16:00:00",
        "tags": ["接单慢", "急刹", "安全性好", "守交规"],
    },
    {
        "signal_id": "SS005",
        "platform": "douyin",
        "author": "支付人-燕子588",
        "content_summary": "来深圳打车打了一辆无人驾驶的萝卜快跑，最后是我快跑，不然都追不上萝卜快跑",
        "sentiment": "negative",
        "heat_score": 1673,
        "comment_count": 2060,
        "share_count": 1009,
        "original_url": None,
        "captured_at": "2026-03-22T11:00:00",
        "tags": ["追不上车", "上车困难", "深圳"],
    },
    {
        "signal_id": "SS006",
        "platform": "douyin",
        "author": "海市蜃楼",
        "content_summary": "萝卜快跑我坐N次了，便宜倒是便宜，就是慢，还有上车点和下车点离下单有点远，再就是网络不好的时候容易把车开进死胡同",
        "sentiment": "neutral",
        "heat_score": 58,
        "comment_count": 12,
        "share_count": 3,
        "original_url": None,
        "captured_at": "2026-02-10T18:30:00",
        "tags": ["便宜", "慢", "站点远", "网络故障", "死胡同"],
    },
    {
        "signal_id": "SS007",
        "platform": "douyin",
        "author": "幸运李",
        "content_summary": "有一次看到无人驾驶车掉头逆行，还有一次像喝醉了酒，我是告诉家人别坐无人驾驶汽车，有点可怕",
        "sentiment": "negative",
        "heat_score": 3,
        "comment_count": 2,
        "share_count": 0,
        "original_url": None,
        "captured_at": "2026-02-27T09:15:00",
        "tags": ["逆行", "安全隐患", "驾驶异常"],
    },
    {
        "signal_id": "SS008",
        "platform": "douyin",
        "author": "小圆子",
        "content_summary": "这边建议赶时间的朋友千万别坐萝卜快跑，这个笨萝卜它跑不快的！",
        "sentiment": "negative",
        "heat_score": 330,
        "comment_count": 371,
        "share_count": 53,
        "original_url": None,
        "captured_at": "2025-04-02T15:00:00",
        "tags": ["速度慢", "赶时间不推荐"],
    },
    {
        "signal_id": "SS009",
        "platform": "xiaohongshu",
        "author": "八月再见",
        "content_summary": "上车的点没有在我设定的位置，而是自定义在了马路斜对面，要跨过跨栏才能上车。真的太慢了，原本20分钟的路程硬是坐了快40分钟。优点：车内真的很干净，音响效果挺好，座椅体验感也不错，行驶中真的很守交规",
        "sentiment": "neutral",
        "heat_score": 45,
        "comment_count": 15,
        "share_count": 8,
        "original_url": None,
        "captured_at": "2026-03-15T13:00:00",
        "tags": ["上车点偏远", "跨栏", "慢", "车内干净", "守交规"],
    },
    {
        "signal_id": "SS010",
        "platform": "xiaohongshu",
        "author": "文化人",
        "content_summary": "萝卜快跑的车真够笨的，我叫车定位在幼儿园门口，车停在马路对面隔了很高的防护栏。走过去满头大汗，结果超过三分钟就自动取消订单跑了，都碰到车了他都开走了。没有任何人车互动功能",
        "sentiment": "negative",
        "heat_score": 22,
        "comment_count": 10,
        "share_count": 6,
        "original_url": None,
        "captured_at": "2026-03-23T10:30:00",
        "tags": ["自动取消", "防护栏", "等待时间短", "无人车互动"],
    },
    {
        "signal_id": "SS011",
        "platform": "xiaohongshu",
        "author": "Shatia",
        "content_summary": "固定停车点经常更换，我公司本来门口就有停车点的，现在换到步行28分钟的地方去了，谁愿意走啊",
        "sentiment": "negative",
        "heat_score": 5,
        "comment_count": 2,
        "share_count": 0,
        "original_url": None,
        "captured_at": "2025-12-17T08:45:00",
        "tags": ["停车点更换", "步行距离远"],
    },
    {
        "signal_id": "SS012",
        "platform": "xiaohongshu",
        "author": "久久的赛博日记本",
        "content_summary": "来武汉终于打卡萝卜快跑。优点：i人友好不会问东问西，车里没异味，可语音呼唤开启座椅按摩，价格跟顺风车类似。缺点：固定停车点不到用户定位处接客，只能等半分钟，不会倒车要绕一大圈，后备箱开启困难，送达位置固定，下车后拖着行李箱走了二十分钟",
        "sentiment": "neutral",
        "heat_score": 85,
        "comment_count": 32,
        "share_count": 15,
        "original_url": None,
        "captured_at": "2025-09-17T14:28:00",
        "tags": ["i人友好", "等待时间短", "不会倒车", "后备箱", "下车点远", "行李"],
    },
    {
        "signal_id": "SS013",
        "platform": "xiaohongshu",
        "author": "小沪达人Rick",
        "content_summary": "先说优点：私密性强适合商务人士和情侣，车内个性化服务丰富。缺点：价格略微昂贵实际费用超过专车。最后一个缺点直接劝退：整车减震感太差了，明明是城市平坦大道却带来山间崎岖不平的乘坐感",
        "sentiment": "neutral",
        "heat_score": 40,
        "comment_count": 18,
        "share_count": 7,
        "original_url": None,
        "captured_at": "2026-02-20T17:00:00",
        "tags": ["私密性好", "价格贵", "减震差", "乘坐感差"],
    },
    {
        "signal_id": "SS014",
        "platform": "xiaohongshu",
        "author": "咸鱼",
        "content_summary": "我真无语了16分钟的车程开了26分钟，差一点把我搞迟到，一路狂奔到单位1秒钟刚好碰到领导喊大家开周会，差点颜面尽失",
        "sentiment": "negative",
        "heat_score": 28,
        "comment_count": 12,
        "share_count": 4,
        "original_url": None,
        "captured_at": "2026-04-14T08:20:00",
        "tags": ["迟到", "车速慢", "路程时间翻倍"],
    },
    {
        "signal_id": "SS015",
        "platform": "xiaohongshu",
        "author": "Tulips",
        "content_summary": "萝卜快跑体验好差。被停在离目的地隔着围墙200米的马路上，实际狂走2公里才能绕进小区。萝卜没有提醒自行修改了目的地，到快下车才发现不能送进小区。开发人员能不能注意：1.不要自行修改目的地 2.变动目的地了一上车就提醒乘客",
        "sentiment": "negative",
        "heat_score": 35,
        "comment_count": 14,
        "share_count": 9,
        "original_url": None,
        "captured_at": "2026-03-30T19:00:00",
        "tags": ["自动改目的地", "下车点远", "不提醒乘客", "苏州"],
    },
    {
        "signal_id": "SS016",
        "platform": "xiaohongshu",
        "author": "匿名用户",
        "content_summary": "30分钟的路程用了一个多小时并且还没到，客服介入说遇到故障，然后当场直接把我扔路边。请问如果晚上也这样呢随便把人扔路边，不考虑危不危险。客服只会说抱歉问多了就是一套话术，很失望",
        "sentiment": "negative",
        "heat_score": 4,
        "comment_count": 2,
        "share_count": 0,
        "original_url": None,
        "captured_at": "2026-04-01T22:10:00",
        "tags": ["中途故障", "扔路边", "安全隐患", "客服态度差"],
    },
    {
        "signal_id": "SS017",
        "platform": "xiaohongshu",
        "author": "匿名用户(广州)",
        "content_summary": "首先无人是真无人驾驶，加速很快不犹豫，遇到慢车也会顺利绕开。但是上车点非常奇葩在护栏外面，眼睁睁看着车嗖的一下从面前冲了过去差了两百米。下车点也一言难尽，点直接下车显示距离终点过近暂时无法停车，下车点数量有限很多地方不能选",
        "sentiment": "neutral",
        "heat_score": 33,
        "comment_count": 9,
        "share_count": 19,
        "original_url": None,
        "captured_at": "2026-04-14T21:00:00",
        "tags": ["上车点奇葩", "护栏", "下车点有限", "广州"],
    },
    {
        "signal_id": "SS018",
        "platform": "xiaohongshu",
        "author": "喝醉能吃三碗饭",
        "content_summary": "一觉起来准备出门，发现常驻的下车点不见了",
        "sentiment": "negative",
        "heat_score": 1,
        "comment_count": 0,
        "share_count": 0,
        "original_url": None,
        "captured_at": "2025-12-19T07:30:00",
        "tags": ["站点消失", "不稳定"],
    },
    {
        "signal_id": "SS019",
        "platform": "xiaohongshu",
        "author": "久久的赛博日记本",
        "content_summary": "我当时是半分钟，因为等错地方了，所以我赶去的时候，眼睁睁看着它在那里又跑走了。只能重新叫车",
        "sentiment": "negative",
        "heat_score": 2,
        "comment_count": 1,
        "share_count": 0,
        "original_url": None,
        "captured_at": "2025-12-16T09:00:00",
        "tags": ["等待时间短", "车走了", "重新叫车"],
    },
    {
        "signal_id": "SS020",
        "platform": "douyin",
        "author": "匿名用户(武汉)",
        "content_summary": "别坐这个车了，武汉都出事了。它才不傻，有些地方不能停吧，你就是萝卜，快跑",
        "sentiment": "negative",
        "heat_score": 200,
        "comment_count": 80,
        "share_count": 45,
        "original_url": None,
        "captured_at": "2026-03-25T16:00:00",
        "tags": ["安全事故", "武汉", "抵制"],
    },
]

# ============================================================
# Part 2: Full Feedback Records (20 real-based + 180 synthetic)
# ============================================================

# --- Constants ---

CITIES = ["武汉", "北京", "深圳", "广州", "苏州", "重庆", "上海", "长沙"]

ROUTES_BY_CITY = {
    "武汉": [
        "光谷广场-武汉站", "江汉路-楚河汉街", "汉口火车站-武昌站", "光谷-鲁巷",
        "武汉大学-中南路", "汉阳客运站-钟家村", "光谷软件园-关山大道",
        "武汉保利城-光谷世界城", "街道口-中南财经政法大学", "武昌站-东湖绿道",
    ],
    "北京": [
        "中关村-望京", "亦庄-大兴机场", "国贸-三里屯", "西二旗-上地",
        "海淀黄庄-五道口", "亦庄经开区-荣华中路", "通州万达-北京南站",
    ],
    "深圳": [
        "南山科技园-深圳湾", "前海-蛇口", "宝安机场-福田", "坪山-龙岗中心",
        "科兴科学园-深圳北站", "前海自贸区-南山",
    ],
    "广州": [
        "琶洲-珠江新城", "黄埔-科学城", "南沙-万达广场", "天河-番禺",
        "白云机场-广州东站", "大学城-客村",
    ],
    "苏州": [
        "苏州站-观前街", "工业园区-金鸡湖", "吴中区-木渎", "相城-苏州北站",
        "独墅湖-星海广场",
    ],
    "重庆": [
        "解放碑-观音桥", "渝北-江北机场", "沙坪坝-大学城", "南岸-弹子石",
    ],
    "上海": [
        "嘉定-安亭", "临港-滴水湖", "浦东机场-张江", "徐汇-人民广场",
    ],
    "长沙": [
        "梅溪湖-岳麓山", "高铁南站-五一广场", "开福区-芙蓉区",
    ],
}

VEHICLE_IDS = [f"V{random.randint(1000, 9999)}" for _ in range(50)]

CATEGORIES = ["驾驶行为", "接驾体验", "车内环境", "路线规划", "安全感知", "费用相关", "新用户引导", "其他"]

OPERATORS = ["op_zhang", "op_li", "op_wang", "op_chen", "op_liu", "op_zhao"]

# Feedback templates by category for synthetic generation
TEMPLATES = {
    "驾驶行为": [
        "车开得太慢了，{route}本来只要{expected}分钟，结果开了{actual}分钟，差点迟到",
        "急刹车太频繁了，坐了一路感觉像坐过山车，胃都要翻了",
        "在{route}路上遇到施工，车直接停住不动了，等了好几分钟才重新启动",
        "变道的时候特别犹豫，后面的车一直按喇叭，有点尴尬",
        "速度控制还不错，就是遇到红绿灯反应有点慢，绿灯亮了好几秒才起步",
        "跟车距离太近了，前面车一刹车它也急刹，坐着很不舒服",
        "总体行驶体验还可以，就是路口左转的时候等的时间太长了，明明可以过的",
        "在{route}高架上开得很稳，比有些司机强多了，这点好评",
        "加速很猛但是刹车也很急，开起来一顿一顿的，不太适合晕车的人",
        "遇到前方有违停车辆，不会绕行，就停在那里等，等了快5分钟",
        "下雨天开得更慢了，平时20分钟的路开了35分钟",
        "弯道的时候感觉车速没有减下来，有点吓人",
        "上高架的时候加速很流畅，这点比之前坐的好多了",
        "经过学校门口减速太多了，龟速行驶了好久",
        "夜间行驶感觉比白天激进一些，可能是车少的原因",
        "减震太差了，明明是平路，颠得跟越野似的",
        "私密性很好，i人狂喜，不用跟司机尬聊",
        "音响效果挺好的，连上蓝牙放歌很享受",
        "车内有股塑料味，可能是新车的原因，开窗又开不了",
        "后座空间还可以，但是放行李的地方太小了",
        "车内温度控制得不太好，冬天上车冻死了，暖风好久才热",
        "绿色安全带很有设计感，细节好评",
        "前排没人还是有点怪怪的，第一次坐有点紧张",
        "车内氛围灯挺好看的，晚上坐很有感觉",
        "安全带提示音太吵了，一直响个不停",
    ],
    "接驾体验": [
        "上车点离我设的位置很远，还要翻护栏才能过去",
        "等待时间只有半分钟，还没走到车跟前就开走了",
        "固定站点太少了，很多地方打不到车",
        "上下车点经常换，上周还能用的点这周就没了",
        "下车点离目的地太远了，下车后走了快20分钟",
        "站点在马路对面，中间有护栏，根本过不去",
        "预估到达时间不准，说8分钟结果等了15分钟",
        "上车点在一个特别偏僻的地方，大晚上的走过去有点怕",
        "叫了车结果车停在马路对面，中间隔了护栏要绕行好远",
        "等了十多分钟车才到，比预估时间多了快一倍",
        "下车点离小区门口太远了，拖着行李走了快二十分钟",
        "车到了之后找不到在哪里，周围也没有明显标志",
    ],
    "车内环境": [
        "车挺干净的，看得出来有定期打扫",
        "上一个乘客留了垃圾在后座，体验很差",
        "车内有异味，不知道是不是消毒水的味道",
        "座椅上有明显的污渍，希望能及时清洁",
        "车内空调滤芯该换了吧，吹出来的风有味道",
        "屏幕上全是指纹，看着不太卫生",
        "整体很整洁，比很多出租车干净多了，好评",
        "后备箱里面比较脏，放行李有点犹豫",
    ],
    "路线规划": [
        "{route}明明有更近的路，非要绕到{detour}去，多走了好几公里",
        "导航路线很奇怪，绕了一大圈才到目的地",
        "路线规划不考虑实时路况，明知道堵车还往那边走",
        "到目的地附近不能进小区，被放在了围墙外面，走了好远",
        "它自己改了我的目的地，到快下车才发现不对",
        "绕路严重，1公里的路程走了快3公里，浪费时间浪费钱",
        "不走高架走地面，时间多了快一倍",
        "居然走到了单行道口才发现过不去，又绕了一大圈",
        "到了目的地附近停在马路对面，中间隔了护栏，还要绕行500米",
        "路线总体还可以，就是最后一段到小区门口那段不太合理",
    ],
    "安全感知": [
        "在{route}上突然故障停车了，大晚上的被扔在路边，太吓人了",
        "有一次差点撞上逆行的电瓶车，吓死我了",
        "半路突然停下来说遇到特殊情况靠边停车，等了十分钟才有人来处理",
        "感觉车辆识别行人还是有点慢，过斑马线的时候刹车太晚了",
        "第一次坐没有安全员的，心里很忐忑",
        "整体安全性还可以，就是偶尔急刹车让人心惊肉跳的",
        "遇到加塞的车处理得还不错，自动减速让行了",
        "夜间行驶灯光感觉不太够，视野不太好",
        "中途车辆故障，客服说要靠边停车等待处理，前后等了半个多小时",
    ],
    "费用相关": [
        "价格跟顺风车差不多，性价比还可以",
        "新人优惠完了之后价格跟快车差不多，没什么优势了",
        "说好的便宜呢？绕路之后费用比正常打车还贵",
        "行程账单页面显示的价格比预估贵了不少，不太透明",
        "目前是免费体验还行，如果正常收费这个体验真的不值",
        "价格还可以，就是遇到堵车计时费有点坑",
        "对标的是商务专车价格，但体验远不如专车",
        "优惠券挺多的，算下来确实便宜",
    ],
    "新用户引导": [
        "第一次叫车完全不知道怎么上车，在那里站了好久",
        "APP上的上车引导不太清楚，找了半天才找到车",
        "输验证码上车的流程太麻烦了，大热天站在外面操作手机",
        "车内很干净座椅也舒服，就是空调不知道怎么调，问了半天也没搞定",
        "座椅按摩功能不错，但是不太好找在哪里开启",
        "后备箱完全不知道怎么打开，按照引导操作了也没反应",
        "USB充电口在很奇怪的位置，找了半天",
        "车内各种功能按钮不太直观，第一次坐根本不知道怎么操作",
        "不知道怎么调节车内温度，屏幕上的操作指引不够清楚",
    ],
    "其他": [
        "整体体验不错，无人驾驶的感觉很新奇",
        "带孩子体验了一下，小朋友很兴奋，觉得很好玩",
        "作为科技体验还不错，但日常通勤还是算了",
        "一路上好多人在看这辆车，回头率很高哈哈",
        "客服响应太慢了，打了好几个电话才接通",
    ],
}

# Positive templates for high-rating (4-5) feedbacks
POSITIVE_TEMPLATES = {
    "驾驶行为": [
        "行驶非常平稳，遇到慢车也能顺利变道超车，技术进步很大",
        "在{route}上开得很稳，比很多人工司机都靠谱，感觉很安心",
        "速度控制很好，加减速都很平滑，乘坐体验不错",
        "遇到复杂路况处理得很好，没有急刹急转，点赞",
        "在{route}全程很丝滑，完全感受不到是无人驾驶",
        "比上次体验好多了，刹车没那么急了，进步很大",
        "车内很干净很安静，座椅也很舒服，比出租车体验好太多了",
        "i人福音！不用跟司机说话，上车就可以享受自己的空间",
        "座椅按摩太舒服了，音响效果也好，感觉像坐商务车",
        "私密性很好，可以自由调空调温度和音乐，这点好评",
        "绿色安全带有设计感，车内氛围灯也很好看，细节满分",
        "接送女朋友体验了一次，她觉得很有趣很新奇，好评",
    ],
    "接驾体验": [
        "站点就在地铁口旁边，非常方便，换乘体验很好",
        "站点位置标注得很清楚，第一次坐也没有找不到的问题",
        "车来得很快，比预估时间还早到了两分钟，好评",
        "上下车点就在小区门口，非常方便，不用多走路",
    ],
    "车内环境": [
        "车内非常干净整洁，比绝大多数出租车和网约车都好",
        "没有异味，座椅干净，看得出来维护得很用心",
        "车内空调给力，上车就很凉快（或暖和），体验不错",
        "清洁度满分，每次坐都很干净，这点必须表扬",
    ],
    "路线规划": [
        "路线规划很合理，选的路又快又不堵，比我自己导航还好",
        "从{route}走的路线很聪明，避开了高峰堵点，准时到达",
        "导航路线和预估时间很准，基本没有绕路",
        "路线选择挺好的，走的高架很顺畅",
    ],
    "安全感知": [
        "安全性很好，遵守交通规则，遇到行人主动减速让行",
        "感觉比有些人工司机开得还安全，特别规矩",
        "经过学校和小区门口会主动减速，安全意识很强",
        "遇到前方有突发情况反应很快，及时刹车了，感觉很安全",
    ],
    "费用相关": [
        "价格很实惠，比出租车便宜了将近一半，性价比超高",
        "新人优惠加上券，基本等于免费坐了一趟，太划算了",
        "价格跟顺风车差不多，但体验好很多，以后会继续坐",
        "优惠活动很多，算下来比坐公交贵不了多少，值了",
    ],
    "新用户引导": [
        "APP引导很清楚，按照指示很顺利就找到车并上车了",
        "上车流程比我想象的简单，输入手机号后四位就好了",
        "车内屏幕操作指引很清晰，空调音响都一看就会用",
        "第一次坐就上手了，界面很友好，功能一目了然",
    ],
    "其他": [
        "第一次体验无人驾驶，非常酷，科技感拉满！",
        "带家人体验了一次，大家都觉得很新奇，拍了好多照片",
        "整体体验超出预期，会推荐朋友来试试",
        "很有未来感的出行方式，期待越来越普及",
    ],
}


def _gen_id(prefix: str) -> str:
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"


def _random_datetime(start: datetime, end: datetime) -> datetime:
    delta = end - start
    rand_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=rand_seconds)


def _infer_rating_from_sentiment(sentiment: str, text: str) -> int:
    """Infer a 1-5 rating from sentiment and text intensity."""
    negative_strong = ["吓人", "可怕", "扔路边", "危险", "逆行", "出事", "故障", "差", "无语"]
    negative_mild = ["慢", "远", "绕", "不方便", "贵"]
    positive = ["好评", "不错", "干净", "友好", "好", "喜欢", "舒服", "稳"]

    strong_neg = sum(1 for w in negative_strong if w in text)
    mild_neg = sum(1 for w in negative_mild if w in text)
    pos = sum(1 for w in positive if w in text)

    if strong_neg >= 2:
        return 1
    if strong_neg >= 1:
        return random.choice([1, 2])
    if sentiment == "negative":
        return random.choice([1, 2, 2, 3])
    if sentiment == "neutral":
        return random.choice([2, 3, 3, 4])
    return random.choice([3, 4, 4, 5])


def make_real_feedbacks() -> list[dict]:
    """Create 20 feedback records based on the real social media posts."""

    real_data = [
        # 1: 被困车内20分钟
        {
            "feedback_text": "今天被困在萝卜车上将近二十分钟，客服电话一直呼叫无法接通，显示5分钟过来的结果等了很久。太无助了",
            "city": "武汉", "route": "光谷广场-武汉站",
            "rating": 1, "ai_category": "安全感知", "ai_confidence": 0.91,
            "trip_duration": 2400, "cluster_id": "C01",
            "priority": "P1", "source": "social_media",
            "feedback_time": "2026-03-31T20:30:00",
            "trip_time": "2026-03-31T19:50:00",
        },
        # 2: 绕路 1.1km变9.1km
        {
            "feedback_text": "1.1公里走了半天还剩9.1公里，问为什么绕圈圈说是避开拥堵路段。让走最近路线不干，要提前下车还让联系客服，结果越绕越远浪费时间浪费钱，只好重新打车",
            "city": "武汉", "route": "武汉保利城-光谷世界城",
            "rating": 1, "ai_category": "路线规划", "ai_confidence": 0.95,
            "trip_duration": 2700, "cluster_id": "C02",
            "priority": "P1", "source": "social_media",
            "feedback_time": "2026-03-28T15:00:00",
            "trip_time": "2026-03-28T14:10:00",
        },
        # 3: 上下车点限制
        {
            "feedback_text": "萝卜快跑有点气人，上下车点有规定不能随意上车，上车点在电商大楼的对面，还要过马路",
            "city": "武汉", "route": "汉阳客运站-钟家村",
            "rating": 2, "ai_category": "接驾体验", "ai_confidence": 0.88,
            "trip_duration": 1200, "cluster_id": "C03",
            "priority": "P2", "source": "social_media",
            "feedback_time": "2025-08-05T13:00:00",
            "trip_time": "2025-08-05T12:20:00",
        },
        # 4: 急刹差 + 安全好
        {
            "feedback_text": "缺点：接单慢，等待时间长，上车地点受限必须先确定好！急刹体验感差。优点：安全性非常好，特别遵守交通规则，遇到斑马线直接减速，应对复杂车况比我好",
            "city": "武汉", "route": "江汉路-楚河汉街",
            "rating": 3, "ai_category": "驾驶行为", "ai_confidence": 0.85,
            "trip_duration": 1500, "cluster_id": "C04",
            "priority": "P3", "source": "social_media",
            "feedback_time": "2025-11-21T17:00:00",
            "trip_time": "2025-11-21T16:20:00",
        },
        # 5: 深圳追不上车
        {
            "feedback_text": "来深圳打车打了一辆无人驾驶的萝卜快跑，最后是我快跑不然都追不上萝卜快跑。车停的地方离我太远了",
            "city": "深圳", "route": "科兴科学园-深圳北站",
            "rating": 2, "ai_category": "接驾体验", "ai_confidence": 0.87,
            "trip_duration": 900, "cluster_id": "C03",
            "priority": "P2", "source": "social_media",
            "feedback_time": "2026-03-22T12:00:00",
            "trip_time": "2026-03-22T11:30:00",
        },
        # 6: 便宜但慢+死胡同
        {
            "feedback_text": "萝卜快跑我坐N次了，便宜倒是便宜，就是慢，还有上车点和下车点离下单有点远，再就是网络不好的时候容易把车开进死胡同",
            "city": "武汉", "route": "光谷-鲁巷",
            "rating": 3, "ai_category": "路线规划", "ai_confidence": 0.82,
            "trip_duration": 1800, "cluster_id": "C02",
            "priority": "P3", "source": "social_media",
            "feedback_time": "2026-02-10T19:00:00",
            "trip_time": "2026-02-10T18:20:00",
        },
        # 7: 逆行+像喝醉酒
        {
            "feedback_text": "有一次看到无人驾驶车掉头逆行，还有一次像喝醉了酒一样开车，我是告诉家人别坐无人驾驶汽车了，有点可怕",
            "city": "广州", "route": "黄埔-科学城",
            "rating": 1, "ai_category": "安全感知", "ai_confidence": 0.93,
            "trip_duration": 1500, "cluster_id": "C01",
            "priority": "P0", "source": "social_media",
            "feedback_time": "2026-02-27T10:00:00",
            "trip_time": "2026-02-27T09:20:00",
        },
        # 8: 笨萝卜跑不快
        {
            "feedback_text": "建议赶时间的朋友千万别坐萝卜快跑，这个笨萝卜它跑不快的！从汉阳客运站出发慢得让人崩溃",
            "city": "武汉", "route": "汉阳客运站-钟家村",
            "rating": 2, "ai_category": "驾驶行为", "ai_confidence": 0.90,
            "trip_duration": 2400, "cluster_id": "C04",
            "priority": "P2", "source": "social_media",
            "feedback_time": "2025-04-02T16:00:00",
            "trip_time": "2025-04-02T15:10:00",
        },
        # 9: 跨栏上车 + 40分钟 + 车内干净
        {
            "feedback_text": "上车的点在马路斜对面，要跨过跨栏才能上车。原本20分钟的路程硬是坐了快40分钟。不过车内真的很干净，音响效果挺好，座椅也不错，行驶中很守交规",
            "city": "武汉", "route": "街道口-中南财经政法大学",
            "rating": 3, "ai_category": "接驾体验", "ai_confidence": 0.80,
            "trip_duration": 2400, "cluster_id": "C03",
            "priority": "P3", "source": "social_media",
            "feedback_time": "2026-03-15T14:00:00",
            "trip_time": "2026-03-15T13:10:00",
        },
        # 10: 3分钟自动取消
        {
            "feedback_text": "叫车定位在幼儿园门口，车却停在马路对面隔了很高的防护栏。走过去满头大汗，结果超过三分钟就自动取消订单跑了。都碰到车了他都开走了，没有任何人车互动功能",
            "city": "广州", "route": "琶洲-珠江新城",
            "rating": 1, "ai_category": "接驾体验", "ai_confidence": 0.92,
            "trip_duration": 0, "cluster_id": "C03",
            "priority": "P1", "source": "social_media",
            "feedback_time": "2026-03-23T11:00:00",
            "trip_time": "2026-03-23T10:30:00",
        },
        # 11: 停车点经常换
        {
            "feedback_text": "固定停车点经常更换，我公司本来门口就有停车点的，现在换到步行28分钟的地方去了，谁愿意走啊",
            "city": "武汉", "route": "光谷软件园-关山大道",
            "rating": 2, "ai_category": "接驾体验", "ai_confidence": 0.89,
            "trip_duration": 1200, "cluster_id": "C03",
            "priority": "P2", "source": "social_media",
            "feedback_time": "2025-12-17T09:00:00",
            "trip_time": "2025-12-17T08:30:00",
        },
        # 12: i人友好 + 下车走20分钟
        {
            "feedback_text": "优点：i人友好不会问东问西，车里没异味，可以语音开启座椅按摩，价格跟顺风车类似。缺点：固定停车点不到用户定位处接客，只能等半分钟就走了，不会倒车要绕一大圈，后备箱开启困难，下车后拖着行李箱走了二十分钟",
            "city": "武汉", "route": "武汉大学-中南路",
            "rating": 3, "ai_category": "接驾体验", "ai_confidence": 0.84,
            "trip_duration": 2100, "cluster_id": "C05",
            "priority": "P2", "source": "social_media",
            "feedback_time": "2025-09-17T15:30:00",
            "trip_time": "2025-09-17T14:50:00",
        },
        # 13: 减震太差
        {
            "feedback_text": "优点：私密性强适合商务人士和情侣，车内个性化服务丰富。缺点：价格略微昂贵实际费用超过专车。整车减震感太差了，明明是城市平坦大道却带来山间崎岖不平的乘坐感，直接劝退",
            "city": "上海", "route": "嘉定-安亭",
            "rating": 2, "ai_category": "驾驶行为", "ai_confidence": 0.88,
            "trip_duration": 1800, "cluster_id": "C05",
            "priority": "P2", "source": "social_media",
            "feedback_time": "2026-02-20T18:00:00",
            "trip_time": "2026-02-20T17:20:00",
        },
        # 14: 16分钟开了26分钟差点迟到
        {
            "feedback_text": "16分钟的车程开了26分钟，差一点把我搞迟到，一路狂奔到单位刚好碰到领导喊大家开周会，差点颜面尽失",
            "city": "苏州", "route": "工业园区-金鸡湖",
            "rating": 2, "ai_category": "驾驶行为", "ai_confidence": 0.90,
            "trip_duration": 1560, "cluster_id": "C04",
            "priority": "P2", "source": "social_media",
            "feedback_time": "2026-04-14T08:50:00",
            "trip_time": "2026-04-14T08:10:00",
        },
        # 15: 自动改目的地 + 围墙外200米
        {
            "feedback_text": "被停在离目的地隔着围墙200米的马路上，实际狂走2公里才能绕进小区。萝卜没有提醒自行修改了目的地，到快下车才发现不能送进小区。开发人员注意下：不要自行修改目的地，变了就一上车提醒乘客",
            "city": "苏州", "route": "苏州站-观前街",
            "rating": 1, "ai_category": "路线规划", "ai_confidence": 0.93,
            "trip_duration": 1800, "cluster_id": "C02",
            "priority": "P1", "source": "social_media",
            "feedback_time": "2026-03-30T19:30:00",
            "trip_time": "2026-03-30T19:00:00",
        },
        # 16: 中途故障扔路边
        {
            "feedback_text": "30分钟的路程用了一个多小时并且还没到，客服介入说遇到故障，然后当场直接把我扔路边。白天还好，如果晚上这样随便把人扔路边不考虑危不危险。客服只会说抱歉问多了就是一套话术",
            "city": "武汉", "route": "汉口火车站-武昌站",
            "rating": 1, "ai_category": "安全感知", "ai_confidence": 0.95,
            "trip_duration": 3600, "cluster_id": "C01",
            "priority": "P0", "source": "social_media",
            "feedback_time": "2026-04-01T22:30:00",
            "trip_time": "2026-04-01T21:15:00",
        },
        # 17: 广州上车点在护栏外
        {
            "feedback_text": "加速很快不犹豫遇到慢车也会顺利绕开。但上车点非常奇葩在护栏外面，眼睁睁看着车从面前冲了过去差了两百米。下车点也一言难尽，点直接下车显示距离终点过近暂时无法停车",
            "city": "广州", "route": "天河-番禺",
            "rating": 2, "ai_category": "接驾体验", "ai_confidence": 0.86,
            "trip_duration": 2100, "cluster_id": "C03",
            "priority": "P2", "source": "social_media",
            "feedback_time": "2026-04-14T22:00:00",
            "trip_time": "2026-04-14T21:20:00",
        },
        # 18: 下车点消失
        {
            "feedback_text": "一觉起来准备出门，发现常驻的下车点不见了，站点说没就没也不通知一下",
            "city": "武汉", "route": "光谷广场-武汉站",
            "rating": 2, "ai_category": "接驾体验", "ai_confidence": 0.85,
            "trip_duration": 0, "cluster_id": "C03",
            "priority": "P3", "source": "social_media",
            "feedback_time": "2025-12-19T08:00:00",
            "trip_time": "2025-12-19T07:30:00",
        },
        # 19: 等错地方车跑了
        {
            "feedback_text": "因为等错地方了赶过去的时候，眼睁睁看着车在那里又跑走了。只能重新叫车，白白浪费时间",
            "city": "重庆", "route": "解放碑-观音桥",
            "rating": 2, "ai_category": "接驾体验", "ai_confidence": 0.88,
            "trip_duration": 0, "cluster_id": "C03",
            "priority": "P3", "source": "social_media",
            "feedback_time": "2025-12-16T09:30:00",
            "trip_time": "2025-12-16T09:00:00",
        },
        # 20: 武汉出事别坐了
        {
            "feedback_text": "别坐这个车了，武汉都出事了。有些地方不能停，安全性堪忧",
            "city": "武汉", "route": "武昌站-东湖绿道",
            "rating": 1, "ai_category": "安全感知", "ai_confidence": 0.90,
            "trip_duration": 1200, "cluster_id": "C01",
            "priority": "P1", "source": "social_media",
            "feedback_time": "2026-03-25T17:00:00",
            "trip_time": "2026-03-25T16:20:00",
        },
    ]

    feedbacks = []
    for i, rd in enumerate(real_data, 1):
        city = rd["city"]
        fb = {
            "feedback_id": f"F{i:04d}",
            "user_id": f"U{random.randint(10000, 99999)}",
            "trip_id": f"T{random.randint(100000, 999999)}",
            "vehicle_id": random.choice(VEHICLE_IDS),
            "rating": rd["rating"],
            "feedback_text": rd["feedback_text"],
            "city": city,
            "route": rd["route"],
            "trip_time": rd["trip_time"],
            "trip_duration": rd["trip_duration"],
            "feedback_time": rd["feedback_time"],
            "source": rd["source"],
            "ai_category": rd["ai_category"],
            "ai_confidence": rd["ai_confidence"],
            "ai_status": "completed",
            "cluster_id": rd["cluster_id"],
            "priority": rd["priority"],
            "created_at": rd["feedback_time"],
        }
        feedbacks.append(fb)
    return feedbacks


def generate_synthetic_feedbacks(start_index: int, count: int) -> list[dict]:
    """Generate synthetic feedback records with realistic distributions."""

    # Rating distribution: skewed towards 3-4 (most rides are okay-ish)
    rating_weights = {1: 0.10, 2: 0.20, 3: 0.30, 4: 0.25, 5: 0.15}
    ratings = list(rating_weights.keys())
    weights = list(rating_weights.values())

    # City distribution: 武汉 dominant (first mover city)
    city_weights = {
        "武汉": 0.35, "北京": 0.15, "深圳": 0.12, "广州": 0.10,
        "苏州": 0.08, "重庆": 0.07, "上海": 0.08, "长沙": 0.05,
    }

    # Category distribution
    cat_weights = {
        "驾驶行为": 0.28, "接驾体验": 0.18, "车内环境": 0.08,
        "路线规划": 0.15, "安全感知": 0.10, "费用相关": 0.07,
        "新用户引导": 0.10, "其他": 0.04,
    }

    # Source distribution for synthetic data
    source_weights = {
        "app_rating": 0.50, "app_feedback": 0.25,
        "customer_service": 0.15, "social_media": 0.10,
    }

    # Priority: lower ratings → higher priority; most feedbacks have no ticket
    cluster_ids = [f"C{i:02d}" for i in range(1, 16)]

    time_start = datetime(2026, 1, 1)
    time_end = datetime(2026, 4, 15)

    feedbacks = []
    for i in range(count):
        idx = start_index + i
        city = random.choices(list(city_weights.keys()), list(city_weights.values()))[0]
        route = random.choice(ROUTES_BY_CITY[city])
        rating = random.choices(ratings, weights)[0]
        category = random.choices(list(cat_weights.keys()), list(cat_weights.values()))[0]
        source = random.choices(list(source_weights.keys()), list(source_weights.values()))[0]

        # Generate feedback text from templates (sentiment-aligned)
        if rating >= 4:
            templates = POSITIVE_TEMPLATES[category]
        else:
            templates = TEMPLATES[category]
        text = random.choice(templates)
        expected = random.randint(12, 30)
        actual = expected + random.randint(5, 25)
        detour = random.choice(ROUTES_BY_CITY[city])
        text = text.format(route=route, expected=expected, actual=actual, detour=detour)

        # Trip time and duration
        trip_time = _random_datetime(time_start, time_end)
        # Weight towards commute hours
        hour = random.choices(
            list(range(24)),
            [1,0,0,0,0,0,2,5,8,6,3,3,4,3,3,3,4,7,8,5,3,2,1,1]
        )[0]
        trip_time = trip_time.replace(hour=hour, minute=random.randint(0, 59))

        base_duration = random.randint(600, 2400)  # 10-40 min
        if rating <= 2:
            trip_duration = int(base_duration * random.uniform(1.3, 2.0))
        else:
            trip_duration = int(base_duration * random.uniform(0.9, 1.3))

        feedback_time = trip_time + timedelta(minutes=random.randint(5, 120))

        # AI classification
        ai_confidence = round(random.uniform(0.65, 0.98), 2)
        ai_status = "completed" if ai_confidence > 0.5 else "failed"

        # Priority assignment (only some feedbacks get tickets)
        priority = None
        if rating == 1 and category == "安全感知":
            priority = "P0"
        elif rating <= 1:
            priority = random.choice(["P0", "P1"])
        elif rating == 2:
            priority = random.choices(["P1", "P2", "P3", None], [0.15, 0.35, 0.20, 0.30])[0]
        elif rating == 3:
            priority = random.choices(["P2", "P3", None], [0.10, 0.15, 0.75])[0]

        fb = {
            "feedback_id": f"F{idx:04d}",
            "user_id": f"U{random.randint(10000, 99999)}",
            "trip_id": f"T{random.randint(100000, 999999)}",
            "vehicle_id": random.choice(VEHICLE_IDS),
            "rating": rating,
            "feedback_text": text,
            "city": city,
            "route": route,
            "trip_time": trip_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "trip_duration": trip_duration,
            "feedback_time": feedback_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "source": source,
            "ai_category": category,
            "ai_confidence": ai_confidence,
            "ai_status": ai_status,
            "cluster_id": random.choice(cluster_ids),
            "priority": priority,
            "created_at": feedback_time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        feedbacks.append(fb)

    return feedbacks


def main():
    # Generate social signals
    print(f"Generated {len(SOCIAL_SIGNALS)} social signal records")

    # Generate feedbacks
    real_feedbacks = make_real_feedbacks()
    synthetic_feedbacks = generate_synthetic_feedbacks(
        start_index=len(real_feedbacks) + 1,
        count=180,
    )
    all_feedbacks = real_feedbacks + synthetic_feedbacks
    print(f"Generated {len(all_feedbacks)} feedback records ({len(real_feedbacks)} real + {len(synthetic_feedbacks)} synthetic)")

    # Print feature count
    sample = all_feedbacks[0]
    print(f"Features per feedback record: {len(sample)} ({', '.join(sample.keys())})")

    # Write files
    output_dir = "backend/scripts"

    with open(f"{output_dir}/social_signals.json", "w", encoding="utf-8") as f:
        json.dump(SOCIAL_SIGNALS, f, ensure_ascii=False, indent=2)
    print(f"Wrote {output_dir}/social_signals.json")

    with open(f"{output_dir}/feedbacks.json", "w", encoding="utf-8") as f:
        json.dump(all_feedbacks, f, ensure_ascii=False, indent=2)
    print(f"Wrote {output_dir}/feedbacks.json")

    # Summary stats
    print("\n--- Distribution Summary ---")
    from collections import Counter
    cities = Counter(f["city"] for f in all_feedbacks)
    cats = Counter(f["ai_category"] for f in all_feedbacks)
    ratings = Counter(f["rating"] for f in all_feedbacks)
    sources = Counter(f["source"] for f in all_feedbacks)
    priorities = Counter(f["priority"] for f in all_feedbacks if f["priority"])

    print(f"\nBy city: {dict(cities.most_common())}")
    print(f"By category: {dict(cats.most_common())}")
    print(f"By rating: {dict(sorted(ratings.items()))}")
    print(f"By source: {dict(sources.most_common())}")
    print(f"By priority (tickets only): {dict(priorities.most_common())}")
    print(f"Feedbacks with tickets: {sum(1 for f in all_feedbacks if f['priority'])}/{len(all_feedbacks)}")


if __name__ == "__main__":
    main()
