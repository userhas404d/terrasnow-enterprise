output "private_sg_id" {
  value = "${aws_security_group.private.id}"
}

output "allow_user_access_sg_id" {
  value = "${aws_security_group.allow_user_access.id}"
}
