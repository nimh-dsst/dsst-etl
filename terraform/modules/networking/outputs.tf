output "vpc_id" {
  description = "ID of the VPC"
  value       = data.aws_vpc.selected.id
}

output "subnet_ids" {
  description = "List of subnet IDs"
  value       = data.aws_subnets.existing.ids
}

output "default_security_group_id" {
  description = "ID of the default security group"
  value       = data.aws_security_group.default.id
}
