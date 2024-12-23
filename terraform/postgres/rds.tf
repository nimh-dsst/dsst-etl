provider "aws" {
  region = "us-east-1"
}

resource "aws_db_instance" "postgres" {
  allocated_storage    = 20
  engine              = "postgres"
  engine_version      = "13.3"
  instance_class      = "db.t3.micro"
  db_name             = "dsst_etl"
  username            = "postgres"
  password            = "postgres"
  parameter_group_name = "default.postgres13"
  skip_final_snapshot = true
  publicly_accessible = true
}