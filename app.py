import requests, pandas, pandas_ta

SET_COIN = 'BTC' # เหรียญหรือโทเคนที่เราต้องการ

SET_TIMEFRAME = '240' # Timeframe ที่เราต้องการ (1, 5, 15, 60, 240, 1D)

SET_DATA_FROM = 1296000 # range กราฟ นับจากปัจจุบันถอยกลับไป ค่าเป็น Timestamp
# 1 นาที คือ 60 ดังนั้นถ้าสมมติเราเลือก Timeframe 1 นาที(1) แล้วอยากได้แท่งเทียน 90 แท่ง ก็เท่ากับ 60*90 = 5400
# ถ้าสมมติเราเลือก Timeframe 4 ชั่วโมง(240) แล้วอยากได้แท่งเทียน 90 แท่ง ก็เท่ากับ ((60*60)*4)*90 = 1296000
# ถ้าตั้ง SET_DATA_FROM ต่ำเกินไป จะทำให้ indicator ข้างล่าง error ได้ แนะนำว่าใช้สัก 90 แท่ง

BK_API = 'https://api.bitkub.com' # API server ของบิทคับ

# ขอ timestamp จากบิทคับ
ex_timestamp = requests.get(BK_API + '/api/servertime')
ex_timestamp = int(ex_timestamp.text) # แปลงให้เป็น int

# ขอข้อมูล chart จากบิทคับ
chart_data = requests.get(BK_API + '/tradingview/history?symbol=' + SET_COIN.upper() + '_THB&resolution=' + SET_TIMEFRAME + '&from=' + str(ex_timestamp-SET_DATA_FROM) + '&to=' + str(ex_timestamp))
chart_data = chart_data.json() #รับข้อมูล chart ให้เป็น json
# ข้อมูลที่ได้มาจะมี s=status, o=open, h=high, l=low, c=close, v=volume, t=timestamp
candles = pandas.DataFrame(chart_data) #จากนั้นเอาข้อมูลมาเก็บไว้ในรูปแบบ pandas DataFrame เพื่อจะได้เรียกใช้สะดวก


### เข้าสู่กระบวนการจับมาวิเคราะห์ด้วย indicator ###

# CDC Action Zone V.2 จะมี EMA ทั้งหมดอยู่ 3 เส้น เส้นแรกสร้างจาก ohlc4 เส้นสองกับเส้นสามสร้างจากเส้นแรก
ohlc4 = pandas_ta.ohlc4(candles['o'], candles['h'], candles['l'], candles['c']) #สร้าง ohlc4
ema1 = pandas_ta.ema(ohlc4, 2) # length 2 (AP)
ema2 = pandas_ta.ema(ema1, 12) # length 12 (Fast)
ema3 = pandas_ta.ema(ema1, 26) # length 26 (Slow)

# ทีนี้เราจะนับจำนวนข้อมูลแท่งเทียนของ ema แต่ละเส้น เพื่อที่จะได้เลือกว่าจะใช้แท่งไหน
# โดยเราจะต้องลบออก 1 เพราะ default ของ pandas จะเริ่มนับจาก 0
ema1_len = len(ema1) - 1
ema2_len = len(ema2) - 1
ema3_len = len(ema3) - 1
# หลังจากนี้เวลาจะเรียกใช้เราสามารถเรียกใช้ได้ง่ายๆ
# เช่น ema1[ema1_len] หมายถึงข้อมูล ema1 แท่งล่าสุด
# ส่วน ema1[ema1_len-1] หมายถึงข้อมูลแท่งก่อนล่าสุด

# สถานะตลาดแท่งปัจจุบัน
if ema2[ema2_len] > ema3[ema3_len]:
    market_status = 'Bullish'
elif ema2[ema2_len] < ema3[ema3_len]:
    market_status = 'Bearish'
else:
    market_status = None

# สถานะตลาดแท่งก่อนหน้าปัจจุบัน
if ema2[ema2_len-1] > ema3[ema3_len-1]:
    market_status_prev = 'Bullish'
elif ema2[ema2_len-1] < ema3[ema3_len-1]:
    market_status_prev = 'Bearish'
else:
    market_status_prev = None

# สี
if market_status == 'Bullish' and ema1[ema1_len]>ema2[ema2_len]:
    color = 'Green'
elif market_status == 'Bearish' and ema1[ema1_len]<ema2[ema2_len]:
    color = 'Red'
elif market_status == 'Bullish' and ema1[ema1_len]<ema2[ema2_len]:
    color = 'Yellow'
elif market_status == 'Bearish' and ema1[ema1_len]>ema2[ema2_len]:
    color = 'Blue'
else:
    color = 'Unknow'

# สถานะซื้อขาย
if market_status == 'Bullish' and market_status_prev == 'Bearish':
    signal = 'Buy'
elif market_status == 'Bearish' and market_status_prev == 'Bullish':
    signal = 'Sell'
else:
    signal = 'Wait'

# Print
print('Color : ' + color)
print('Signal : ' + signal)
