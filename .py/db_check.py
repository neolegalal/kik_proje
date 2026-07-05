import sqlite3, os

print("Calisilan klasor:", os.getcwd())
print("kik.db var mi:", os.path.exists("kik.db"))
if os.path.exists("kik.db"):
    print("kik.db boyutu:", os.path.getsize("kik.db"), "byte")

c = sqlite3.connect("kik.db")
tablolar = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Tablolar:", tablolar)

if tablolar:
    for t in tablolar:
        sayi = c.execute(f"SELECT COUNT(*) FROM {t[0]}").fetchone()[0]
        print(f"  {t[0]}: {sayi} kayit")
c.close()
