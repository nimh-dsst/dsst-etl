terraform {
  required_version = ">= 1.0.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "dsst-etl-terraform-state-storage-shared"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "dsst-etl-state-locks-shared"
    encrypt        = true
  }
}

provider "aws" {
  region = "us-east-1"
}

module "shared" {
  source = "../modules/shared"
} 