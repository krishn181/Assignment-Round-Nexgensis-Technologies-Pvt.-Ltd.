import json
import math


class Location:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance_to(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


class Warehouse:
    def __init__(self, wid, x, y):
        self.id = wid
        self.location = Location(x, y)


class Package:
    def __init__(self, pid, warehouse_id, dest_x, dest_y):
        self.id = pid
        self.warehouse_id = warehouse_id
        self.destination = Location(dest_x, dest_y)
        self.assigned_agent = None


class Agent:
    def __init__(self, aid, x, y):
        self.id = aid
        self.location = Location(x, y)
        self.total_distance = 0
        self.packages_delivered = 0

    def deliver_package(self, warehouse, package):
        dist_to_warehouse = self.location.distance_to(warehouse.location)
        dist_to_destination = warehouse.location.distance_to(package.destination)

        self.total_distance += dist_to_warehouse + dist_to_destination
        self.packages_delivered += 1

        self.location = package.destination


class DeliverySystem:
    def __init__(self, data_file):
        self.warehouses = {}
        self.agents = []
        self.packages = []
        self.load_data(data_file)

    def load_data(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)

        for w in data["warehouses"]:
            self.warehouses[w["id"]] = Warehouse(w["id"], w["x"], w["y"])

        for a in data["agents"]:
            self.agents.append(Agent(a["id"], a["x"], a["y"]))

        for p in data["packages"]:
            self.packages.append(
                Package(p["id"], p["warehouse_id"], p["destination_x"], p["destination_y"])
            )

    def assign_packages(self):
        for package in self.packages:
            warehouse = self.warehouses[package.warehouse_id]
            nearest_agent = min(
                self.agents,
                key=lambda agent: agent.location.distance_to(warehouse.location)
            )
            package.assigned_agent = nearest_agent

    def simulate_deliveries(self):
        for package in self.packages:
            agent = package.assigned_agent
            warehouse = self.warehouses[package.warehouse_id]
            agent.deliver_package(warehouse, package)

    def generate_report(self, output_file):
        report = {"agents": [], "best_agent": None}
        best_efficiency = float("inf")

        for agent in self.agents:
            efficiency = (
                agent.total_distance / agent.packages_delivered
                if agent.packages_delivered else 0
            )

            agent_data = {
                "agent_id": agent.id,
                "packages_delivered": agent.packages_delivered,
                "total_distance": round(agent.total_distance, 2),
                "efficiency": round(efficiency, 2)
            }

            report["agents"].append(agent_data)

            if efficiency < best_efficiency and agent.packages_delivered > 0:
                best_efficiency = efficiency
                report["best_agent"] = agent.id

        with open(output_file, "w") as file:
            json.dump(report, file, indent=4)


def main():
    system = DeliverySystem("data.json")
    system.assign_packages()
    system.simulate_deliveries()
    system.generate_report("report.json")
    print("Delivery simulation completed. Report generated.")


if __name__ == "__main__":
    main()
