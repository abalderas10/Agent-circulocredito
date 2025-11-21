#!/usr/bin/env python3
"""
Agente IA para Evaluación Crediticia - Círculo de Crédito
Plataforma automática de otorgamiento de créditos
"""

import json
import sys
import logging
from credit_agent import CreditEvaluationAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """Función principal del agente"""
    try:
        # Leer datos de entrada desde stdin o archivo
        if len(sys.argv) > 1:
            # Leer desde archivo
            with open(sys.argv[1], 'r', encoding='utf-8') as f:
                solicitud = json.load(f)
        else:
            # Leer desde stdin
            input_data = sys.stdin.read()
            solicitud = json.loads(input_data)

        logging.info("Solicitud recibida: %s", solicitud.get('nombre', 'Desconocido'))

        # Inicializar agente
        agent = CreditEvaluationAgent()

        # Procesar evaluación
        resultado = agent.evaluate_credit_request(solicitud)

        # Imprimir resultado como JSON
        print(json.dumps(resultado, indent=2, ensure_ascii=False))

    except json.JSONDecodeError as e:
        logging.error("Error al parsear JSON de entrada: %s", e)
        print(json.dumps({"error": "JSON inválido", "detalle": str(e)}))
        sys.exit(1)
    except KeyError as e:
        logging.error("Campo requerido faltante: %s", e)
        print(json.dumps({"error": "Campo requerido faltante", "campo": str(e)}))
        sys.exit(1)
    except Exception as e:
        logging.error("Error inesperado: %s", e)
        print(json.dumps({"error": "Error interno", "detalle": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()