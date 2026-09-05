"""
scripts/run_inventory_worker.py
Script CLI para execução do Worker Autônomo de Auditoria de Estoque.
Pode ser agendado via Cron (ex: toda segunda-feira às 07:00) ou executado sob demanda.
"""

import sys
import argparse
import logging
from dotenv import load_dotenv

load_dotenv()

from src.agent.worker import run_autonomous_inventory_audit

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


def main():
    parser = argparse.ArgumentParser(description="Executar Worker Autônomo de Auditoria de Estoque (Vértice Retail)")
    parser.add_argument("--send-email", action="store_true", default=True, help="Disparar e-mail executivo via Resend (default: True)")
    parser.add_argument("--no-email", action="store_false", dest="send_email", help="Não disparar e-mail, apenas executar auditoria e salvar snapshot")
    parser.add_argument("--to-email", type=str, default=None, help="E-mail de destino customizado")

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("VÉRTICE RETAIL & ELOGROUP AI LAB — WORKER AUTÔNOMO DE ESTOQUE")
    print("=" * 70)

    try:
        result = run_autonomous_inventory_audit(
            send_email=args.send_email,
            to_email=args.to_email
        )
        print("\nAuditoria concluída com sucesso!")
        print(f"⏱Timestamp: {result['timestamp']}")
        print(f"Deep Link Gerado: {result['deep_link_url']}")
        
        email_res = result.get("email_result")
        if email_res:
            print(f"Status do E-mail (Resend): {email_res.get('status')} | Destino: {email_res.get('to')}")
            if email_res.get("id"):
                print(f"ID da Mensagem Resend: {email_res.get('id')}")

        print(f"Snapshot persistido em: {result['snapshot_path']}")
        print("=" * 70 + "\n")
        return 0
    except Exception as e:
        print(f"\n❌ Erro durante execução do worker: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
