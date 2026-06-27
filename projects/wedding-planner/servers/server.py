#server.py
import sqlite3
import datetime

class SQL_Request_DB:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def log_action(self, action: str, sql: str, status: str)-> None:
        with open("audit_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now()}] {action} | {status} | {sql}\n")
    
    def read_param(self, sql: str, params: tuple = ()) -> dict:
        sql_stripped = sql.strip().lower()
        if not sql_stripped.startswith("select"):
            return {"ok": False, "error": "Erreur : Seules les requêtes SELECT sont autorisées pour la lecture."}

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                results = cursor.fetchall()

                self.log_action("FETCHING", f"{sql} param:{params}", "ACCEPT")
                return {"ok": True, "data": results}

        except Exception as e:
            return {"ok": False, "error": f"Erreur SQL {str(e)}"}
    
    def write_param(self, sql: str, params: tuple = ()) -> dict:
        conn = None
        try:
            sql_stripped = sql.strip().lower()
            if not (sql_stripped.startswith("insert") or sql_stripped.startswith("update")):
                self.log_action("WRITE_BLOCKED", sql, "REFUSED") 
                return {"ok": False, "error": "Erreur : Seules les requêtes INSERT et UPDATE sont autorisées pour l'écriture."}
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            conn.execute("BEGIN IMMEDIATE")  # ou "BEGIN"
            cursor.execute(sql, params)
            conn.commit()

            msg = f"Succès : {cursor.rowcount} ligne(s) modifiée(s)."
            self.log_action("WRITE_OK", sql, msg)
            return {"ok": True, "data": msg}
            
        except Exception as e:
            if conn: conn.rollback()
            self.log_action("WRITE_ERROR", sql, str(e))
            return {"ok": False, "error": f"Erreur SQL (rollback) {str(e)}"}
        
        finally:
            if conn:
                conn.close()
    
    def transaction(self, operations: list) -> dict:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # transaction explicite plus safe
            conn.execute("BEGIN IMMEDIATE")

            for op in operations:
                if not isinstance(op, tuple) or len(op) != 2:
                    raise ValueError("Chaque opération doit être (sql, params)")

                sql, params = op

                sql_stripped = sql.strip().lower()
                if not (sql_stripped.startswith("insert") or sql_stripped.startswith("update")):
                    raise ValueError(f"SQL non autorisé dans transaction: {sql}")

                if params is None:
                    params = ()

                cursor.execute(sql, params)

            conn.commit()
            msg = f"Succès : {cursor.rowcount} ligne(s) modifiée(s)."
            self.log_action("TRANSACTION_OK", sql, msg)
            return {"ok": True, "data": "Transaction réussie"}

        except Exception as e:
            if conn:
                conn.rollback()
            
            self.log_action("TRANSACTION_ERROR", sql, str(e))
            return {"ok": False, "error": str(e)}

        finally:
            if conn:
                conn.close()

# Initialisation de la BDD
DB_PATH = r"D:\marchine_learning\Agent_course\agentic-labs\projects\wedding-planner\database\wedding_planner.db"
db = SQL_Request_DB(DB_PATH)