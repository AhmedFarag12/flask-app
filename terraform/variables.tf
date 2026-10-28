variable "region" {
  description = "AWS region for every resource."
  type        = string
  default     = "eu-central-1"
}

variable "name" {
  description = "Name used for the server and its security group."
  type        = string
  default     = "flask-todo"
}

variable "instance_type" {
  description = "EC2 instance type for the server."
  type        = string
  default     = "t3.micro"
}

variable "image" {
  description = "Docker image to run; CI pushes a new :latest on every commit to main."
  type        = string
  default     = "ghcr.io/ahmedfarag12/flask-app:latest"
}
