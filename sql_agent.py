import os
import sqlite3
from google import genai
from google.genai import types
from schema_inspector import get_database_context

# 1. TƏHLÜKƏSİZ SQL İCRA ALƏTİ (Tool)
def execute_sql(sql_query: str) -> dict:
    """
    SQLite verilənlər bazasında YALNIZ OXUMAQ (SELECT) sorğularını icra edir
    və nəticəni (və ya xəta mesajını) qaytarır.
    
    Args:
        sql_query: İcra ediləcək SQLite SELECT sorğusu.
    """
    print(f"\n🛠️  [AGENT SQL İCRA EDİR]:\n{sql_query}\n")
    
    clean_query = sql_query.strip()
    
    # Qoruma 1: Yalnız SELECT və WITH sorğularına icazə ver
    if not (clean_query.upper().startswith("SELECT") or clean_query.upper().startswith("WITH")):
        return {
            "status": "error",
            "error_message": "TƏHLÜKƏSİZLİK XƏTASI: Yalnız SELECT və ya WITH sorğularına icazə verilir!"
        }

    try:
        # Qoruma 2: Bazanı Read-Only (mode=ro) rejimində açırıq
        conn = sqlite3.connect("file:sayad_parfum.db?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute(clean_query)
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        conn.close()

        # Nəticəni oxunaqlı lüğət (dict) siyahısına çeviririk
        results = [dict(zip(columns, row)) for row in rows]
        
        print(f"✅ [BAZADAN QAYIDAN NƏTİCƏ]: {len(results)} sətir tapıldı.")
        return {
            "status": "success",
            "row_count": len(results),
            "data": results[:50]  # Konteksti şişirtməmək üçün maksimum 50 sətir
        }

    except sqlite3.Error as e:
        # Özünü-Düzəltmə (Self-Correction) üçün xətanı AI-a qaytarırıq!
        print(f"⚠️  [SQL XƏTASI BAŞ VERDİ]: {e} -> Agent indi özü düzəldəcək...")
        return {
            "status": "error",
            "error_message": f"SQLite xətası: {str(e)}. Sxemi yoxla və sorğunu düzəldib yenidən çağır."
        }


# 2. SİSTEM PROMPTU YARADICISI
def build_system_prompt() -> str:
    schema_context = get_database_context("sayad_parfum.db")
    return f"""Sən "Sayad Parfum" mağazası üçün çalışan peşəkar Mətn-SQL Analitiki (Text-to-SQL Analyst) agentisən.
Vəzifən istifadəçinin Azərbaycan dilində verdiyi biznes suallarını dəqiq SQLite sorğularına çevirmək, `execute_sql` aləti ilə icra etmək və nəticəni aydın biznes dilində izah etməkdir.

<database_schema>
{schema_context}
</database_schema>

<business_rules>
1. SQL Dialekti: Yalnız keçərli SQLite sintaksisindən istifadə et.
2. Mətn axtarışı: Ətir və ya müştəri adlarını axtararkən həmişə `LOWER(column) LIKE LOWER('%axtarılan%')` istifadə et.
3. Maliyyə düsturları:
   - Məhsul üzrə Ümumi Satış (Gross Revenue): `SUM(si.item_total_azn)`
   - Qəbz üzrə Xalis Ödəniş (Net Revenue): Qəbzin `sale_items` cəmindən `sales.discount_azn` çıxılmalıdır. (DİQQƏT: `sales` və `sale_items` JOIN edilərkən `discount_azn` hər sətir üçün təkrarlana bilər! Ona görə ümumi xalis gəliri tapanda əvvəlcə hər `sale_id` üzrə cəmi alt-sorğuda (CTE) hesabla, sonra `discount_azn`-i çıx).
   - Məhsulun Maya Dəyəri (COGS): `si.grams_sold * p.cost_per_gram`
   - Məhsul üzrə Xalis Mənfəət (Gross Profit): `SUM(si.item_total_azn - (si.grams_sold * p.cost_per_gram))`
4. Qeydiyyatsız müştərilər: `sales.customer_id` NULL ola bilər. Müştəri cədvəli ilə birləşdirərkən satışları itirməmək üçün `LEFT JOIN` istifadə et.
</business_rules>

<execution_rules>
- Heç vaxt rəqəmləri təxmin etmə, mütləq `execute_sql` alətini çağır.
- Əgər `execute_sql` xəta (`status: error`) qaytararsa, xəta mesajını oxu, SQL sorğusunu düzəlt və aləti yenidən çağır.
- Cavab verərkən əvvəlcə qısa və aydın biznes cavabını yaz, rəqəmləri AZN və qram ilə göstər.
</execution_rules>
"""


# 3. AGENTİN ƏSAS İŞLƏMƏ DÖVRÜ
def run_agent():
    # Əgər GEMINI_API_KEY mühit dəyişənində yoxdursa, bura birbaşa da yaza bilərsən:
    # client = genai.Client(api_key="SƏNİN_API_AÇARIN")
    client = genai.Client()

    system_prompt = build_system_prompt()

    # Gemini konfiqurasiyası: Python funksiyamızı `tools` siyahısına veririk.
    # SDK avtomatik olaraq funksiyanı çağıracaq və lazım gəlsə bir neçə dəfə dövr edəcək!
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=[execute_sql],
        temperature=0.0  # Analitik dəqiqlik üçün temperaturu 0 edirik (yaradıcılıq yox, dəqiqlik!)
    )

    # Çat sessiyası başladırıq ki, əvvəlki sualları da xatırlasın (Multi-turn conversation)
    chat = client.chats.create(model="gemini-3.5-flash-lite", config=config)

    print("=====================================================")
    print("🤖 Sayad Parfum - Text-to-SQL Analitik Agenti Hazırdır!")
    print("Çıxmaq üçün 'exit' və ya 'cixis' yazın.")
    print("=====================================================\n")

    while True:
        user_question = input("\n📊 Sualınız: ").strip()
        if user_question.lower() in ["exit", "quit", "cixis", "çıxış"]:
            print("Agent dayandırıldı. Uğurlar!")
            break
        if not user_question:
            continue

        try:
            response = chat.send_message(user_question)
            print(f"\n💡 Agentin Cavabı:\n{response.text}")
            print("-" * 50)
        except Exception as e:
            print(f"\n❌ Sistem xətası: {e}")

if __name__ == "__main__":
    run_agent()