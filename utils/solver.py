import pandas as pd
import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

def solve_vrp(depot_coords, locations, fleet_df):
    """
    Solves the Capacity Vehicle Routing Problem (CVRP) using OR-Tools.
    
    Parameters:
    depot_coords (tuple): (lat, lon) of the start/end point.
    locations (DataFrame): Customers with 'Latitude', 'Longitude', and 'Demand_Qty'.
    fleet_df (DataFrame): Vehicles with 'Driver_ID', 'Capacity', and 'Cost_per_km'.
    """
    
    # 1. Prepare Data Points
    # Index 0 is always the Depot
    all_points = [depot_coords] + list(zip(locations['Latitude'], locations['Longitude']))
    demands = [0] + [int(d) for d in locations['Demand_Qty']]
    vehicle_capacities = [int(c) for c in fleet_df['Capacity']]
    num_vehicles = len(vehicle_capacities)
    
    # 2. Distance Matrix Calculation
    # We use Euclidean distance * 111 (approx km per degree) for HCMC area
    def compute_distance(p1, p2):
        return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2) * 111.0

    dist_matrix = []
    for i in all_points:
        row = []
        for j in all_points:
            # OR-Tools requires integers, so we multiply by 1000 to keep precision (meters)
            row.append(int(compute_distance(i, j) * 1000))
        dist_matrix.append(row)

    # 3. Create Routing Model
    manager = pywrapcp.RoutingIndexManager(len(dist_matrix), num_vehicles, 0)
    routing = pywrapcp.RoutingModel(manager)

    # Transit Callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return dist_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Demand Callback
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return demands[from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    
    # Add Capacity Constraints
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        vehicle_capacities,  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity'
    )

    # 4. Setting Search Parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.seconds = 5 # Prevent UI from hanging

    # 5. Solving
    solution = routing.SolveWithParameters(search_parameters)

    # 6. Extracting Results for UI
    if solution:
        output_routes = []
        for vehicle_id in range(num_vehicles):
            index = routing.Start(vehicle_id)
            route_path = []
            route_distance = 0
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route_path.append(node_index)
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
            
            # Index 0 is the depot; a route with only [0] is an unused truck
            if len(route_path) > 1:
                # Map node indices back to customer addresses/data
                # Node 0 = Depot, Node 1 = Customer index 0, etc.
                detailed_path = []
                for node in route_path:
                    if node == 0:
                        detailed_path.append("Depot")
                    else:
                        detailed_path.append(locations.iloc[node-1]['Address'])

                output_routes.append({
                    "driver_id": fleet_df.iloc[vehicle_id]['Driver_ID'],
                    "path_indices": route_path,
                    "readable_path": detailed_path,
                    "distance_km": route_distance / 1000.0,
                    "cost": (route_distance / 1000.0) * fleet_df.iloc[vehicle_id]['Cost_per_km']
                })
        return output_routes
    return None