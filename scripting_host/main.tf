provider "aws" {
  region = "${var.aws_region}"
}

locals {
  instance_name   = "${var.alias_name}-${var.env_type}"
  domain_name     = "${var.alias_name}.${var.target_r53_zone}"
  target_r53_zone = "${var.target_r53_zone}."
}

# create the private sg
module "sg" {
  source                = "sg/"
  pub_sg_name           = "${local.instance_name}-public-sg"
  pub_access_sg         = "${var.pub_access_sg}"
  priv_sg_name          = "${local.instance_name}-private-sg"
  priv_sg_desc          = "${var.alias_name} ${var.env_type} private sg"
  vpc_id                = "${var.priv_access_vpc_id}"
  sg_allow_inbound_from = "${var.sg_allow_inbound_from}"
}

data "template_file" "init" {
  template = "${file("${path.module}/init.tpl")}"
}

data "aws_ami" "centos7" {
  most_recent = true

  filter {
    name   = "name"
    values = ["*spel-minimal-centos-7*"]
  }

  filter {
    name   = "is-public"
    values = ["true"]
  }

  filter {
    name   = "state"
    values = ["available"]
  }

  filter {
    name   = "owner-id"
    values = ["701759196663"]
  }
}

resource "aws_instance" "scripting_host" {
  ami           = "${data.aws_ami.centos7.image_id}"
  instance_type = "${var.instance_type}"
  key_name      = "${var.key_name}"

  vpc_security_group_ids = ["${module.sg.private_sg_id}",
    "${module.sg.allow_user_access_sg_id}",
  ]

  subnet_id            = "${var.subnet_id}"
  iam_instance_profile = "${var.instance_role}"
  user_data            = "${data.template_file.init.rendered}"

  root_block_device {
    volume_type           = "gp2"
    volume_size           = 20
    delete_on_termination = true
  }

  tags {
    Name = "${local.instance_name}-scripting-host"

    // CLAP_OFF = "0 19 * * 1-7 *"
    // CLAP_ON = ""
  }
}

module "dns" {
  source = "dns/"

  alias_name      = "${var.alias_name}"
  target_r53_zone = "${local.target_r53_zone}"
  alb_dns_name    = "${module.alb.dns_name}"
  alb_zone_id     = "${module.alb.zone_id}"
}

module "alb" {
  source                  = "alb/"
  alb_name                = "${local.instance_name}-public-alb"
  env_type                = "${var.env_type}"
  https_target_group_name = "${local.instance_name}-https-target-group"
  alb_target_group_vpc    = "${var.priv_access_vpc_id}"
  priv_security_groups    = "${var.pub_access_sg}"
  priv_alb_subnets        = "${var.priv_alb_subnets}"
  target_instance_id      = "${aws_instance.scripting_host.id}"
  domain_name             = "${local.domain_name}"
  r53_zone_id             = "${module.dns.zone_id}"
}

output "private_ip" {
  description = "List of private IP addresses assigned to the instances"
  value       = ["${aws_instance.scripting_host.private_ip}"]
}
