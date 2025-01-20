terraform {
  required_version = ">= 1.0.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "dsst-etl-terraform-state-storage-prod"
    key            = "postgres/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "dsst-etl-state-locks-prod"
    encrypt        = true
  }
}

provider "aws" {
  region = "us-east-1"
}

# Reference shared infrastructure
data "aws_db_subnet_group" "shared" {
  name = "dsst-etl-shared-rds-subnet-group"
}

# Get VPC ID from the subnet group
data "aws_vpc" "shared" {
  id = "vpc-0da7e09c28aed91d4"  # shared VPC
}

# Create environment-specific security group for RDS
resource "aws_security_group" "rds" {
  name        = "dsst-etl-rds-sg-prod"
  description = "Security group for DSST ETL RDS instance in prod - Allows PostgreSQL access only"
  vpc_id      = data.aws_vpc.shared.id

  ingress {
    description = "Allow PostgreSQL access from any IP"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow outbound traffic for updates and backups"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow DNS resolution"
    from_port   = 53
    to_port     = 53
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = "dsst-etl-rds-sg-prod"
    Environment = "prod"
    Purpose = "PostgreSQL database access"
    ManagedBy = "terraform"
  }
}

variable "db_password" {
  description = "Password for the RDS instance. Must be at least 8 characters long and contain letters, numbers, and symbols."
  type        = string
  sensitive   = true
}

# Create RDS instance
resource "aws_db_instance" "postgres" {
  allocated_storage    = 20
  engine              = "postgres"
  engine_version      = "15.10"
  instance_class      = "db.t3.micro"
  identifier          = "dsst-etl-postgres-prod"
  db_name             = "dsst_etl"
  username            = "postgres"
  password            = var.db_password
  parameter_group_name = "default.postgres15"
  skip_final_snapshot = true
  publicly_accessible = true
  db_subnet_group_name = data.aws_db_subnet_group.shared.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  # Enhanced security settings
  backup_retention_period = 30
  backup_window = "03:00-04:00"
  maintenance_window = "Mon:04:00-Mon:05:00"
  copy_tags_to_snapshot = true

  tags = {
    Name = "DSST ETL Postgres"
    Environment = "prod"
    ManagedBy = "terraform"
    BackupRetention = "30days"
  }
}

# Output the RDS endpoint
output "rds_endpoint" {
  value = aws_db_instance.postgres.endpoint
}