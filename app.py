import streamlit as st
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(page_title="Weather Dashboard", page_icon="🌤️", layout="wide")

# ---------- Data helpers ----------
@st.cache_data(ttl=900)
def geocode(city):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    r = requests.get(url, params={"name": city, "count": 1, "language": "en", "format": "json"}, timeout=15)
    r.raise_for_status()
    results = r.json().get("results", [])
    return results[0] if results else None


@st.cache_data(ttl=900)
def get_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "forecast_days": 7, "timezone": "auto"
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def weather_info(code, is_day=True):
    if code == 0: return ("Clear sky", "☀️" if is_day else "🌙")
    if code in (1, 2): return ("Mainly clear" if code == 1 else "Partly cloudy", "🌤️")
    if code == 3: return ("Overcast", "☁️")
    if code in (45, 48): return ("Fog", "🌫️")
    if code in (51, 53, 55, 56, 57): return ("Drizzle", "🌦️")
    if code in (61, 63, 65, 66, 67): return ("Rain", "🌧️")
    if code in (71, 73, 75, 77): return ("Snow", "❄️")
    if code in (80, 81, 82): return ("Rain showers", "🌦️")
    if code in (85, 86): return ("Snow showers", "🌨️")
    if code in (95, 96, 99): return ("Thunderstorm", "⛈️")
    return ("Weather", "🌤️")


def icon_html(emoji):
    return f'<div class="weather-icon">{emoji}</div>'

# ---------- Styling ----------
st.markdown("""\n<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: Inter, sans-serif; }
.stApp { background:#f6f8fc; color:#1c2b45; }
[data-testid="stSidebar"] { background:#fff; border-right:1px solid #e6ebf5; }
[data-testid="stSidebar"] > div { padding-top:1.3rem; }
.block-container { padding-top:1.2rem; padding-bottom:2rem; max-width:1500px; }
header[data-testid="stHeader"] { background:transparent; }
section[data-testid="stMain"] { background:#f6f8fc; }
.menu-label { color:#91a0bd; font-size:11px; letter-spacing:1.3px; font-weight:700; padding:12px 16px; }
.nav-item { padding:14px 16px; border-radius:15px; color:#7788a8; font-size:14px; margin:3px 0; }
.nav-active { background:#edf1ff; color:#536fff; font-weight:700; }
.brand-note { background:linear-gradient(145deg,#eef2ff,#e8edff); padding:22px; border-radius:20px; margin-top:40px; color:#7d8fb2; font-size:13px; line-height:1.6; }
.brand-note strong { color:#3c5798; }
.top-title { font-size:30px; font-weight:800; letter-spacing:-1px; color:#1d2c46; margin-bottom:0; }
.subtitle { color:#8192b1; font-size:14px; margin-top:3px; }
.date-pill { background:#fff; border:1px solid #e8edf6; border-radius:14px; padding:9px 14px; color:#8494b5; font-size:12px; text-align:center; }
.search-wrap { background:white; border:1px solid #e7ecf5; border-radius:18px; padding:8px 12px; box-shadow:0 6px 20px rgba(30,65,120,.025); }
.hero { background:linear-gradient(112deg,#5678f6,#8ca8ff); border-radius:25px; color:white; padding:34px 36px 0; box-shadow:0 22px 44px rgba(73,105,210,.14); overflow:hidden; position:relative; min-height:285px; }
.hero:after { content:""; position:absolute; right:8%; top:-130px; width:370px; height:370px; border-radius:50%; border:1px solid rgba(255,255,255,.12); box-shadow:0 0 0 36px rgba(255,255,255,.025), 0 0 0 74px rgba(255,255,255,.025); }
.hero-location { font-size:14px; font-weight:600; }
.hero-label { font-size:11px; letter-spacing:1px; font-weight:700; opacity:.8; }
.hero-condition { margin-top:28px; font-size:16px; }
.hero-temp { font-size:76px; font-weight:800; line-height:1; letter-spacing:-4px; }
.hero-temp span { font-size:30px; vertical-align:top; letter-spacing:-1px; }
.hero-feels { margin-top:14px; font-size:13px; opacity:.9; }
.hero-sun { position:absolute; right:12%; top:54px; font-size:112px; z-index:1; filter:drop-shadow(0 10px 8px rgba(226,135,41,.15)); }
.hero-footer { border-top:1px solid rgba(255,255,255,.2); margin:35px -36px 0; padding:16px 36px; font-size:12px; opacity:.9; display:flex; justify-content:space-between; }
.section-title { font-size:20px; font-weight:700; color:#1c2b45; margin:0; }
.section-sub { color:#8292b2; font-size:13px; margin-top:7px; }
.metric-card { background:white; border:1px solid #e7edf6; border-radius:19px; padding:22px 20px; min-height:174px; box-shadow:0 7px 20px rgba(30,65,120,.025); }
.metric-title { color:#7e8fb1; font-size:13px; }
.metric-value { color:#1c2b45; font-size:31px; font-weight:800; margin-top:20px; letter-spacing:-1px; }
.metric-unit { font-size:13px; font-weight:500; letter-spacing:0; color:#7587a7; }
.metric-desc { color:#8b9ab7; font-size:12px; margin-top:7px; }
.metric-foot { color:#9aa8c2; font-size:11px; margin-top:16px; }
.forecast-card { background:white; border:1px solid #e7edf6; border-radius:17px; min-height:230px; padding:18px 8px; text-align:center; }
.forecast-day { font-weight:700; color:#6f809f; font-size:13px; }
.forecast-date { color:#91a0bd; font-size:12px; margin-top:5px; }
.forecast-icon { font-size:34px; margin:24px 0 20px; }
.forecast-condition { color:#8192b1; font-size:12px; min-height:18px; }
.forecast-temps { color:#20314d; font-weight:700; margin-top:24px; font-size:14px; }
.forecast-rain { color:#657cff; font-size:11px; margin-top:13px; }
.history-card { background:white; border:1px solid #e7edf6; border-radius:19px; padding:10px 20px; }
.history-row { border-bottom:1px solid #edf1f7; display:grid; grid-template-columns:1.25fr 1.25fr .85fr 1fr; gap:10px; padding:16px 0; font-size:13px; color:#7183a4; }
.history-row:last-child { border-bottom:0; }
.history-head { font-size:10px; color:#91a0bd; letter-spacing:1px; font-weight:700; }
.history-row strong { color:#20314d; }
div[data-testid="stButton"] button { border-radius:12px; background:#5576f4; border:0; color:white; font-weight:700; height:44px; }
div[data-testid="stButton"] button:hover { background:#4969e9; color:white; }
@media(max-width:850px){ .hero-sun{right:4%;font-size:78px;top:70px}.hero-temp{font-size:62px}.hero{padding:25px 22px 0}.hero-footer{margin-left:-22px;margin-right:-22px;padding:14px 22px}.history-row{grid-template-columns:1fr 1fr;}}
</style>
""", unsafe_allow_html=True)


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown('<div class="menu-label">MENU</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-item nav-active">▦ &nbsp;&nbsp; Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-item">◷ &nbsp;&nbsp; 7-day forecast</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-item">↻ &nbsp;&nbsp; Search history</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-note">🌦️<br><br><strong>Weather, made simple.</strong><br>Plan your day with a little more confidence.<br><br><small>Data by Open-Meteo</small></div>', unsafe_allow_html=True)

