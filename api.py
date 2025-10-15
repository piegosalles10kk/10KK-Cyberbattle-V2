from flask import Flask, request, Response, jsonify
import json
import logging
from queue import Queue
from threading import Thread
from datetime import datetime
from orchestrator import CyberDuelOrchestrator
from attack_database import AttackDatabase

app = Flask(__name__)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class LogStreamer:
    """Classe para gerenciar streaming de logs em tempo real"""
    def __init__(self):
        self.log_queue = Queue()
        self.finished = False
    
    def emit_log(self, level, message, data=None):
        """Emite um log estruturado para a fila"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "data": data or {}
        }
        self.log_queue.put(log_entry)
    
    def finish(self):
        """Marca o streaming como finalizado"""
        self.finished = True
        self.log_queue.put(None)  # Sentinel value


def validate_payload(payload):
    """Valida o payload da requisição"""
    required_fields = ['test_id', 'test_name', 'cloud_provider', 'os_template']
    
    for field in required_fields:
        if field not in payload:
            return False, f"Campo obrigatório ausente: {field}"
    
    if 'vm_config' not in payload:
        return False, "Campo 'vm_config' é obrigatório"
    
    vm_required = ['vm_cpu', 'vm_ram_mb', 'vm_switch_name', 'base_vhdx_path', 'admin_user', 'admin_password']
    for field in vm_required:
        if field not in payload['vm_config']:
            return False, f"Campo obrigatório ausente em vm_config: {field}"
    
    return True, None


def run_cyberduel_test(payload, streamer):
    """Executa o teste CyberDuel em uma thread separada"""
    try:
        streamer.emit_log("INFO", "🚀 Iniciando CyberDuel Test", {
            "test_id": payload["test_id"],
            "test_name": payload["test_name"]
        })
        
        # Inicializar o orquestrador
        orchestrator = CyberDuelOrchestrator(payload, streamer)
        
        # Executar o teste completo
        results = orchestrator.execute_full_test()
        
        streamer.emit_log("SUCCESS", "✅ Teste concluído com sucesso", results)
        
    except Exception as e:
        streamer.emit_log("ERROR", f"❌ Erro fatal durante execução: {str(e)}", {
            "error_type": type(e).__name__,
            "error_details": str(e)
        })
    finally:
        streamer.finish()


@app.route('/api/v1/cyberduel/execute', methods=['POST'])
def execute_cyberduel_test():
    """
    Endpoint principal para executar testes CyberDuel com streaming de logs.
    
    Retorna logs em tempo real usando Server-Sent Events (SSE).
    """
    try:
        payload = request.get_json()
        
        # Validar payload
        is_valid, error_message = validate_payload(payload)
        if not is_valid:
            return jsonify({
                "status": "error",
                "message": error_message
            }), 400
        
        # Criar streamer de logs
        streamer = LogStreamer()
        
        # Iniciar execução em thread separada
        test_thread = Thread(
            target=run_cyberduel_test,
            args=(payload, streamer),
            daemon=True
        )
        test_thread.start()
        
        # Função geradora para streaming
        def generate_logs():
            while True:
                log_entry = streamer.log_queue.get()
                
                # Se receber None, terminou
                if log_entry is None:
                    yield f"data: {json.dumps({'status': 'completed'})}\n\n"
                    break
                
                # Enviar log como SSE
                yield f"data: {json.dumps(log_entry)}\n\n"
        
        # Retornar response com streaming
        return Response(
            generate_logs(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/v1/attacks/list', methods=['GET'])
def list_attacks():
    """Lista todos os ataques disponíveis no banco de dados"""
    try:
        db = AttackDatabase()
        attacks = db.get_all_attacks()
        
        return jsonify({
            "status": "success",
            "total": len(attacks),
            "attacks": attacks
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/v1/attacks/<ttp_id>', methods=['GET'])
def get_attack_details(ttp_id):
    """Retorna detalhes de um ataque específico"""
    try:
        db = AttackDatabase()
        attack = db.get_attack(ttp_id)
        
        if attack:
            return jsonify({
                "status": "success",
                "attack": attack
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": f"Ataque {ttp_id} não encontrado"
            }), 404
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "CyberDuel API"
    }), 200


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,  # Em produção, sempre False
        threaded=True
    )