import pyodbc
import subprocess
from enum import IntEnum
from concurrent.futures import ThreadPoolExecutor


class NaturezaEquipamento(IntEnum):
    NULL = 0
    RELOGIO = 1
    CATRACA = 2
    CATRACA_PONTO = 3
    CATRACA_REFEITORIO = 4

    @classmethod
    def is_relogio(cls, valor):
        return valor == cls.RELOGIO
    @classmethod
    def is_catraca(cls, valor):
        return valor in (cls.CATRACA, cls.CATRACA_PONTO, cls.CATRACA_REFEITORIO)

# ---- Configuração ---
config = {
    "EURO":{
        "CONTROLADORA": "FORPONTO.CONTROLADORA",
        "EQUIPAMENTO": "FORPONTO.EQUIPAMENTO",
    }
}

def busca_todos_equipamentos():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=LAPTOP-5112UO3P\\SQLEXPRESS;"
        "DATABASE=EURO;"
        "UID=FORPONTO;"
        "PWD=FORPONTO;"
        "Trusted_Connection=yes"
    )

    lista_final = []
    relogios = []
    catracas = []
    outros = []

    with pyodbc.connect(conn_str) as conexao:
        cursor = conexao.cursor()

        for tabela in config:
            try:
                query = '''
                    SELECT 
                        COTR_CODIGO,
                        COTR_DESCRICAO,
                        COTR_ENDERECOTCP,
                        EQUI_NATUREZA
                    FROM {CONTROLADORA} C
                    INNER JOIN {EQUIPAMENTO} E
	                    ON C.COTR_ID = E.COTR_ID
                '''.format(**config[tabela])

                cursor.execute(query)
                rows = cursor.fetchall()

                for row in rows:
                    lista_final.append(
                        {
                            "CODIGO": row.COTR_CODIGO,
                            "DESCRICAO": row.COTR_DESCRICAO,
                            "IP": row.COTR_ENDERECOTCP,
                            "NATUREZA": int(row.EQUI_NATUREZA)
                        }
                    )

                    if NaturezaEquipamento.is_relogio(row.EQUI_NATUREZA):
                        relogios.append(row.COTR_CODIGO)

                    elif NaturezaEquipamento.is_catraca(row.EQUI_NATUREZA):
                        catracas.append(row.COTR_CODIGO)

                    else:
                        outros.append(row.COTR_CODIGO)

            except Exception as e:
                print(f"Erro na tabela {tabela}: {e}")

    return lista_final, relogios, catracas, outros

def ping_ip(ip):
    resultado = subprocess.run(
        ["ping", "-n", "1", "-w", ip],
        capture_output=True,
        text=True,
        )
    return resultado.returncode == 0

def verifica_equipamentos(lista_final):

    for eq in lista_final:
        ip = eq["IP"]

        if not ip:
            print(f"{eq['DESCRICAO']} - sem IP cadastrado")
            continue
        if ping_ip(ip):
            print(f"{eq['DESCRICAO']}({ip}) - online")
        else:
            print(f"{eq['DESCRICAO']} ({ip}) - offline")



if __name__ == "__main__":
    lista, relogios, catracas, outros = busca_todos_equipamentos()

    print(f"Total equipamentos: {len(lista)}")
    print(f"Relógios:  {len(relogios)}")
    print(f"Catracas:  {len(catracas)}")
    print(f"Outros:    {len(outros)}")

    print("\n--- LISTA COMPLETA ---")
    for eq in lista:
        print(eq)

    print("\n--- VERIFICANDO PING ---")
    verifica_equipamentos(lista)