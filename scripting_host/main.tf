provider "aws" {
  region = "${var.aws_region}"
}

locals {
  tfe_name        = "${var.alias_name}-${var.env_type}"
}

# create the private sg
module "sg" {
  source = "sg/"

  priv_sg_name          = "${local.tfe_name}-private-sg"
  priv_sg_desc          = "${var.alias_name} ${var.env_type} private sg"
  vpc_id                = "${var.priv_access_vpc_id}"
  sg_allow_inbound_from = "${var.sg_allow_inbound_from}"
}

data "template_file" "init" {
  template = "${file("${path.module}/init.tpl")}"
}

resource "aws_instance" "tfe_instance" {
  ami                    = "${var.ami_id}"
  instance_type          = "${var.instance_type}"
  key_name               = "${var.key_name}"
  vpc_security_group_ids = ["${module.sg.private_sg_id}"]
  subnet_id              = "${var.subnet_id}"
  iam_instance_profile   = "${var.instance_role}"
  user_data              = "${data.template_file.init.rendered}"

  root_block_device {
    volume_type           = "gp2"
    volume_size           = 20
    delete_on_termination = true
  }

  tags {
    Name = "${local.tfe_name}-scripting-host"

    // CLAP_OFF = "0 19 * * 1-7 *"
    // CLAP_ON = ""
  }
}

output "private_ip" {
  description = "List of private IP addresses assigned to the instances"
  value       = ["${aws_instance.tfe_instance.private_ip}"]
}
