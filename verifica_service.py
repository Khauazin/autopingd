import ctypes
import win32serviceutil
import win32service
import time
import sys
import os
import win32evtlog
import win32evtlogutil


aplicacoes = [
    "Foracesso",
    "Forponto",
    "FptoExec",
    "FptoAcess",
    "Online",
    "Portaria",
    "Distribuidor",
    "Executor",
    "Monitor",
    "TaskService",
    "TaskServ",
    "Mensageiro",
]

def nome_monitorado(source):
    for app in aplicacoes:
        if app.lower() in source.lower():
            return True
    return False


def verifica_eventos(log_type="Application"):
    server = None
    hand = win32evtlog.OpenEventLog(server, log_type)
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

    events = win32evtlog.ReadEventLog(hand, flags, 0)
    print(f"📋 Verificando {len(events)} eventos no log {log_type}...")

    for event in events:
        if event.EventType == win32evtlog.EVENTLOG_ERROR_TYPE:
            if nome_monitorado(event.SourceName):
                print(f"Erro encontrado: {event.SourceName}")
    
    win32evtlog.CloseEventLog(hand)


def executar_como_admin():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("Reiniciando como Administrador ...")
        script = os.path.abspath(sys.argv[0])
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

executar_como_admin()

servicos = [
    "wuauserv",
    "Spooler",
    "TaskService",
    "TComManagerService",
]


def verifica_servico(nome):
    try:
        status = win32serviceutil.QueryServiceStatus(nome)

        if status[1] == win32service.SERVICE_RUNNING:
            print(f"Serviço {nome} - Em Execução")
        elif status[1] == win32service.SERVICE_STOPPED:
            print(f"Serviço {nome} - Esta Parado")
            try:
                win32serviceutil.StartService(nome)
                print(f"iServiço {nome} - Iniciado com Sucesso!")
            except Exception as e:
                print(f"Serviço {nome} - Erro não esperado {e}")
        else:
            print(f"Serviço {nome} Status: {status[1]}")
    except Exception as e:
        print(f"Serviço {nome} - Erro não esperado: {e}")

while True:
    verifica_eventos("Application")
    for servico in servicos:
        verifica_servico(servico)
    print("---")
    time.sleep(60)

