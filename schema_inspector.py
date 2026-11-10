import sqlite3

def get_database_context(db_path="sayad_parfum.db") -> str:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Bütün cədvəllərin siyahısını və DDL-ni (CREATE TABLE kodunu) alırıq
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = cursor.fetchall()

    context_parts = []
    for table_name, ddl in tables:
        context_parts.append(f"### Cədvəl: {table_name}\n```sql\n{ddl}\n```")
        
        # Hər cədvəldən ilk 3 sətri nümunə kimi götürürük ki, AI formatı görsün
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
        rows = cursor.fetchall()
        col_names = [description[0] for description in cursor.description]
        
        context_parts.append(f"Nümunə sətirlər ({', '.join(col_names)}):")
        for row in rows:
            context_parts.append(f"  {row}")
        context_parts.append("")

    conn.close()
    return "\n".join(context_parts)

if __name__ == "__main__":
    print(get_database_context())