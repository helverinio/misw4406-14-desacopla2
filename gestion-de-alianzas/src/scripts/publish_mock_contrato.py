import pulsar
import json
from datetime import date, datetime
import uuid
from src.domain.models.contrato import Contrato, TipoContrato, EstadoContrato

PULSAR_SERVICE_URL = 'pulsar://localhost:6650'
TOPIC = 'gestion-de-integraciones'

def create_mock_contrato():
    tipos = list(TipoContrato)
    estados = list(EstadoContrato)
    monedas = ["USD", "EUR", "COP", "MXN"]
    condiciones_list = ["Condición A", "Condición B", "Condición C", "Condición D"]
    return Contrato(
        partner_id=str(uuid.uuid4()),
        tipo=tipos[0],
        fecha_inicio=date.today(),
        fecha_fin=None,
        monto=500.0,
        moneda=monedas[0],
        condiciones=condiciones_list[0],
        estado=estados[0],
        fecha_creacion=datetime.utcnow(),
        fecha_actualizacion=None
    )

def main():
    client = pulsar.Client(PULSAR_SERVICE_URL)
    producer = client.create_producer(TOPIC)
    contrato = create_mock_contrato()
    data_json = contrato.model_dump_json() if hasattr(contrato, 'model_dump_json') else json.dumps(contrato.dict(), default=str)
    producer.send(data_json.encode('utf-8'))
    print(f"Published mock contrato: {data_json}")
    client.close()

if __name__ == "__main__":
    main()
