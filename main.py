#!/usr/bin/env python3
# Usage: python main.py action
# Example: python main.py nodes|stacks|services|tasks

import time
import platform
import logging
import os
import sys

import boto3
import docker


docker_client = docker.from_env()
docker_api = docker.APIClient(base_url='unix://var/run/docker.sock')
logging.basicConfig(level=logging.INFO, format="%(asctime)s " + platform.node() + ": %(message)s")


def main(action=""):
    logging.info("========================")

    if action == "nodes":
        logging.info("### Nodes ###")

        nodes = docker_client.nodes.list(filters={'role': 'manager'})
        logging.info("#### Managers: %s" % (len(nodes)))
        logging.info("ID\t\t\t\tHOSTNAME\tIP\tSTATUS\tAVAILABILITY\tMANAGER\tREACHABILITY\tCREATED")
        for node in nodes:
            # logging.info("attrs: " + str(node.attrs))
            logging.info("%s\t%s\t%s\t%s\t%s\t\t%s\t%s\t%s" % (
                node.attrs['ID'],
                node.attrs['Description']['Hostname'],
                node.attrs['Status']['Addr'],
                node.attrs['Status']['State'],
                node.attrs['Spec']['Availability'],
                node.attrs['ManagerStatus']['Leader'],
                node.attrs['ManagerStatus']['Reachability'],
                node.attrs['CreatedAt']
            ))

        nodes = docker_client.nodes.list(filters={'role': 'worker'})
        logging.info("#### Managers: %s" % (len(nodes)))
        logging.info("ID\t\t\t\tHOSTNAME\tIP\tSTATUS\tAVAILABILITY\tCREATED")
        for node in nodes:
            # logging.info("attrs: " + str(node.attrs))
            logging.info("%s\t%s\t%s\t%s\t%s\t\t%s" % (
                node.attrs['ID'],
                node.attrs['Description']['Hostname'],
                node.attrs['Status']['Addr'],
                node.attrs['Status']['State'],
                node.attrs['Spec']['Availability'],
                node.attrs['CreatedAt']
            ))
        return

    if action == "services":
        logging.info("###### Services ######")
        services = docker_client.services.list()
        logging.info("ID\t\t\t\tNAME\t\tMODE\tREPLICAS-TASKS\tIMAGE\tPORTS\tCREATED")
        for service in services:
            # logging.info("Service attrs: " + str(service.attrs))
            mode = ""
            for mod in service.attrs['Spec']['Mode'].keys():
                mode = mod
            replicas = 0
            if mode == "Replicated":
                replicas = service.attrs['Spec']['Mode']['Replicated']['Replicas']
            ports = []
            if "Ports" in service.attrs['Endpoint']:
                for ingress in service.attrs['Endpoint']['Ports']:
                    ports.append(
                        ingress['Protocol'] + "/" + str(ingress['PublishedPort']) + ":" + str(ingress['TargetPort']))

            logging.info("%s\t%s\t\t%s\t%s-%s\t%s\t%s\t%s" % (
                service.attrs['ID'],
                service.name[:7],
                mode[:6],
                replicas,
                len(service.tasks()),
                service.attrs['Spec']['TaskTemplate']['ContainerSpec']['Image'].split("@")[0],
                ",".join(ports),
                service.attrs['CreatedAt']
            ))
        return

    if action == "tasks":
        logging.info("###### Tasks ######")
        services = docker_client.services.list()
        logging.info("ID\t\t\t\tNAME\t\tIMAGE\t\t\tNODE\tDESIRED\tCURRENT\tERROR\tPORTS\tCREATED")
        for service in services:
            for task in service.tasks():
                # logging.info("Tasks attrs: " + str(task))
                node = docker_api.inspect_node(task['NodeID'])
                logging.info("%s\t%s\t\t%s\t\t%s\t%s\t%s\t%s\t%s\t%s" % (
                    task['ID'],
                    "",
                    task['Spec']['ContainerSpec']['Image'].split("@")[0],
                    node['Description']['Hostname'],
                    task['DesiredState'],
                    task['Status']['State'],
                    "",
                    "",
                    task['CreatedAt']
                ))
        return


if __name__ == "__main__":
    main(sys.argv[1])
