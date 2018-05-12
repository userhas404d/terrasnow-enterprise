resource "aws_lb" "internal" {
  name               = "${var.alb_name}"
  internal           = true
  load_balancer_type = "application"
  security_groups    = ["${var.priv_security_groups}"]
  subnets            = "${var.priv_alb_subnets}"

  tags {
    Environment = "${var.env_type}"
  }
}

resource "aws_lb_target_group" "http" {
  name     = "${var.https_target_group_name}"
  port     = 80
  protocol = "HTTP"
  vpc_id   = "${var.alb_target_group_vpc}"
}

resource "aws_lb_target_group_attachment" "http" {
  target_group_arn = "${aws_lb_target_group.http.arn}"
  target_id        = "${var.target_instance_id}"
  port             = 80
}

resource "aws_lb_listener" "frontend_https" {
  load_balancer_arn = "${aws_lb.internal.arn}"
  port              = "443"
  protocol          = "HTTPS"
  certificate_arn   = "${aws_acm_certificate.cert.arn}"
  ssl_policy        = "ELBSecurityPolicy-2015-05"

  default_action {
    target_group_arn = "${aws_lb_target_group.http.arn}"
    type             = "forward"
  }
}

# create the certs

resource "aws_acm_certificate" "cert" {
  domain_name       = "${var.domain_name}"
  validation_method = "DNS"

  tags {
    Environment = "${var.env_type}"
  }
}

# dns validation

resource "aws_route53_record" "cert_validation" {
  name    = "${aws_acm_certificate.cert.domain_validation_options.0.resource_record_name}"
  type    = "${aws_acm_certificate.cert.domain_validation_options.0.resource_record_type}"
  zone_id = "${var.r53_zone_id}"
  records = ["${aws_acm_certificate.cert.domain_validation_options.0.resource_record_value}"]
  ttl     = 60
}

resource "aws_acm_certificate_validation" "cert" {
  certificate_arn         = "${aws_acm_certificate.cert.arn}"
  validation_record_fqdns = ["${aws_route53_record.cert_validation.fqdn}"]
}

resource "aws_lb_listener_certificate" "https_listener" {
  listener_arn    = "${aws_lb_listener.frontend_https.arn}"
  certificate_arn = "${aws_acm_certificate.cert.arn}"
}

output "dns_name" {
  value = "${aws_lb.internal.dns_name}"
}

output "zone_id" {
  value = "${aws_lb.internal.zone_id}"
}
