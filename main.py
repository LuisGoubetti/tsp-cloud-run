# main.py

import json
from flask import Flask, request, jsonify
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import os

app = Flask(__name__)

# --- Lógica de Resolução do TSP (Problema do Caixeiro Viajante) ---
def solve_tsp(num_nodes, distance_matrix):
    """Resolve o TSP usando o Google OR-Tools Routing Solver."""
    
    # 1. Cria o gerente de índices, com 1 veículo (TSP) e o ponto inicial (depot) na cidade 0.
    manager = pywrapcp.RoutingIndexManager(num_nodes, 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    # 2. Define o callback de distância (custo entre dois nós)
    def distance_callback(from_index, to_index):
        """Retorna a distância entre duas cidades."""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    # Registra o callback e define o custo para todos os arcos
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # 3. Define a política de busca para otimização
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.time_limit.FromSeconds(1)

    # 4. Resolve o problema
    solution = routing.SolveWithParameters(search_parameters)

    # 5. Processa o resultado
    if solution:
        route = []
        total_distance = 0
        index = routing.Start(0)
        
        # Constrói a rota
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route.append(node_index)
            
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            total_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
        
        # Adiciona o nó final (retorno ao depot/início)
        route.append(manager.IndexToNode(index))

        return {
            "alunos": "Seu_Nome",  # <<< ALtere AQUI
            "distancia_total": total_distance,
            "rota": route
        }
    else:
        return None
# ---------------------------------------------------------------------

@app.route('/', methods=['POST'])
def handle_tsp_request():
    """Endpoint HTTP que recebe o JSON do cliente e chama o solver."""
    try:
        data = request.get_json()
        if not data or 'n' not in data or 'distancias' not in data:
            return jsonify({"erro": "Requisição JSON inválida. Faltando 'n' ou 'distancias'."}), 400

        num_nodes = data['n']
        distance_matrix = data['distancias']
        
        # Validação de tamanho (n x n)
        if len(distance_matrix) != num_nodes or any(len(row) != num_nodes for row in distance_matrix):
            return jsonify({"erro": "Matriz de distâncias inválida. O tamanho deve ser n x n."}), 400

        result = solve_tsp(num_nodes, distance_matrix)

        if result:
            return jsonify(result), 200
        else:
            return jsonify({"erro": "Não foi possível encontrar uma solução para o TSP."}), 500

    except Exception as e:
        return jsonify({"erro": f"Erro interno do servidor: {str(e)}"}), 500

if __name__ == '__main__':
    # Roda o servidor Flask para desenvolvimento local (não será usado no Cloud Run)
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)