# ---------- Header/search ----------
if "history" not in st.session_state:
    st.session_state.history = []
if "city" not in st.session_state:
    st.session_state.city = "Delhi"

header_cols = st.columns([5, 1.15])
with header_cols[0]:
    st.markdown('<div class="top-title">Good day, weather explorer ✨</div><div class="subtitle">Here’s what’s happening outside.</div>', unsafe_allow_html=True)
with header_cols[1]:
    st.markdown(f'<div class="date-pill">◷ &nbsp; {datetime.now().strftime("%a, %B %d, %Y")}</div>', unsafe_allow_html=True)

search_cols = st.columns([6, 1])
with search_cols[0]:
    city_input = st.text_input("Search location", value=st.session_state.city, label_visibility="collapsed", placeholder="Search city or town…")
with search_cols[1]:
    submitted = st.button("Search  →", use_container_width=True)
if submitted and city_input.strip():
    st.session_state.city = city_input.strip()
    st.cache_data.clear()

try:
    place = geocode(st.session_state.city)
    if not place:
        st.error("Couldn't find that location. Try another city or place name.")
        st.stop()
    weather = get_weather(place["latitude"], place["longitude"])
except Exception as e:
    st.error("Weather data couldn't be loaded right now. Please try again in a moment.")
    st.stop()

current = weather["current"]
daily = weather["daily"]
current_condition, current_icon = weather_info(current["weather_code"], bool(current.get("is_day", 1)))
city_name = place.get("name", st.session_state.city)
region = place.get("admin1", "")
country = place.get("country", "")
location_text = ", ".join([x for x in [city_name, region, country] if x])

if not st.session_state.history or st.session_state.history[0][0] != city_name:
    st.session_state.history.insert(0, (city_name, current_condition, round(current["temperature_2m"]), datetime.now().strftime("%b %d, %I:%M %p")))
    st.session_state.history = st.session_state.history[:5]

