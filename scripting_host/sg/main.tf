#------------------------------------------------------------------------------
# security groups
#------------------------------------------------------------------------------

resource "aws_security_group" "private" {
  name        = "${var.priv_sg_name}"
  description = "${var.priv_sg_desc}"
  vpc_id      = "${var.vpc_id}"

  ingress {
    protocol  = -1
    from_port = 0
    to_port   = 0
    self      = true
  }

  ingress {
    protocol        = "tcp"
    from_port       = 22
    to_port         = 22
    security_groups = ["${var.sg_allow_inbound_from}"]
  }

  ingress {
    protocol  = "tcp"
    from_port = 80
    to_port   = 80

    security_groups = [
      "${var.sg_allow_inbound_from}",
    ]
  }

  ingress {
    protocol  = "tcp"
    from_port = 443
    to_port   = 443

    security_groups = [
      "${var.sg_allow_inbound_from}",
    ]
  }

  egress {
    protocol    = -1
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags {
    Name = "${var.priv_sg_name}"
  }
}
