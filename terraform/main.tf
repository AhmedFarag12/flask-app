# One EC2 server in the account's default VPC that runs the app in Docker.
# Create it with:  terraform -chdir=terraform apply

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project   = var.name
      ManagedBy = "terraform"
    }
  }
}

# Latest Amazon Linux 2023.
data "aws_ssm_parameter" "ami" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

# Only HTTP is open; there is no SSH. Use Session Manager to get a shell.
resource "aws_security_group" "web" {
  name        = var.name
  description = "HTTP to the app"

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Lets you open a shell from the AWS console (Session Manager) instead of SSH.
resource "aws_iam_role" "server" {
  name = "${var.name}-server"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.server.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "server" {
  name = "${var.name}-server"
  role = aws_iam_role.server.name
}

resource "aws_instance" "server" {
  ami                    = data.aws_ssm_parameter.ami.value
  instance_type          = var.instance_type
  vpc_security_group_ids = [aws_security_group.web.id]
  iam_instance_profile   = aws_iam_instance_profile.server.name

  # Installs Docker and starts the app; see user-data.sh.tftpl.
  user_data = templatefile("${path.module}/user-data.sh.tftpl", { image = var.image })

  metadata_options {
    http_tokens = "required"
  }

  tags = {
    Name = var.name
  }

  # A new AMI would otherwise replace the server and lose the database.
  lifecycle {
    ignore_changes = [ami]
  }
}
