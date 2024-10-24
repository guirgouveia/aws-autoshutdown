import os
import boto3
import logging
import argparse

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Load environment variables
CLUSTERS_NAMES = os.getenv('CLUSTERS_NAMES', "your_cluster_1,your_cluster_2").split(",")  # Placeholder for cluster names
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')  # Placeholder for AWS region

# Initialize AWS clients
ecs = boto3.client('ecs', region_name=AWS_REGION)
ec2 = boto3.client('ec2', region_name=AWS_REGION)
rds = boto3.client('rds', region_name=AWS_REGION)
eks = boto3.client('eks', region_name=AWS_REGION)

def shutdown_ecs():
    """Shuts down ECS services in specified clusters."""
    for cluster in CLUSTERS_NAMES:
        try:
            logger.info(f"Checking ECS cluster: {cluster}")
            response = ecs.list_services(cluster=cluster)
            service_arns = response.get('serviceArns', [])

            if not service_arns:
                logger.info(f"No services found for cluster: {cluster}")
                continue

            for service_arn in service_arns:
                service_name = service_arn.split('/')[-1]
                services_response = ecs.describe_services(cluster=cluster, services=[service_name])
                service = services_response['services'][0]
                desired_count = service['desiredCount']

                if desired_count > 0:
                    ecs.update_service(cluster=cluster, service=service_name, desiredCount=0)
                    logger.info(f"Successfully stopped ECS service: {service_name}")
                else:
                    logger.info(f"Service {service_name} is already stopped.")

        except Exception as e:
            logger.error(f"Error stopping services in ECS cluster {cluster}: {str(e)}")
            raise

def turn_on_ecs():
    """Turns on ECS services in specified clusters."""
    for cluster in CLUSTERS_NAMES:
        try:
            logger.info(f"Checking ECS cluster: {cluster}")
            response = ecs.list_services(cluster=cluster)
            service_arns = response.get('serviceArns', [])

            if not service_arns:
                logger.info(f"No services found for cluster: {cluster}")
                continue

            for service_arn in service_arns:
                service_name = service_arn.split('/')[-1]
                service_response = ecs.describe_services(cluster=cluster, services=[service_name])
                service = service_response['services'][0]
                previous_desired_count = service['desiredCount']

                if previous_desired_count == 0:
                    task_definition_arn = service['taskDefinition']
                    task_definition_response = ecs.describe_task_definition(taskDefinition=task_definition_arn)
                    original_desired_count = task_definition_response['taskDefinition']['containerDefinitions'][0]['desiredCount']

                    if original_desired_count is None or original_desired_count <= 0:
                        original_desired_count = 1

                    ecs.update_service(cluster=cluster, service=service_name, desiredCount=original_desired_count)
                    logger.info(f"Successfully restarted ECS service: {service_name} with {original_desired_count} containers.")
                else:
                    logger.info(f"Service {service_name} is already running with {previous_desired_count} containers.")

        except Exception as e:
            logger.error(f"Error starting ECS service in cluster {cluster}: {str(e)}")
            raise

def shutdown_ec2_instances():
    """Shuts down EC2 instances."""
    try:
        logger.info("Shutting down EC2 instances...")
        response = ec2.describe_instances()
        instances = [i for r in response['Reservations'] for i in r['Instances'] if i['State']['Name'] == 'running']

        if not instances:
            logger.info("No running EC2 instances found.")
            return

        for instance in instances:
            instance_id = instance['InstanceId']
            ec2.stop_instances(InstanceIds=[instance_id])
            logger.info(f"Successfully stopped EC2 instance: {instance_id}")

    except Exception as e:
        logger.error(f"Error shutting down EC2 instances: {str(e)}")
        raise

