variable "aws_region" {}
variable "env_type" {}
variable "alias_name" {}

variable "target_r53_zone" {}

variable "priv_access_vpc_id" {}

variable "priv_alb_subnets" {
  type = "list"
}

variable "subnet_id" {}
variable "sg_allow_inbound_from" {}

variable "instance_type" {}
variable "key_name" {}
variable "instance_role" {}
