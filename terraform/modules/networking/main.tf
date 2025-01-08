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
  region = var.region
}

# Use data source to reference existing VPC
data "aws_vpc" "selected" {
  id = var.environment == "shared" ? "vpc-0da7e09c28aed91d4" : (
    var.environment == "stage" ? "vpc-04e9bc794785725bd" : "vpc-08907c4cf973b8351"
  )
}

# Get existing subnets in the VPC
data "aws_subnets" "existing" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.selected.id]
  }
}

# Get existing security groups
data "aws_security_group" "default" {
  vpc_id = data.aws_vpc.selected.id
  name   = "default"
}
