output "rds_subnet_1_id" {
  description = "ID of the first shared RDS subnet"
  value       = aws_subnet.rds_subnet_1.id
}

output "rds_subnet_2_id" {
  description = "ID of the second shared RDS subnet"
  value       = aws_subnet.rds_subnet_2.id
}

output "db_subnet_group_name" {
  description = "Name of the shared RDS subnet group"
  value       = aws_db_subnet_group.rds.name
}

output "shared_vpc_id" {
  description = "ID of the shared VPC"
  value       = data.aws_vpc.shared.id
} 