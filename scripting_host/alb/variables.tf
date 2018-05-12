variable "alb_name" {}
variable "env_type" {}

variable "https_target_group_name" {}
variable "alb_target_group_vpc" {}

variable "priv_alb_subnets" {
  type = "list"
}

variable "priv_security_groups" {}
variable "target_instance_id" {}
variable "domain_name" {}
variable "r53_zone_id" {}