def turn_on_ec2_instances():
    """Starts EC2 instances."""
    try:
        logger.info("Starting EC2 instances...")
        response = ec2.describe_instances()
        instances = [i for r in response['Reservations'] for i in r['Instances'] if i['State']['Name'] == 'stopped']

        if not instances:
            logger.info("No stopped EC2 instances found.")
            return

        for instance in instances:
            instance_id = instance['InstanceId']
            ec2.start_instances(InstanceIds=[instance_id])
            logger.info(f"Successfully started EC2 instance: {instance_id}")

    except Exception as e:
        logger.error(f"Error starting EC2 instances: {str(e)}")
        raise

def shutdown_rds_databases():
    """Shuts down RDS databases."""
    try:
        logger.info("Shutting down RDS databases...")
        response = rds.describe_db_instances()
        db_instances = [db['DBInstanceIdentifier'] for db in response['DBInstances'] if db['DBInstanceStatus'] == 'available']

        if not db_instances:
            logger.info("No available RDS databases found.")
            return

        for db_instance in db_instances:
            rds.stop_db_instance(DBInstanceIdentifier=db_instance)
            logger.info(f"Successfully stopped RDS database: {db_instance}")

    except Exception as e:
        logger.error(f"Error shutting down RDS databases: {str(e)}")
        raise

def turn_on_rds_databases():
    """Starts RDS databases."""
    try:
        logger.info("Starting RDS databases...")
        response = rds.describe_db_instances()
        db_instances = [db['DBInstanceIdentifier'] for db in response['DBInstances'] if db['DBInstanceStatus'] == 'stopped']

        if not db_instances:
            logger.info("No stopped RDS databases found.")
            return

        for db_instance in db_instances:
            rds.start_db_instance(DBInstanceIdentifier=db_instance)
            logger.info(f"Successfully started RDS database: {db_instance}")

    except Exception as e:
        logger.error(f"Error starting RDS databases: {str(e)}")
        raise

def shutdown_eks_clusters():
    """Shuts down EKS clusters (disables)."""
    try:
        logger.info("Shutting down EKS clusters...")
        for cluster in CLUSTERS_NAMES:
            try:
                eks.update_cluster_config(name=cluster, resourcesVpcConfig={'endpointPublicAccess': False})
                logger.info(f"Successfully disabled access for EKS cluster: {cluster}")
            except Exception as e:
                logger.error(f"Error shutting down EKS cluster {cluster}: {str(e)}")
    except Exception as e:
        logger.error(f"Error shutting down EKS clusters: {str(e)}")
        raise

def turn_on_eks_clusters():
    """Enables EKS clusters (enables public access)."""
    try:
        logger.info("Turning on EKS clusters...")
        for cluster in CLUSTERS_NAMES:
            try:
                eks.update_cluster_config(name=cluster, resourcesVpcConfig={'endpointPublicAccess': True})
                logger.info(f"Successfully enabled access for EKS cluster: {cluster}")
            except Exception as e:
                logger.error(f"Error turning on EKS cluster {cluster}: {str(e)}")
    except Exception as e:
        logger.error(f"Error turning on EKS clusters: {str(e)}")
        raise

def shutdown(shutdown_ecs, shutdown_ec2_instances, shutdown_rds_databases, shutdown_eks_clusters):
    shutdown_ecs()
    shutdown_ec2_instances()
    shutdown_rds_databases()
    shutdown_eks_clusters()

def turn_on(turn_on_ecs, turn_on_ec2_instances, turn_on_rds_databases, turn_on_eks_clusters):
    turn_on_ecs()
    turn_on_ec2_instances()
    turn_on_rds_databases()
    turn_on_eks_clusters()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage AWS resources including ECS, EC2, RDS, and EKS.")
    parser.add_argument('--turn-on', action='store_true', help='Turn on all resources')
    parser.add_argument('--shutdown', action='store_true', help='Shutdown all resources')
    args = parser.parse_args()

    if args.shutdown:
        shutdown(shutdown_ecs, shutdown_ec2_instances, shutdown_rds_databases, shutdown_eks_clusters)
    elif args.turn_on:
        turn_on(turn_on_ecs, turn_on_ec2_instances, turn_on_rds_databases, turn_on_eks_clusters)
    else:
        print("Please specify either --turn-on or --shutdown flag.")