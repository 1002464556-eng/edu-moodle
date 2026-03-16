import streamlit as st
import pandas as pd
import plotly.express as px

# הגדרת תצורת העמוד
st.set_page_config(page_title="דשבורד מפקחים - מדעים ומתמטיקה", layout="wide", page_icon="📊")

# פונקציה לטעינת הנתונים
@st.cache_data
def load_data():
    df1 = pd.read_csv('מתמטיקה+מדעים _ מחוז ועיר 16.03.csv')
    df2 = pd.read_csv('ללא קורסים.csv')
    return df1, df2

df1, df2 = load_data()

# סרגל צד לבחירת מחוז תקשוב (הפרדה מוחלטת)
district = st.sidebar.selectbox("בחר/י מחוז תקשוב:", ['ירושלים', 'העיר ירושלים'])

# סינון הקבצים לפי המחוז הנבחר
df1_dist = df1[df1['מחוז תקשוב'] == district]
df2_dist = df2[df2['מחוז תקשוב'] == district]

st.title(f"📊 דשבורד מצב משימות - מחוז {district}")

# ==========================================
# חלק א': שקף מאקרו - מחוזי
# ==========================================
st.header("מבט על - מחוזי")
col1, col2 = st.columns(2)

def calc_macro(df, domain):
    d = df[df['תחום'] == domain]
    if d.empty or d['מספר תלמידים בשכבה'].sum() == 0:
        return 0, 0
    # מדד 1: אחוז תלמידים פעילים
    pct_active = (d['תלמידים שביצעו משימה אחת לפחות'].sum() / d['מספר תלמידים בשכבה'].sum()) * 100
    # מדד 2: ממוצע משימות
    avg_tasks = d['ממוצע משימות לתלמיד- כלל שכבתי'].mean()
    return pct_active, avg_tasks

math_pct, math_avg = calc_macro(df1_dist, 'מתמטיקה')
sci_pct, sci_avg = calc_macro(df1_dist, 'מדעים')

with col1:
    st.subheader("📐 מתמטיקה")
    st.metric("אחוז תלמידים פעילים", f"{math_pct:.1f}%")
    st.metric("ממוצע משימות לשכבה", f"{math_avg:.1f}")

with col2:
    st.subheader("🔬 מדעים")
    st.metric("אחוז תלמידים פעילים", f"{sci_pct:.1f}%")
    st.metric("ממוצע משימות לשכבה", f"{sci_avg:.1f}")

st.divider()

# ==========================================
# חלק ב': שקף מיקרו - לכל מפקח
# ==========================================
st.header("👤 פילוח לפי מפקח")
# רשימת המפקחים במחוז
supervisors = df1_dist['שם מפקח'].dropna().unique()
supervisor = st.selectbox("בחר/י מפקח:", supervisors)

df1_sup = df1_dist[df1_dist['שם מפקח'] == supervisor]

# הצגת יעדים
st.info("🎯 **יעדים לסוף חודש מרץ:** 17 משימות במתמטיקה | 8 משימות במדעים")

math_sup_pct, math_sup_avg = calc_macro(df1_sup, 'מתמטיקה')
sci_sup_pct, sci_sup_avg = calc_macro(df1_sup, 'מדעים')

# יצירת גרף עמודות
chart_data = pd.DataFrame({
    'מדד': ['אחוז תלמידים פעילים', 'ממוצע משימות לשכבה', 'אחוז תלמידים פעילים ', 'ממוצע משימות לשכבה '],
    'ערך': [math_sup_pct, math_sup_avg, sci_sup_pct, sci_sup_avg],
    'תחום': ['מתמטיקה', 'מתמטיקה', 'מדעים', 'מדעים']
})

fig = px.bar(chart_data, x='מדד', y='ערך', color='תחום', text_auto='.1f', 
             title=f"מדדי ביצוע - בתי הספר באחריות: {supervisor}", barmode='group')
st.plotly_chart(fig, use_container_width=True)

# --- Drill Down (פירוט בתי ספר וצביעה מותנית) ---
st.markdown("### 📋 פירוט בתי ספר (Drill-Down)")
st.caption("לחץ על הלשוניות כדי לראות את בתי הספר שמהם נגזרו העמודות בגרף.")

tab1, tab2 = st.tabs(["📐 בתי ספר - מתמטיקה", "🔬 בתי ספר - מדעים"])

# פונקציות לצביעה מותנית של עמודה M
def color_math(val):
    if pd.isna(val): return ''
    if val < 5: return 'background-color: #ffcccc; color: black;' # אדום
    elif 5 <= val <= 15: return 'background-color: #ffffcc; color: black;' # צהוב
    else: return 'background-color: #ccffcc; color: black;' # ירוק

def color_sci(val):
    if pd.isna(val): return ''
    if val < 2: return 'background-color: #ffcccc; color: black;' # אדום
    elif 2 <= val <= 4: return 'background-color: #ffffcc; color: black;' # צהוב
    else: return 'background-color: #ccffcc; color: black;' # ירוק

cols_to_show = ['מוסד', 'רשות', 'מספר תלמידים בשכבה', 'תלמידים שביצעו משימה אחת לפחות', 'ממוצע משימות לתלמיד- כלל שכבתי']

with tab1:
    df_math = df1_sup[df1_sup['תחום'] == 'מתמטיקה'][cols_to_show]
    st.dataframe(df_math.style.map(color_math, subset=['ממוצע משימות לתלמיד- כלל שכבתי']), use_container_width=True, hide_index=True)

with tab2:
    df_sci = df1_sup[df1_sup['תחום'] == 'מדעים'][cols_to_show]
    st.dataframe(df_sci.style.map(color_sci, subset=['ממוצע משימות לתלמיד- כלל שכבתי']), use_container_width=True, hide_index=True)

st.divider()

# ==========================================
# חלק ג': מוסדות ללא פתיחת מרחבים
# ==========================================
st.header("🚨 בתי ספר ללא מרחבים (ללא קורסים)")
# סינון קובץ 2 לפי המפקח
df2_sup = df2_dist[df2_dist['מפקח'] == supervisor] 
math_no_course = df2_sup[df2_sup['תחום'] == 'מתמטיקה']
sci_no_course = df2_sup[df2_sup['תחום'] == 'מדעים']

col_no1, col_no2 = st.columns(2)

with col_no1:
    with st.expander(f"מתמטיקה: לחץ לצפייה ב-{len(math_no_course)} מוסדות שלא פתחו"):
        st.dataframe(math_no_course[['מוסד', 'רשות']], hide_index=True, use_container_width=True)

with col_no2:
    with st.expander(f"מדעים: לחץ לצפייה ב-{len(sci_no_course)} מוסדות שלא פתחו"):
        st.dataframe(sci_no_course[['מוסד', 'רשות']], hide_index=True, use_container_width=True)