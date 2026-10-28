output "app_url" {
  description = "Address of the app. The IP changes if the server is stopped and started."
  value       = "http://${aws_instance.server.public_ip}"
}

output "instance_id" {
  description = "Use with: aws ssm start-session --target <id>"
  value       = aws_instance.server.id
}
