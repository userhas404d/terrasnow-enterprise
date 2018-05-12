#------------------------------------------------------------------------------
# DNS
#------------------------------------------------------------------------------

data "aws_route53_zone" "selected" {
  name = "${var.target_r53_zone}"
}

resource "aws_route53_record" "www" {
  zone_id = "${data.aws_route53_zone.selected.zone_id}"
  name    = "${var.alias_name}.${var.target_r53_zone}"
  type    = "A"

  alias {
    name                   = "${var.alb_dns_name}"
    zone_id                = "${var.alb_zone_id}"
    evaluate_target_health = false
  }
}

output "zone_id" {
  value = "${data.aws_route53_zone.selected.id}"
}
