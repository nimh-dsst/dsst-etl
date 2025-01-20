terraform {
  required_version = ">= 1.0.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# Use data source to reference shared VPC
data "aws_vpc" "shared" {
  id = "vpc-0da7e09c28aed91d4"
}

# Reference existing Internet Gateway
data "aws_internet_gateway" "main" {
  filter {
    name   = "attachment.vpc-id"
    values = [data.aws_vpc.shared.id]
  }
}

# Create shared subnets for RDS
resource "aws_subnet" "rds_subnet_1" {
  vpc_id            = data.aws_vpc.shared.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "us-east-1a"

  tags = {
    Name = "shared-rds-subnet-1"
    Purpose = "Shared RDS subnet across environments"
  }
}

resource "aws_subnet" "rds_subnet_2" {
  vpc_id            = data.aws_vpc.shared.id
  cidr_block        = "10.0.4.0/24"
  availability_zone = "us-east-1b"

  tags = {
    Name = "shared-rds-subnet-2"
    Purpose = "Shared RDS subnet across environments"
  }
}

# Create route table for RDS subnets
resource "aws_route_table" "rds" {
  vpc_id = data.aws_vpc.shared.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = data.aws_internet_gateway.main.id
  }

  tags = {
    Name = "dsst-etl-shared-rds-rt"
    Purpose = "Shared RDS subnets route table"
  }
}

# Associate route table with RDS subnets
resource "aws_route_table_association" "rds_subnet_1" {
  subnet_id      = aws_subnet.rds_subnet_1.id
  route_table_id = aws_route_table.rds.id
}

resource "aws_route_table_association" "rds_subnet_2" {
  subnet_id      = aws_subnet.rds_subnet_2.id
  route_table_id = aws_route_table.rds.id
}

# Create shared DB subnet group
resource "aws_db_subnet_group" "rds" {
  name        = "dsst-etl-shared-rds-subnet-group"
  description = "Shared RDS subnet group for all environments"
  subnet_ids  = [aws_subnet.rds_subnet_1.id, aws_subnet.rds_subnet_2.id]

  tags = {
    Name = "DSST ETL Shared RDS subnet group"
    Purpose = "Shared across environments"
  }
} 