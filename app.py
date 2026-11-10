import streamlit as st
import sqlite3
from google import genai
from google.genai import types
from schema_inspector import get_database_context

# Səhifənin dizayn tənzimləmələri
st.set_page_title_config = st.set_page_config(
    page_title="Sayad Parfum - AI SQL Analitiki",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Sayad Parfum - Text-to-SQL AI Analitiki")
st.markdown("Bu agent verilənlər bazasındakı satışları, məhsulları və mənfəəti təbii dildə sorğulamaq üçün **Google Gemini** və **Agentic RAG** arxitekturası ilə işləyir.")

# 1. SQL İcra funksiyası (Eyni təhlükəsizlik qaydası ilə)
def execute_sql(sql_query: str) -> dict:
    clean_query = sql_query.strip()
    if not (clean_query.upper().startswith("SELECT") or clean_query.upper().startswith("WITH")):
        return {"status": "error", "error_message": "Yalnız SELECT sorğularına icazə verilir!"}

    try:
        conn = sqlite3.connect("file:sayad_parfum.db?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute(clean_query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        conn.close()

        results = [dict(zip(columns, row)) for row in rows]
        return {"status": "success", "row_count": len(results), "data": results[:50]}
    except sqlite3.Error as e:
        return {"status": "error", "error_message": f"SQLite xətası: {str(e)}. Lütfən sorğunu düzəlt."}

# 2. Sistem Promptu
@st.cache_resource
def get_cached_system_prompt():
    schema_context = get_database_context("sayad_parfum.db")
    return f"""Sən "Sayad Parfum" mağazası üçün çalışan peşəkar Mətn-SQL Analitiki agentisən.
Vəzifən istifadəçinin suallarını SQLite sorğularına çevirmək, `execute_sql` ilə icra etmək və nəticəni aydın biznes dilində izah etməkdir.

<database_schema>
{schema_context}
</database_schema>

<business_rules>
1. Yalnız SQLite sintaksisindən istifadə et.
2. Mətn axtarışında həmişə `LOWER(column) LIKE LOWER('%axtarılan%')` işlət.
3. Maliyyə düsturları:
   - Ümumi Satış: `SUM(si.item_total_azn)`
   - Xalis Ödəniş: `sales` və `sale_items` JOIN edilərkən endirimi (`discount_azn`) hər sətir üçün təkrar hesablamamaq üçün CTE (`WITH`) istifadə et.
   - Xalis Mənfəət: `SUM(si.item_total_azn - (si.grams_sold * p.cost_per_gram))`
4. Qeydiyyatsız müştərilər üçün `LEFT JOIN` istifadə et.
</business_rules>
"""

# 3. Gemini Chat Sessiyasının Başladılması
if "chat_session" not in st.session_state:
    client = genai.Client() # API açarı mühit dəyişənindən oxunur
    config = types.GenerateContentConfig(
        system_instruction=get_cached_system_prompt(),
        tools=[execute_sql],
        temperature=0.0
    )
    st.session_state.chat_session = client.chats.create(model="gemini-3.5-flash-lite", config=config)

# 4. Söhbət Tarixçəsi (Chat History)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Salam! Mən Sayad Parfum-un analitik agentiyəm. Mağazanın satışları, stokları və mənfəəti ilə bağlı istənilən sualı verə bilərsiniz."}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. İstifadəçidən Sualın Alınması
if prompt := st.chat_input("Məsələn: Bu ay ən çox hansı ətir satılıb?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Agent verilənlər bazasını analiz edir..."):
            try:
                response = st.session_state.chat_session.send_message(prompt)
                bot_reply = response.text
                st.markdown(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            except Exception as e:
                error_msg = f"Sistem xətası baş verdi: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})