# ---------- Current conditions ----------
st.markdown(f'''<div class="hero"><div class="hero-location">• &nbsp; {location_text} &nbsp; <span style="color:#72f0b0">●</span> <span class="hero-label">LIVE FORECAST</span></div><div class="hero-condition">{current_condition}</div><div class="hero-temp">{round(current["temperature_2m"])}<span>°{weather.get("current_units",{}).get("temperature_2m","°C").replace("°","")}</span></div><div class="hero-feels">Feels like {round(current["apparent_temperature"])}°C · {weather.get("timezone","Local time")}</div><div class="hero-sun">{current_icon}</div><div class="hero-footer"><span>✳ &nbsp;Stay prepared for the day</span><span>Updated {datetime.now().strftime("%I:%M %p")}</span></div></div>''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-title">Today’s highlights</div><div class="section-sub">A quick look at the conditions</div>', unsafe_allow_html=True)
metrics = [
    ("Humidity", f'{current["relative_humidity_2m"]}<span class="metric-unit">%</span>', "Relative humidity", "◌", "#f2eaff", "#9b73ff"),
    ("Wind speed", f'{current["wind_speed_10m"]}<span class="metric-unit"> km/h</span>', "Near-surface wind", "↗", "#eaf0ff", "#5578ff"),
    ("Precipitation", f'{current["precipitation"]}<span class="metric-unit"> mm</span>', "Current precipitation", "☂", "#e3f8f5", "#26b5a9"),
    ("Feels like", f'{round(current["apparent_temperature"])}<span class="metric-unit">°C</span>', "Apparent temperature", "♨", "#fff0e1", "#ff9b3d"),
]
metric_cols = st.columns(4, gap="medium")
for col, (title, value, desc, symbol, bg, color) in zip(metric_cols, metrics):
    with col:
        st.markdown(f'<div class="metric-card"><div style="display:flex;justify-content:space-between"><div class="metric-title">{title}</div><div style="background:{bg};color:{color};width:34px;height:34px;border-radius:11px;text-align:center;padding-top:6px;font-size:16px">{symbol}</div></div><div class="metric-value">{value}</div><div class="metric-desc">{desc}</div><div class="metric-foot">{("Measured at 10 metres" if title=="Wind speed" else "Rainfall at this time" if title=="Precipitation" else "How it may feel outdoors" if title=="Feels like" else "")}</div></div>', unsafe_allow_html=True)

# ---------- Forecast ----------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-title">7-day forecast</div><div class="section-sub">Look ahead and plan your week</div>', unsafe_allow_html=True)
forecast_cols = st.columns(7, gap="small")
for i, col in enumerate(forecast_cols):
    with col:
        date_obj = datetime.fromisoformat(daily["time"][i])
        label = "Today" if i == 0 else date_obj.strftime("%a")
        cond, ico = weather_info(daily["weather_code"][i])
        high = round(daily["temperature_2m_max"][i])
        low = round(daily["temperature_2m_min"][i])
        rain = daily.get("precipitation_probability_max", [0]*7)[i]
        st.markdown(f'<div class="forecast-card"><div class="forecast-day">{label}</div><div class="forecast-date">{date_obj.strftime("%a, %b %d")}</div><div class="forecast-icon">{ico}</div><div class="forecast-condition">{cond}</div><div class="forecast-temps">{high}° &nbsp; <span style="color:#8da0bf;font-weight:500">{low}°</span></div><div class="forecast-rain">↟ {rain}% rain</div></div>', unsafe_allow_html=True)

# ---------- History ----------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-title">Recent searches</div><div class="section-sub">Your latest weather lookups, saved locally</div>', unsafe_allow_html=True)
if st.button("Refresh ↻", key="refresh_history"):
    st.cache_data.clear()
    st.rerun()
rows = ['<div class="history-card"><div class="history-row history-head"><span>LOCATION</span><span>CONDITION</span><span>TEMPERATURE</span><span>SEARCHED AT</span></div>']
for name, condition, temp, timestamp in st.session_state.history:
    rows.append(f'<div class="history-row"><strong>{name}</strong><span>{condition}</span><strong>{temp}°C</strong><span>{timestamp}</span></div>')
rows.append('</div>')
st.markdown(''.join(rows), unsafe_allow_html=True)
st.markdown('<div style="text-align:center;color:#91a0bd;font-size:12px;margin-top:35px">Weather data by <strong>Open-Meteo</strong> · Built with Streamlit and Python</div>', unsafe_allow_html=True)
