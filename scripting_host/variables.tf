variable "aws_region" {
  description = "Target aws region"
}

variable "env_type" {
  description = "Suffix added to the instance name (dev, test, prod, etc.)"
}

variable "alias_name" {
  description = "Host alias used in building the instance name and the instance domain name."
}

variable "target_r53_zone" {
  description = "Target route 53 zone in which to build the resulting domain name entry."
}

variable "pub_access_sg" {
  descripiton = "Public access security group."
}

variable "priv_access_vpc_id" {
  description = "ID of the VPC that provides private access."
}

variable "priv_alb_subnets" {
  type        = "list"
  description = "List of subnets that are backed by the private ALB."
}

variable "subnet_id" {
  description = "The id of the security group in which to place the instance."
}

variable "sg_allow_inbound_from" {
  description = "source security group to allow inbound traffic into the instance's private security group."
}

variable "instance_type" {
  description = "AWS instance type (t2.micro, t2.medium, etc.)"
}

variable "key_name" {
  description = "SSH public key used to login to the TerraSnow instance."
}

variable "instance_role" {
  description = "Role to associate with the TerraForm Scripting host instance."
}

variable "private_gitlab_server" {
  description = "hostname of the gitlab server. ex: gitlab.mydomain.net"
}
