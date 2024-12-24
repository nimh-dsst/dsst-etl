output "subnet_id" {
  value = module.networking.subnet_ids[0]
}

output "security_group_id" {
  value = module.networking.default_security_group_id
}

output "instance_profile_name" {
  value = module.iam_role_and_policy.instance_profile_name
}
